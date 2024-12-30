from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ChatMessageBase(BaseModel):
    chatroom_id: UUID = Field(..., description="The unique identifier for the chatroom.")
    user_id: UUID = Field(..., description="The unique identifier for the user sending the message.")
    message: str = Field(..., description="The message content.")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageRead(ChatMessageBase):
    id: UUID
    timestamp: datetime
    message: str  # Explicit inclusion (optional)

    class Config:
        from_attributes = True

class ChatRoomActions(BaseModel):
    chatroom_id: UUID = Field(..., description="The unique identifier for the chatroom.")

    class Config:
        json_schema_extra = {
            "example": {
                "chatroom_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

class ChatRoomMessageList(BaseModel):
    chatroom_id: UUID = Field(..., description="The unique identifier for the chatroom.")
    messages: List[ChatMessageRead] = Field(..., description="A list of messages in the chatroom.")
