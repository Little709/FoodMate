# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float
from datetime import datetime as dt
import datetime
from sqlalchemy.orm import relationship
from utils.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Existing preference fields
    preferred_cuisines = Column(Text, default="")
    disliked_ingredients = Column(Text, default="")

    # New user metrics
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    weight = Column(Float, nullable=False)  # in kilograms
    height = Column(Float, nullable=False)  # in centimeters
    activity_level = Column(String, nullable=False)
    goal = Column(String, nullable=False)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    instructions = Column(Text, nullable=False)
    # Possibly store other details like ingredients, etc.


class UserRecipeRating(Base):
    __tablename__ = "user_recipe_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5 star rating, for example

    user = relationship("User", backref="recipe_ratings")
    recipe = relationship("Recipe", backref="user_ratings")


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=dt.now(datetime.timezone.utc), nullable=False)
