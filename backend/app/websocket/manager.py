import asyncio
import json
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.config import settings
from app.redis_client import get_redis


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []
        self._listener_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)
        if self._listener_task is None or self._listener_task.done():
            self._listener_task = asyncio.create_task(self._redis_listener())

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        payload = json.dumps(message)
        for ws in self.active:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def _redis_listener(self) -> None:
        client = await get_redis()
        if not client:
            return
        pubsub = client.pubsub()
        await pubsub.subscribe(settings.dashboard_channel)
        try:
            async for msg in pubsub.listen():
                if msg["type"] != "message":
                    continue
                data = json.loads(msg["data"])
                await self.broadcast(data)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(settings.dashboard_channel)
            raise

    @property
    def count(self) -> int:
        return len(self.active)


dashboard_ws = ConnectionManager()
