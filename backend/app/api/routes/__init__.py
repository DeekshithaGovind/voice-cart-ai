from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy import cast, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.types import Date

from app.database import SessionLocal, get_db
from app.models import CallLog, Customer, Order, OrderItem, Product
from app.schemas import (
    ActiveSessionOut,
    AnalyticsCharts,
    AnalyticsSummary,
    CallLogOut,
    CallSessionStart,
    CustomerOut,
    MonitoringStatus,
    OrderOut,
    ProductOut,
    TranscriptChunk,
)
from app.services.call_session import call_manager
from app.services.learning.nightly import run_nightly_learning
from app.services.stt.faster_whisper import transcribe_audio_bytes
from app.websocket.manager import dashboard_ws

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "voicecart-api"}


@router.post("/calls/start")
async def start_call(payload: CallSessionStart, db: AsyncSession = Depends(get_db)):
    session = await call_manager.start_session(db, payload.phone, payload.language)
    return {
        "session_id": session.id,
        "state": session.state,
        "customer_name": session.customer_name,
        "language": session.language,
        "call_log_id": session.call_log_id,
        "stage": session.current_stage,
        "stages": session.stage_history,
    }


@router.post("/calls/{session_id}/voice")
async def submit_voice(
    session_id: str,
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    db: AsyncSession = Depends(get_db),
):
    session = call_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    audio_bytes = await audio.read()
    stt = await transcribe_audio_bytes(audio_bytes, language if language != "auto" else session.language)
    if stt.get("error") and not stt.get("text"):
        raise HTTPException(422, detail=stt.get("error", "Transcription failed"))

    text = stt.get("text", "").strip()
    if not text:
        raise HTTPException(422, detail="No speech detected in recording")

    await call_manager.append_transcript(db, session_id, text, is_final=True)
    result = await call_manager.process_order(db, session_id)
    return {"partial": session.partial_transcript, "transcript": text, "stt_language": stt.get("language"), **result}


@router.get("/calls/active", response_model=list[ActiveSessionOut])
async def list_active_calls():
    return call_manager.list_active_sessions()


@router.post("/calls/transcript")
async def submit_transcript(payload: TranscriptChunk, db: AsyncSession = Depends(get_db)):
    session = call_manager.get_session(payload.session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    await call_manager.append_transcript(db, payload.session_id, payload.text, payload.is_final)
    if payload.is_final:
        result = await call_manager.process_order(db, payload.session_id)
        return {"partial": session.partial_transcript, **result}
    return {"partial": session.partial_transcript, "state": session.state, "stage": session.current_stage}


@router.post("/calls/{session_id}/confirm")
async def confirm_call(session_id: str, confirmed: bool = True, db: AsyncSession = Depends(get_db)):
    result = await call_manager.confirm_order(db, session_id, confirmed)
    if result.get("order_id"):
        session = call_manager.get_session(session_id)
        await dashboard_ws.broadcast(
            {
                "type": "order_confirmed",
                **result,
                "customer_name": session.customer_name if session else None,
                "validation_details": result.get("validation_details"),
            }
        )
        await dashboard_ws.broadcast({"type": "dashboard_refresh", "reason": "order_confirmed"})
    return result


@router.get("/orders", response_model=list[OrderOut])
async def list_orders(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.customer))
        .order_by(desc(Order.created_at))
        .limit(limit)
    )
    orders = result.scalars().all()
    out = []
    for o in orders:
        item = OrderOut.model_validate(o)
        item.customer_name = o.customer.name if o.customer else None
        item.customer_phone = o.customer.phone if o.customer else None
        out.append(item)
    return out


@router.get("/calls", response_model=list[CallLogOut])
async def list_calls(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CallLog).options(selectinload(CallLog.customer)).order_by(desc(CallLog.started_at)).limit(limit)
    )
    logs = result.scalars().all()
    out = []
    for log in logs:
        item = CallLogOut.model_validate(log)
        item.customer_name = log.customer.name if log.customer else None
        out.append(item)
    return out


@router.get("/customers", response_model=list[CustomerOut])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.name))
    return result.scalars().all()


@router.get("/products", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.active.is_(True)).order_by(Product.name))
    return result.scalars().all()


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def analytics_summary(db: AsyncSession = Depends(get_db)):
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0
    total_revenue = (await db.execute(select(func.coalesce(func.sum(Order.total_amount), 0)))).scalar() or 0
    total_calls = (await db.execute(select(func.count(CallLog.id)))).scalar() or 0
    avg_order = float(total_revenue) / total_orders if total_orders else 0

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    orders_today = (
        await db.execute(select(func.count(Order.id)).where(Order.created_at >= today))
    ).scalar() or 0
    calls_today = (
        await db.execute(select(func.count(CallLog.id)).where(CallLog.started_at >= today))
    ).scalar() or 0

    tier_counts = {1: 0, 2: 0, 3: 0}
    tier_result = await db.execute(select(Order.nlu_tier_used, func.count(Order.id)).group_by(Order.nlu_tier_used))
    for tier, count in tier_result.all():
        if tier in tier_counts:
            tier_counts[tier] = count

    total_tier = sum(tier_counts.values()) or 1
    return AnalyticsSummary(
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_calls=total_calls,
        avg_order_value=avg_order,
        tier1_rate=tier_counts[1] / total_tier,
        tier2_rate=tier_counts[2] / total_tier,
        tier3_rate=tier_counts[3] / total_tier,
        orders_today=orders_today,
        calls_today=calls_today,
        active_calls=call_manager.active_count,
    )


@router.get("/analytics/charts", response_model=AnalyticsCharts)
async def analytics_charts(db: AsyncSession = Depends(get_db)):
    top_result = await db.execute(
        select(OrderItem.product_name, func.sum(OrderItem.quantity).label("qty"), func.sum(OrderItem.line_total).label("revenue"))
        .group_by(OrderItem.product_name)
        .order_by(desc("qty"))
        .limit(8)
    )
    top_products = [
        {"name": row.product_name, "quantity": float(row.qty), "revenue": float(row.revenue)}
        for row in top_result.all()
    ]

    since = datetime.now(timezone.utc) - timedelta(days=6)
    day_col = cast(Order.created_at, Date).label("day")
    revenue_result = await db.execute(
        select(day_col, func.coalesce(func.sum(Order.total_amount), 0).label("revenue"))
        .where(Order.created_at >= since)
        .group_by(day_col)
        .order_by(day_col)
    )
    revenue_trend = [{"day": str(row.day), "revenue": float(row.revenue)} for row in revenue_result.all()]

    orders_result = await db.execute(
        select(day_col, func.count(Order.id).label("orders"))
        .where(Order.created_at >= since)
        .group_by(day_col)
        .order_by(day_col)
    )
    orders_by_day = [{"day": str(row.day), "orders": int(row.orders)} for row in orders_result.all()]

    tier_result = await db.execute(
        select(Order.nlu_tier_used, func.count(Order.id)).group_by(Order.nlu_tier_used)
    )
    tier_labels = {1: "Tier 1 · Fuzzy", 2: "Tier 2 · NER", 3: "Tier 3 · LLM", None: "Unknown"}
    nlu_tier_usage = [
        {"tier": tier_labels.get(tier, f"Tier {tier}"), "count": count}
        for tier, count in tier_result.all()
    ]

    return AnalyticsCharts(
        top_products=top_products,
        revenue_trend=revenue_trend,
        orders_by_day=orders_by_day,
        nlu_tier_usage=nlu_tier_usage,
    )


@router.get("/monitoring/status", response_model=MonitoringStatus)
async def monitoring_status(db: AsyncSession = Depends(get_db)):
    from app.redis_client import get_redis

    db_ok = "ok"
    try:
        await db.execute(select(1))
    except Exception:
        db_ok = "error"

    redis_client = await get_redis()
    redis_ok = "ok" if redis_client else "degraded"

    last_order = (await db.execute(select(Order.created_at).order_by(desc(Order.created_at)).limit(1))).scalar_one_or_none()
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0
    total_customers = (await db.execute(select(func.count(Customer.id)))).scalar() or 0

    return MonitoringStatus(
        api="ok",
        backend="ok",
        database=db_ok,
        redis=redis_ok,
        websocket_connections=dashboard_ws.count,
        active_sessions=call_manager.active_count,
        active_calls=call_manager.active_count,
        total_orders=total_orders,
        total_customers=total_customers,
        last_order_at=last_order,
        uptime_hint="VoiceCart AI running",
    )


@router.post("/jobs/nightly-learning")
async def trigger_nightly_learning(db: AsyncSession = Depends(get_db)):
    result = await run_nightly_learning(db)
    return result


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await dashboard_ws.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_ws.disconnect(websocket)


@router.websocket("/ws/calls/{session_id}")
async def call_websocket(websocket: WebSocket, session_id: str):
    session = call_manager.get_session(session_id)
    if not session:
        await websocket.close(code=4004)
        return
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "")
            is_final = data.get("is_final", False)
            async with SessionLocal() as db:
                await call_manager.append_transcript(db, session_id, text, is_final)
                await websocket.send_json({"partial": session.partial_transcript, "state": session.state})
                if is_final:
                    result = await call_manager.process_order(db, session_id)
                    await websocket.send_json(result)
    except WebSocketDisconnect:
        pass
