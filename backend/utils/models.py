from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float, UniqueConstraint,select,inspect, Table, insert
from datetime import datetime as dt
import datetime
from sqlalchemy.orm import relationship, Mapped, Session
from utils.database import Base

from sqlalchemy.dialects.postgresql import JSON, UUID,JSONB, ARRAY
import uuid


# recipe_ingredient_association = Table(
#     "recipe_ingredient_association",
#     Base.metadata,
#     Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
#     Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
#     Column("quantity", String, nullable=False)  # Store the specific quantity for the recipe
# )
#
# instruction_step_association = Table(
#     "instruction_step_association",
#     Base.metadata,
#     Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
#     Column("instruction_id", Integer, ForeignKey("instructions.id"), primary_key=True),
#     Column("step_number", Integer, nullable=False)  # Step number for ordering
# )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    preferred_cuisines = Column(JSON, default=[])
    disliked_ingredients = Column(JSON, default=[])
    liked_ingredients = Column(JSON, default=[])
    allergies = Column(JSON, default=[])

    # New fields
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    activity_level = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    meal_timing = Column(String, default="")
    portion_size = Column(String, default="")
    snack_preference = Column(String, default="")
    dietary_preference = Column(String, default="")
    personal_story = Column(Text, default="")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    prepare_time = Column(Integer, nullable=False)
    ingredients = Column(ARRAY(String), nullable=False)  # Store ingredients as an array of strings
    instructions = Column(ARRAY(String), nullable=False)  # Store instructions as an array of strings
    cuisine = Column(String, nullable=True)
    servings = Column(Integer, nullable=False)
    calories = Column(Float, nullable=False)
    macros = Column(ARRAY(String), nullable=False)
    needed_equipment = Column(ARRAY(String), nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    source = Column(String, nullable=True)
    image_url = Column(String, nullable=True)


# class Ingredient(general_Base):
#     __tablename__ = "ingredients"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, nullable=False)
#     unit = Column(String, nullable=True)  # e.g., "g", "ml", "tbsp"
#
# class InstructionStep(general_Base):
#     __tablename__ = "instructions"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     step_number = Column(Integer, nullable=False)  # Sequence of the step
#     text = Column(String, nullable=False)  # Instruction text


class UserRecipeRating(Base):
    __tablename__ = "user_recipe_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Changed to UUID
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5 star rating
    user = relationship("User", backref="recipe_ratings")
    recipe = relationship("Recipe", backref="user_ratings")



class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=dt.now(datetime.timezone.utc), nullable=False)

class ChatsMetadata(Base):
    __tablename__ = "chats_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String, default='', nullable=False)  # Ensure nullable=False for updates
    participants = Column(JSONB, nullable=False)  # JSON list of user IDs
    creation_date = Column(DateTime, default=dt.utcnow, nullable=False)
    last_activity = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow, nullable=False)
    thread_id = Column(String)

    def user_is_participant(self, user_id):
        """Check if a user is a participant in the chat."""
        return str(user_id) in self.participants

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

    # Add the notification trigger to the chat table
    table_name = f"chat_{chat_id}"
    trigger_sql = f"""
    CREATE TRIGGER new_message_trigger
    AFTER INSERT ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_message();
    """
    metadata.bind.execute(trigger_sql)  # Execute the SQL for the trigger

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


