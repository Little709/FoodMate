# backend/chat/routes.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from utils.schemas import UserRead, CreateChatSchema, ChatSummary
from utils.database import SessionLocal as GeneralSession
from utils.models import User, ChatsMetadata
from .chat_database.database import SessionLocal as ChatSession
from .chat_database.models import ChatMessage
from .chat_database.schemas import ChatMessageCreate, ChatMessageRead
from typing import List
from utils.authutils import verify_token
import uuid
import json
from datetime import datetime as dt

router = APIRouter()


def generate_room_id():
    return uuid.uuid4().hex


# General database connection
def get_general_db():
    db = GeneralSession()
    try:
        yield db
    finally:
        db.close()


# Chat database connection
def get_chat_db():
    db = ChatSession()
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
async def chat_endpoint(websocket: WebSocket, room: str, chat_db: Session = Depends(get_chat_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        user_id = verify_token(token)  # Extract user ID from token
    except Exception as e:
        print(f"Token verification failed: {e}")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()

            # Save message to the chat database
            new_message = ChatMessage(
                chatroom_id=room,
                user_id=user_id,
                message=data,
                timestamp=dt.utcnow()
            )
            try:
                chat_db.add(new_message)
                chat_db.commit()
            except Exception as e:
                chat_db.rollback()
                print(f"Error saving message: {e}")
                await websocket.send_text(json.dumps({"error": "Message could not be saved"}))
                continue

            # Broadcast the message
            broadcast_message = {
                "id": str(new_message.id),
                "chatroom_id": room,
                "user_id": str(user_id),  # Ensure UUIDs are converted to strings
                "message": data,
                "timestamp": new_message.timestamp.isoformat()
            }
            await manager.broadcast(message=json.dumps(broadcast_message), room=room)


    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")


@router.get("/user/{user_id}/dietary-info", response_model=UserRead)
def get_user_dietary_info(user_id: int, db: Session = Depends(get_general_db)):
    # Fetch user details from the general database
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


@router.post("/chats/new", response_model=CreateChatSchema)
def create_chat(chat: CreateChatSchema, db: Session = Depends(get_general_db)):
    try:
        new_chat = ChatsMetadata(
            participants=chat.participants,
            creation_date=dt.utcnow(),
            last_activity=dt.utcnow()
        )
        db.add(new_chat)
        db.commit()
        return CreateChatSchema(participants=new_chat.participants)
    except Exception as e:
        print(f"Error creating chat: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the chat")

@router.get("/user/{user_id}/chats", response_model=List[ChatSummary])
def get_user_chats(user_id: UUID, db: Session = Depends(get_general_db)):
    try:
        chats = (
            db.query(ChatsMetadata)
            .filter(ChatsMetadata.participants.contains([str(user_id)]))
            .order_by(ChatsMetadata.last_activity.desc())
            .all()
        )
        # Use Pydantic's from_orm to ensure compatibility
        return [ChatSummary.from_orm(chat) for chat in chats]
    except Exception as e:
        print(f"Error fetching user chats: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching user chats")
