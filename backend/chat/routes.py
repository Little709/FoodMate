# backend/chat/routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends, HTTPException
from sqlalchemy.orm import Session
from utils.schemas import UserRead
from utils.database import SessionLocal
from utils.models import User
from typing import List
from utils.authutils import verify_token
import asyncio

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        verify_token(token)
    except Exception as e:
        print(f"Token verification failed: {e}")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            user_message = f"You: {data}"
            server_response = f"Server: Echoing '{data}'"

            # Send user message and response back to the same WebSocket
            # await websocket.send_text(user_message)
            await websocket.send_text(server_response)

            # Optional: If needed, broadcast only the original message
            # await manager.broadcast(data, room)

            print(f"Received message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")




@router.get("/user/{user_id}/dietary-info", response_model=UserRead)
def get_user_dietary_info(user_id: int, db: Session = Depends(get_db)):
    # Fetch user details from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Return user data as JSON
    return {
        "id": user.id,
        "username": user.username,
        "age": user.age,
        "sex": user.sex,
        "weight": user.weight,
        "height": user.height,
        "activity_level": user.activity_level,
        "goal": user.goal,
        "preferred_cuisines": user.preferred_cuisines,
        "disliked_ingredients": user.disliked_ingredients,
        "liked_ingredients": user.liked_ingredients,
        "allergies": user.allergies,
        "meal_timing": user.meal_timing,
        "portion_size": user.portion_size,
        "snack_preference": user.snack_preference,
        "dietary_preference": user.dietary_preference,
        "personal_story": user.personal_story,
    }