from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Table, Integer, exists, inspect, insert, select
from datetime import datetime as dt
from .database import Base
from uuid import UUID

# Function to create a dynamic table for each chat_id
def create_chat_table(chat_id: str, metadata):
    table_name = f"{chat_id}"  # Dynamic table name for each chat

    # Define the table dynamically
    table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),  # Auto-incrementing index
        Column('user_id', String, nullable=False),  # Sender
        Column('message', Text, nullable=False),  # Message content
        Column('timestamp', DateTime, default=dt.utcnow, nullable=False),  # Timestamp for message
    )

    return table
# Example of how we can create a dynamic model

def create_chat_model(chat_id, metadata):
    """
    Dynamically create a chat table model.
    """
    table_name = f"chat_{chat_id}"  # Use a prefix for chat table names
    return Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),  # Fix here
        Column("user_id", String, nullable=False),
        Column("message", String, nullable=False),
        Column("timestamp", DateTime, default=dt.utcnow, nullable=False),
        extend_existing=True,  # Prevent "already defined" errors
    )

class ChatRoomManager:
    """
    Provides methods for managing chatrooms, such as removing all messages, adding a message,
    retrieving the latest message, etc.
    """

    @staticmethod
    def remove_chat(session, chat_id):
        """Remove the entire table for a specific chat identified by chat_id, if it exists."""
        table_name = f"chat_messages_{chat_id}"

        # Use the inspector to check if the table exists
        inspector = inspect(session.bind)
        if inspector.has_table(table_name):
            # Drop the table
            drop_statement = f"DROP TABLE {table_name}"
            session.execute(drop_statement)
            session.commit()



    @staticmethod
    def add_message(session, chat_id, user_id, message):
        """Add a message to a specific chat identified by chat_id."""
        # Dynamically create the table
        ChatMessageTable = create_chat_model(chat_id, Base.metadata)

        # Insert the message into the table
        stmt = insert(ChatMessageTable).values(
            user_id=user_id,
            message=message,
            timestamp=dt.utcnow()
        )
        session.execute(stmt)
        session.commit()

    @staticmethod
    def get_latest_message(session, chat_id):
        """Retrieve the latest message from a specific chat identified by chat_id."""
        # Dynamically create the model for the specific chat_id
        ChatMessageModel = create_chat_model(chat_id, Base.metadata)

        try:
            return session.query(ChatMessageModel).order_by(ChatMessageModel.timestamp.desc()).first()
        except Exception as e:
            print(f"Error retrieving latest message: {e}")
            return None


    @staticmethod
    def get_all_messages(session, chat_id):
        """
        Retrieve all messages from a specific chat, ordered by timestamp.
        """
        # Dynamically create the model for the specific chat_id
        ChatMessageModel = create_chat_model(chat_id, Base.metadata)

        # Correct usage of select by passing individual columns
        stmt = select(
            ChatMessageModel.c.id,
            ChatMessageModel.c.user_id,
            ChatMessageModel.c.message,
            ChatMessageModel.c.timestamp
        ).order_by(ChatMessageModel.c.timestamp)

        # Execute the query and fetch all results
        return session.execute(stmt).fetchall()

    @staticmethod
    def search_messages(session, chat_id, query):
        """Search for messages in a specific chat containing a specific string."""
        # Dynamically create the model for the specific chat_id
        ChatMessageModel = create_chat_model(chat_id, Base.metadata)

        return session.query(ChatMessageModel).filter(ChatMessageModel.message.ilike(f"%{query}%")).all()

    @staticmethod
    def get_paginated_messages(session, chat_id, page, per_page):
        """Retrieve messages with pagination."""
        offset = (page - 1) * per_page
        # Dynamically create the model for the specific chat_id
        ChatMessageModel = create_chat_model(chat_id, Base.metadata)

        return session.query(ChatMessageModel).limit(per_page).offset(offset).all()