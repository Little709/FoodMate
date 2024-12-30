from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt
from .database import Base
import uuid


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatroom_id = Column(UUID(as_uuid=True),ForeignKey('chatrooms.id'), nullable=False, index=True)  # Refers to the chatroom
    user_id = Column(UUID(as_uuid=True),ForeignKey('users.id'), nullable=False, index=True)      # User who sent the message
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=dt.utcnow, nullable=False)      # When the message was sent

    chatroom = relationship("ChatRoom", back_populates="messages")
    user = relationship("User", back_populates="messages")

class ChatRoomManager:
    """
    Provides methods for managing chatrooms, such as removing all messages, adding a message,
    retrieving the latest message, etc.
    """
    @staticmethod
    def remove_chat(session, chatroom_id):
        """Remove all messages from a chatroom."""
        session.query(ChatMessage).filter(ChatMessage.chatroom_id == chatroom_id).delete()
        session.commit()

    @staticmethod
    def add_message(session, chatroom_id, user_id, message):
        """Add a message to a chatroom."""
        new_message = ChatMessage(chatroom_id=chatroom_id, user_id=user_id, message=message)
        session.add(new_message)
        session.commit()

    @staticmethod
    def get_latest_message(session, chatroom_id):
        """Retrieve the latest message from a chatroom."""
        try:
            return (
                session.query(ChatMessage)
                .filter(ChatMessage.chatroom_id == chatroom_id)
                .order_by(ChatMessage.timestamp.desc())
                .first()
            )
        except Exception as e:
            print(f"Error retrieving latest message: {e}")
            return None

    @staticmethod
    def get_all_messages(session, chatroom_id):
        """Retrieve all messages from a chatroom, ordered by timestamp."""
        return (
            session.query(ChatMessage)
            .filter(ChatMessage.chatroom_id == chatroom_id)
            .order_by(ChatMessage.timestamp)
            .all()
        )

    @staticmethod
    def search_messages(session, chatroom_id, query):
        """Search for messages in a chatroom containing a specific string."""
        return (
            session.query(ChatMessage)
            .filter(ChatMessage.chatroom_id == chatroom_id)
            .filter(ChatMessage.message.ilike(f"%{query}%"))
            .order_by(ChatMessage.timestamp)
            .all()
        )

    @staticmethod
    def get_paginated_messages(session, chatroom_id, page, per_page):
        """Retrieve messages with pagination."""
        offset = (page - 1) * per_page
        return (
            session.query(ChatMessage)
            .filter(ChatMessage.chatroom_id == chatroom_id)
            .order_by(ChatMessage.timestamp)
            .limit(per_page)
            .offset(offset)
            .all()
        )