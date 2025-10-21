import asyncio
import logging
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()
        self._heartbeat_task: asyncio.Task | None = None
        self._started = False

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("🔌 WebSocket connected. Active: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("🔌 WebSocket disconnected. Active: %d", len(self.active_connections))

    async def broadcast_json(self, message: dict) -> None:
        to_drop = []
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception:
                to_drop.append(ws)
        for ws in to_drop:
            self.disconnect(ws)

    async def _heartbeat_loop(self) -> None:
        # lightweight keepalive + observability
        while True:
            try:
                await asyncio.sleep(30)
                await self.broadcast_json({"type": "heartbeat", "active": len(self.active_connections)})
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning("WS heartbeat error: %s", e, exc_info=True)

    async def start(self) -> None:
        if self._started:
            return
        logger.info("✅ WebSocketManager starting…")
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(), name="ws-heartbeat")
        self._started = True

    async def shutdown(self) -> None:
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        self._started = False
        logger.info("🛑 WebSocketManager stopped")

_ws_manager: WebSocketManager | None = None

def get_websocket_manager() -> WebSocketManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
