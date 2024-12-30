from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float, UniqueConstraint
from datetime import datetime as dt
import datetime
from sqlalchemy.orm import relationship
from utils.database import Base
from sqlalchemy.dialects.postgresql import JSON, UUID,JSONB
import uuid

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
    instructions = Column(Text, nullable=False)


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

    def user_is_participant(self, user_id):
        """Check if a user is a participant in the chat."""
        return str(user_id) in self.participants