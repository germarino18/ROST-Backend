from fastapi import WebSocket
from typing import Any
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def disconnect(self, websocket: WebSocket):
        for room, connections in self.active_connections.items():
            if websocket in connections:
                connections.remove(websocket)
        empty_rooms = [r for r, c in self.active_connections.items() if not c]
        for r in empty_rooms:
            del self.active_connections[r]

    async def join_room(self, room: str, websocket: WebSocket):
        if room not in self.active_connections:
            self.active_connections[room] = []
        if websocket not in self.active_connections[room]:
            self.active_connections[room].append(websocket)

    async def leave_room(self, room: str, websocket: WebSocket):
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast_to_room(self, room: str, message: dict[str, Any]):
        if room not in self.active_connections:
            return
        payload = json.dumps(message, default=str)
        disconnected = []
        for ws in self.active_connections[room]:
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            await self.disconnect(ws)

    async def broadcast_to_rooms(self, rooms: list[str], message: dict[str, Any]):
        for room in rooms:
            await self.broadcast_to_room(room, message)
