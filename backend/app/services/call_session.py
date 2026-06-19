import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import CallLog
from app.schemas import NLUResult
from app.services.caller.profile import increment_call_count, preload_caller
from app.services.nlu.cascade import NLUCascade
from app.services.order_processor import save_confirmed_order
from app.services.stt.streaming import detect_language
from app.services.tts.confirmation import build_confirmation_script, synthesize_confirmation
from app.services.stage_events import emit_stage
from app.services.validation.details import build_validation_details
from app.services.validation.order_validator import validate_order


class CallState(str, Enum):
    STARTED = "started"
    LISTENING = "listening"
    PROCESSING = "processing"
    CLARIFYING = "clarifying"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CallSession:
    id: str
    phone: str
    language: str = "en"
    state: CallState = CallState.STARTED
    customer_id: str | None = None
    customer_name: str | None = None
    call_log_id: str | None = None
    transcript: str = ""
    partial_transcript: str = ""
    nlu_result: NLUResult | None = None
    validation_issues: list = field(default_factory=list)
    clarification_count: int = 0
    pending_confirmation: bool = False
    current_stage: str = "call_started"
    stage_history: list = field(default_factory=list)
    validation_details: dict | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CallSessionManager:
    def __init__(self) -> None:
        self.sessions: dict[str, CallSession] = {}
        self.nlu = NLUCascade()

    async def _set_stage(self, session: CallSession, stage: str, extra: dict | None = None) -> None:
        session.current_stage = stage
        session.stage_history.append({"stage": stage, "at": datetime.now(timezone.utc).isoformat()})
        await emit_stage(
            session.id,
            stage,
            customer_name=session.customer_name,
            call_log_id=session.call_log_id,
            extra=extra,
        )

    async def start_session(self, db: AsyncSession, phone: str, language: str = "en") -> CallSession:
        session_id = str(uuid.uuid4())
        profile = await preload_caller(db, phone)

        call_log = CallLog(phone=phone, language=language, status="started")
        if profile:
            call_log.customer_id = profile["id"]
        db.add(call_log)
        await db.commit()
        await db.refresh(call_log)

        session = CallSession(
            id=session_id,
            phone=phone,
            language=profile["language"] if profile else language,
            customer_id=profile["id"] if profile else None,
            customer_name=profile["name"] if profile else None,
            call_log_id=call_log.id,
            state=CallState.LISTENING,
        )
        self.sessions[session_id] = session

        if profile:
            await increment_call_count(db, profile["id"], phone)

        await self._set_stage(session, "call_started", {"state": session.state.value})
        return session

    async def append_transcript(self, db: AsyncSession, session_id: str, text: str, is_final: bool) -> CallSession:
        session = self.sessions[session_id]
        detected = detect_language(text, session.language)
        if detected != "en":
            session.language = detected

        if is_final:
            session.transcript = (session.transcript + " " + text).strip()
            session.partial_transcript = session.transcript
            session.state = CallState.PROCESSING
            await self._set_stage(session, "transcript_received", {"transcript": session.transcript})
        else:
            session.partial_transcript = (session.transcript + " " + text).strip()

        if session.call_log_id:
            log = await db.get(CallLog, session.call_log_id)
            if log:
                log.partial_transcript = session.partial_transcript
                log.transcript = session.transcript
                log.language = session.language
                await db.commit()

        return session

    async def process_order(self, db: AsyncSession, session_id: str) -> dict:
        session = self.sessions[session_id]
        if not session.customer_id:
            session.state = CallState.FAILED
            return {"error": "unknown_caller", "message": "Caller not registered"}

        nlu_result = await self.nlu.parse(db, session.transcript, session.language)
        session.nlu_result = nlu_result
        await self._set_stage(
            session,
            "product_match",
            {"tier": nlu_result.tier_used, "items_matched": len([i for i in nlu_result.items if i.product_id])},
        )

        validation = await validate_order(db, session.customer_id, nlu_result)
        session.validation_issues = [i.model_dump() for i in validation.issues]
        session.validation_details = await build_validation_details(
            db, nlu_result, validation, confirmation_status="pending"
        )
        await self._set_stage(session, "validation", {"valid": validation.valid, "issues_count": len(validation.issues)})

        if session.call_log_id:
            log = await db.get(CallLog, session.call_log_id)
            if log:
                log.nlu_result = nlu_result.model_dump()
                log.validation_errors = session.validation_issues
                await db.commit()

        if not validation.valid:
            if session.clarification_count < settings.max_clarification_attempts:
                session.clarification_count += 1
                session.state = CallState.CLARIFYING
                if session.call_log_id:
                    log = await db.get(CallLog, session.call_log_id)
                    if log:
                        log.clarification_count = session.clarification_count
                        log.status = "clarifying"
                        await db.commit()
                return {
                    "state": session.state,
                    "clarification_needed": True,
                    "issues": session.validation_issues,
                    "validation_details": session.validation_details,
                    "attempt": session.clarification_count,
                    "nlu": nlu_result.model_dump(),
                    "stage": session.current_stage,
                    "stages": session.stage_history,
                }
            session.state = CallState.FAILED
            if session.validation_details:
                session.validation_details["confirmation_status"] = "failed"
            return {
                "state": session.state,
                "error": "validation_failed",
                "issues": session.validation_issues,
                "validation_details": session.validation_details,
                "stage": session.current_stage,
                "stages": session.stage_history,
            }

        session.state = CallState.CONFIRMING
        session.pending_confirmation = True
        if session.validation_details:
            session.validation_details["confirmation_status"] = "pending"

        await self._set_stage(session, "confirmation", {"total_amount": validation.total_amount})

        items_summary = []
        for item in nlu_result.items:
            if item.product_id:
                items_summary.append(
                    {"name": item.product_name, "quantity": item.quantity, "unit": item.unit or "unit"}
                )

        confirm_text = build_confirmation_script(
            session.language,
            session.customer_name or "customer",
            items_summary,
            validation.total_amount,
        )
        audio = await synthesize_confirmation(session.language, confirm_text)

        return {
            "state": session.state,
            "confirmation_text": confirm_text,
            "confirmation_audio_base64": audio.hex() if audio else None,
            "total_amount": validation.total_amount,
            "items": items_summary,
            "nlu_tier": nlu_result.tier_used,
            "validation_details": session.validation_details,
            "stage": session.current_stage,
            "stages": session.stage_history,
        }

    async def confirm_order(self, db: AsyncSession, session_id: str, confirmed: bool) -> dict:
        session = self.sessions[session_id]
        if not confirmed:
            session.state = CallState.FAILED
            return {"state": session.state, "cancelled": True}

        if not session.nlu_result or not session.customer_id:
            return {"error": "no_order"}

        validation = await validate_order(db, session.customer_id, session.nlu_result)
        if not validation.valid:
            return {"error": "validation_failed", "issues": [i.model_dump() for i in validation.issues]}

        order = await save_confirmed_order(
            db,
            session.customer_id,
            session.call_log_id,
            session.nlu_result,
            validation.total_amount,
        )
        session.state = CallState.COMPLETED
        session.pending_confirmation = False
        if session.validation_details:
            session.validation_details["confirmation_status"] = "confirmed"

        await self._set_stage(
            session,
            "order_created",
            {"order_id": order.id, "total_amount": validation.total_amount},
        )

        return {
            "state": session.state,
            "order_id": order.id,
            "total_amount": validation.total_amount,
            "validation_details": session.validation_details,
            "stage": session.current_stage,
            "stages": session.stage_history,
        }

    def get_session(self, session_id: str) -> CallSession | None:
        return self.sessions.get(session_id)

    def list_active_sessions(self) -> list[dict]:
        result = []
        for s in self.sessions.values():
            if s.state in (CallState.COMPLETED, CallState.FAILED):
                continue
            result.append(
                {
                    "session_id": s.id,
                    "customer_name": s.customer_name,
                    "phone": s.phone,
                    "state": s.state.value,
                    "current_stage": s.current_stage,
                    "stages": s.stage_history,
                    "transcript": s.partial_transcript,
                    "validation_details": s.validation_details,
                }
            )
        return result

    @property
    def active_count(self) -> int:
        return sum(1 for s in self.sessions.values() if s.state not in (CallState.COMPLETED, CallState.FAILED))


call_manager = CallSessionManager()
