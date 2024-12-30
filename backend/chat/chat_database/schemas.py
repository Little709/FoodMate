from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessageBase(BaseModel):
    user_id: str = Field(..., description="The unique identifier for the user sending the message.")
    message: str = Field(..., description="The message content.")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageRead(ChatMessageBase):
    id: int  # Auto-incrementing ID for sorting
    timestamp: datetime
    type: Optional[str] = None  # Optional field with a default value of None

    class Config:
        from_attributes = True

class ChatRoomActions(BaseModel):
    chatroom_id: str = Field(..., description="The unique identifier for the chatroom.")

    class Config:
        json_schema_extra = {
            "example": {
                "chatroom_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

class ChatRoomMessageList(BaseModel):
    chatroom_id: str = Field(..., description="The unique identifier for the chatroom.")
    messages: List[ChatMessageRead] = Field(..., description="A list of messages in the chatroom.")
