# backend/chat/routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections[room].remove(websocket)
        if not self.active_connections[room]:
            del self.active_connections[room]

    async def broadcast(self, message: str, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{room}")
async def chat_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast the incoming message to all members of the room
            await manager.broadcast(data, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
