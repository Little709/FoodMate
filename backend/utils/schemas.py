from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
# from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID
import uuid
from datetime import datetime
# Enums
class SexEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class ActivityLevelEnum(str, Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extra_active = "extra_active"

class GoalEnum(str, Enum):
    lose_weight = "lose_weight"
    maintain_weight = "maintain_weight"
    gain_weight = "gain_weight"

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    age: int = Field(..., gt=0)
    sex: SexEnum
    weight: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    activity_level: ActivityLevelEnum
    goal: GoalEnum
    #TODO: below = "| None = None" but it should really be "Field(default_factory=list)". can't really figure out why that doesn't work.
    preferred_cuisines: Optional[List[str]] | None = None
    disliked_ingredients: Optional[List[str]] | None = None
    liked_ingredients: Optional[List[str]] | None = None
    allergies: Optional[List[str]] | None = None
    meal_timing: Optional[str] = ""
    portion_size: Optional[str] = ""
    snack_preference: Optional[str] = ""
    dietary_preference: Optional[str] = ""
    personal_story: Optional[str] = ""

class UserRead(UserBase):
    id: UUID
    age: int
    sex: SexEnum
    weight: float
    height: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum
    preferred_cuisines: Optional[List[str]] = ""
    disliked_ingredients: Optional[List[str]] = ""
    liked_ingredients: Optional[List[str]] = ""
    allergies: Optional[List[str]] = ""
    meal_timing: Optional[str] = ""
    portion_size: Optional[str] = ""
    snack_preference: Optional[str] = ""
    dietary_preference: Optional[str] = ""
    personal_story: Optional[str] = ""

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    age: Optional[int]
    sex: Optional[SexEnum]
    weight: Optional[float]
    height: Optional[float]
    activity_level: Optional[ActivityLevelEnum]
    goal: Optional[GoalEnum]
    preferred_cuisines: Optional[List[str]]
    disliked_ingredients: Optional[List[str]]
    liked_ingredients: Optional[List[str]]
    allergies: Optional[List[str]]
    meal_timing: Optional[str]
    portion_size: Optional[str]
    snack_preference: Optional[str]
    dietary_preference: Optional[str]
    personal_story: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    username: str

class Message(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Recipe Schemas
class RecipeBase(BaseModel):
    title: str
    instructions: str

class RecipeRead(RecipeBase):
    id: int

    class Config:
        from_attributes = True

class RecipeRating(BaseModel):
    recipe_id: int
    rating: int = Field(..., ge=1, le=5)  # 1 to 5 star rating

class CreateChatSchema(BaseModel):
    participants: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "participants": [1, 2, 3]
            }
        }

class ChatSummary(BaseModel):
    id: UUID
    display_name: str
    last_activity: datetime

    class Config:
        from_attributes = True
