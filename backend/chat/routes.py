# backend/chat/routes.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import inspect, select
from starlette.config import undefined
from utils.schemas import UserRead, CreateChatSchema, ChatSummary,ChatResponseSchema, UpdateChatMetadata
from utils.database import SessionLocal as GeneralSession
from utils.models import User, ChatsMetadata
from .chat_database.database import SessionLocal as ChatSession
from .chat_database.models import ChatRoomManager, create_chat_model
from .chat_database.schemas import ChatMessageRead
from typing import List
from .chat_database.database import Base
from utils.authutils import verify_token, get_current_user
import uuid
from jose import jwt
from uuid import UUID
import json
from datetime import datetime as dt
import logging

router = APIRouter()

# Set up logging
logger = logging.getLogger("chat")


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
        # Use self.active_connections instead of self.rooms
        for connection in self.active_connections.get(room, []):
            await connection.send_text(message)

    async def broadcast_to_others(self, sender: WebSocket, message: str, room: str):
        """
        Broadcast a message to all clients in a room except the sender.
        """
        for connection in self.active_connections.get(room, []):
            if connection != sender:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")
                    await self.disconnect(connection, room)


manager = ConnectionManager()

@router.websocket("/room")
async def chat_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    room = websocket.query_params.get("chatid")

    try:
        chat_db = next(get_chat_db())

    except Exception as e:
        await websocket.close(code=1008)
        logger.error(f"Failed to initialize chat database: {e}")
        return

    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = verify_token(token)
    except Exception as e:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()

            # print("1")
            # Add the message to the database
            if(data):
                timestamp = dt.utcnow().isoformat()
                ChatRoomManager.add_message(chat_db, room, user.username, data)
                broadcast_message = {
                    "timestamp": timestamp,
                    "sender": user.username,
                    "content": data,
                    "type": "received",
                }
                await manager.broadcast_to_others(
                    websocket, json.dumps(broadcast_message), room=room
                )

                # print(data)
                # ChatRoomManager.add_message(chat_db, room, "server", data)
                # await manager.broadcast(json.dumps(broadcast_message),room=room)


    except WebSocketDisconnect:
        chat_db.close()
        manager.disconnect(websocket, room)
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")

@router.post("/new", response_model=ChatResponseSchema)
def create_chat(
    data: dict,
    db: Session = Depends(get_general_db),
    chat_db: Session = Depends(get_chat_db),
    current_user=Depends(get_current_user),
    display_name: str = None,

):
    print(data)
    """
    Create a new chat with the authenticated user as the sole participant.
    """
    try:
        if(display_name == None or display_name == "undefined"):
            display_name = f"Chat_{dt.utcnow()}"
        # Use only the current user ID as the participant
        new_chat = ChatsMetadata(
            participants=[str(current_user.id)],  # List containing only the current user ID
            display_name=display_name
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)  # Refresh to get the auto-generated ID

        chat_table_name = str(new_chat.id)  # Use the chat ID as the table name
        inspector = inspect(chat_db.bind)
        if not inspector.has_table(chat_table_name):
            # Dynamically create the table
            ChatMessageTable = create_chat_model(chat_table_name, Base.metadata)
            Base.metadata.create_all(bind=chat_db.bind, tables=[ChatMessageTable])
        print("response to be sent",new_chat)
        return new_chat

    except Exception as e:
        print(f"Error creating chat: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the chat")


@router.get("/chats", response_model=List[ChatSummary])
def get_user_chats(
    db: Session = Depends(get_general_db),
    chat_db: Session = Depends(get_chat_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all chats for the user authenticated by the token
    and ensure all chat tables exist in the chat database.
    """
    try:

        # Fetch all chats the user participates in
        chats = (
            db.query(ChatsMetadata)
            .filter(ChatsMetadata.participants.cast(JSONB).op("@>")([str(current_user.id)]))
            .order_by(ChatsMetadata.last_activity.desc())
            .all()
        )
        for chat in chats:
            print(chat.display_name,chat.last_activity)
        if not chats:
            return []

        # Check and create missing tables in chat_db
        inspector = inspect(chat_db.bind)
        for chat in chats:
            chat_table_name = str(chat.id)  # Convert UUID to string
            if not inspector.has_table(chat_table_name):
                # Dynamically create the table and add it to the database
                ChatMessageTable = create_chat_model(chat_table_name, Base.metadata)
                Base.metadata.create_all(bind=chat_db.bind, tables=[ChatMessageTable])

        # Convert chats to Pydantic schemas
        return [ChatSummary.from_orm(chat) for chat in chats]

    except Exception as e:
        logger.error(f"Error fetching user chats: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching user chats")




@router.delete("/delete/{chat_id}", response_model=ChatResponseSchema)
def delete_chat(
        chat_id: UUID,
        db: Session = Depends(get_general_db),
        current_user: User = Depends(get_current_user)
):
    """
    Delete a chat and all associated messages.
    """
    try:
        # Fetch the chat metadata by chat_id
        chat = db.query(ChatsMetadata).filter(ChatsMetadata.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Check if the current user is a participant in the chat
        if str(current_user.id) not in [str(participant) for participant in chat.participants]:
            raise HTTPException(status_code=403, detail="User is not authorized to delete this chat")
        # print('hi')
        # Remove all chat messages
        ChatRoomManager.remove_chat(db, chat_id)
        # print("this works")
        # Remove the chatroom metadata entry
        db.delete(chat)
        db.commit()

        return chat  # Return the deleted chat metadata as a confirmation response

    except Exception as e:
        print(f"Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the chat")

@router.get("/{chat_id}/messages", response_model=List[ChatMessageRead])
def get_chat_messages(
    chat_id: str,
    chat_db: Session = Depends(get_chat_db),
    current_user: User = Depends(get_current_user)
):
    print(current_user.username)
    """
    Retrieve all messages of a specific chat using ChatRoomManager.
    """
    try:
        # Fetch all messages using the ChatRoomManager
        raw_messages = ChatRoomManager.get_all_messages(chat_db, chat_id)
        # for message in raw_messages:
            # print("sent" if message.user_id == current_user.username else "received")
        # Convert raw results to Pydantic schemas
        return [
            ChatMessageRead(
                id=message.id,
                user_id=message.user_id,
                message=message.message,
                timestamp=message.timestamp,
                type="sent" if message.user_id == current_user.username else "received",
            )
            for message in raw_messages
        ]

    except Exception as e:
        logger.error(f"Error fetching messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching messages")


@router.get("/{chat_id}/sync-messages", response_model=List[ChatMessageRead])
def sync_messages(
    chat_id: str,
    since: str,
    chat_db: Session = Depends(get_chat_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch messages for a chat since the given timestamp using ChatRoomManager.
    """
    try:
        # Validate chat table existence
        inspector = inspect(chat_db.bind)
        table_name = f"chat_{chat_id}"
        if not inspector.has_table(table_name):
            raise HTTPException(status_code=404, detail="Chat not found")

        # Parse 'since' timestamp
        try:
            since_timestamp = dt.fromisoformat(since)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")

        # Fetch messages since the given timestamp
        ChatMessageModel = create_chat_model(chat_id, Base.metadata)
        stmt = (
            select(
                ChatMessageModel.c.id,
                ChatMessageModel.c.user_id,
                ChatMessageModel.c.message,
                ChatMessageModel.c.timestamp
            )
            .where(ChatMessageModel.c.timestamp > since_timestamp)
            .order_by(ChatMessageModel.c.timestamp)
        )
        raw_messages = chat_db.execute(stmt).fetchall()

        # Convert raw results to Pydantic schemas
        return [
            ChatMessageRead(
                id=message.id,
                user_id=message.user_id,
                message=message.message,
                timestamp=message.timestamp,
            )
            for message in raw_messages
        ]

    except Exception as e:
        logger.error(f"Error syncing messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while syncing messages")

@router.put("/{chat_id}/metadata")
def update_chat_metadata(
    chat_id: UUID,
    metadata: UpdateChatMetadata,
    db: Session = Depends(get_general_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update chat metadata like display_name and participants.
    """
    try:
        # Fetch the chat
        chat = db.query(ChatsMetadata).filter(ChatsMetadata.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Update the metadata fields
        if metadata.display_name is not None:
            chat.display_name = metadata.display_name

        if metadata.participants is not None:
            chat.participants = metadata.participants

        # Update the last_activity timestamp
        chat.last_activity = dt.utcnow()

        # Commit the changes
        db.commit()

        return {"detail": "Chat metadata updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
