import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer
from app.redis_client import cache_get, cache_set


CALLER_CACHE_TTL = 3600


def caller_cache_key(phone: str) -> str:
    return f"caller:{phone}"


async def preload_caller(db: AsyncSession, phone: str) -> dict[str, Any] | None:
    cached = await cache_get(caller_cache_key(phone))
    if cached:
        return json.loads(cached)

    result = await db.execute(select(Customer).where(Customer.phone == phone))
    customer = result.scalar_one_or_none()
    if not customer:
        return None

    profile = {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "language": customer.language,
        "credit_limit": customer.credit_limit,
        "credit_used": customer.credit_used,
        "preferred_products": customer.preferred_products or [],
        "aliases": customer.aliases or {},
        "call_count": customer.call_count,
    }
    await cache_set(caller_cache_key(phone), json.dumps(profile), ex=CALLER_CACHE_TTL)
    return profile


async def invalidate_caller_cache(phone: str) -> None:
    from app.redis_client import cache_delete

    await cache_delete(caller_cache_key(phone))


async def increment_call_count(db: AsyncSession, customer_id: str, phone: str) -> None:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if customer:
        customer.call_count += 1
        await db.commit()
        await invalidate_caller_cache(phone)
