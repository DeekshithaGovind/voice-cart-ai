from typing import Any

from app.websocket.manager import dashboard_ws

STAGES = [
    "call_started",
    "transcript_received",
    "product_match",
    "validation",
    "confirmation",
    "order_created",
]

STAGE_LABELS = {
    "call_started": "Call Started",
    "transcript_received": "Transcript Received",
    "product_match": "Product Match",
    "validation": "Validation",
    "confirmation": "Confirmation",
    "order_created": "Order Created",
}


async def emit_stage(
    session_id: str,
    stage: str,
    *,
    customer_name: str | None = None,
    call_log_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "type": "stage_update",
        "session_id": session_id,
        "stage": stage,
        "stage_label": STAGE_LABELS.get(stage, stage),
        "customer_name": customer_name,
        "call_log_id": call_log_id,
    }
    if extra:
        payload.update(extra)
    await dashboard_ws.broadcast(payload)
