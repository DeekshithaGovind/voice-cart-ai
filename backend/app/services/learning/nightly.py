import asyncio
import json
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import CallLog, Customer, Order, OrderItem, Product, ProductAlias
from app.redis_client import get_redis


async def run_nightly_learning(db: AsyncSession) -> dict:
    """Learn aliases from successful calls where tier 1 matched with high confidence."""
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(Order, OrderItem, CallLog)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .outerjoin(CallLog, CallLog.id == Order.call_log_id)
        .where(Order.created_at >= since)
        .where(OrderItem.nlu_tier == 1)
        .where(OrderItem.match_confidence >= 0.85)
    )
    rows = result.all()
    learned = 0

    for order, item, call_log in rows:
        if not call_log or not call_log.transcript:
            continue
        segments = [s.strip().lower() for s in call_log.transcript.split(",") if s.strip()]
        for seg in segments:
            if item.product_name.lower() in seg:
                continue
            existing = await db.execute(
                select(ProductAlias).where(
                    ProductAlias.product_id == item.product_id,
                    ProductAlias.alias == seg,
                )
            )
            if existing.scalar_one_or_none():
                continue
            db.add(
                ProductAlias(
                    product_id=item.product_id,
                    alias=seg,
                    language=order.language,
                    source="nightly_learning",
                    confidence=item.match_confidence,
                )
            )
            product = await db.get(Product, item.product_id)
            if product:
                aliases = list(product.aliases or [])
                if seg not in aliases:
                    aliases.append(seg)
                    product.aliases = aliases
            learned += 1

    await db.commit()
    return {"learned_aliases": learned, "processed_orders": len(rows)}
