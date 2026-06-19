import json
from typing import Any

import redis.asyncio as redis

from app.config import settings

_redis: redis.Redis | None = None
_memory_store: dict[str, Any] = {}
_memory_streams: dict[str, list] = {"voicecart:orders": []}


async def get_redis() -> redis.Redis | None:
    global _redis
    if _redis is None:
        try:
            client = redis.from_url(settings.redis_url, decode_responses=True)
            await client.ping()
            _redis = client
        except Exception:
            _redis = None
    return _redis


async def cache_get(key: str) -> str | None:
    client = await get_redis()
    if client:
        return await client.get(key)
    return _memory_store.get(key)


async def cache_set(key: str, value: str, ex: int | None = None) -> None:
    client = await get_redis()
    if client:
        await client.set(key, value, ex=ex)
    else:
        _memory_store[key] = value


async def cache_delete(key: str) -> None:
    client = await get_redis()
    if client:
        await client.delete(key)
    else:
        _memory_store.pop(key, None)


async def publish(channel: str, message: dict[str, Any]) -> None:
    payload = json.dumps(message)
    client = await get_redis()
    if client:
        await client.publish(channel, payload)
    else:
        _memory_store.setdefault(f"pub:{channel}", []).append(payload)


async def stream_add(stream: str, data: dict[str, str]) -> str:
    client = await get_redis()
    if client:
        return await client.xadd(stream, data)
    _memory_streams.setdefault(stream, []).append(data)
    return str(len(_memory_streams[stream]))


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
