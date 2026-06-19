import asyncio
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import CallLog, Customer, Order, OrderItem, Product
from app.redis_client import publish, stream_add
from app.schemas import NLUResult, OrderCreate, OrderItemCreate
from app.services.caller.profile import invalidate_caller_cache


async def _notify_webhook(url: str, payload: dict) -> None:
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload)
    except Exception:
        pass


async def save_confirmed_order(
    db: AsyncSession,
    customer_id: str,
    call_log_id: str | None,
    nlu_result: NLUResult,
    total_amount: float,
) -> Order:
    order = Order(
        customer_id=customer_id,
        call_log_id=call_log_id,
        status="confirmed",
        language=nlu_result.language,
        total_amount=total_amount,
        transcript=nlu_result.raw_transcript,
        nlu_tier_used=nlu_result.tier_used,
        metadata_={"unmatched": nlu_result.unmatched},
    )
    db.add(order)
    await db.flush()

    for item in nlu_result.items:
        if not item.product_id:
            continue
        product = (
            await db.execute(select(Product).where(Product.id == item.product_id))
        ).scalar_one()
        line_total = item.quantity * product.price
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                unit_price=product.price,
                line_total=line_total,
                match_confidence=item.confidence,
                nlu_tier=item.nlu_tier,
            )
        )
        product.stock = max(0, product.stock - item.quantity)

    customer = (await db.execute(select(Customer).where(Customer.id == customer_id))).scalar_one()
    customer.credit_used += total_amount

    if call_log_id:
        call_log = (await db.execute(select(CallLog).where(CallLog.id == call_log_id))).scalar_one_or_none()
        if call_log:
            call_log.status = "completed"
            call_log.ended_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(order)
    await invalidate_caller_cache(customer.phone)

    stream_payload = {
        "order_id": order.id,
        "customer_id": customer_id,
        "total": str(total_amount),
        "status": "confirmed",
        "tier": str(nlu_result.tier_used),
    }
    await stream_add(settings.order_stream_key, stream_payload)

    dashboard_event = {
        "type": "order_confirmed",
        "order_id": order.id,
        "customer_name": customer.name,
        "customer_phone": customer.phone,
        "total_amount": total_amount,
        "items_count": len(nlu_result.items),
        "nlu_tier": nlu_result.tier_used,
        "created_at": order.created_at.isoformat(),
    }
    await publish(settings.dashboard_channel, dashboard_event)

    asyncio.create_task(_notify_webhook(settings.webhook_url, dashboard_event))
    asyncio.create_task(_notify_webhook(settings.erp_webhook_url, {"order_id": order.id, **dashboard_event}))

    return order
