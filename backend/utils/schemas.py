from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
import re

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
    preferred_cuisines: Optional[str] = ""
    disliked_ingredients: Optional[str] = ""

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserRead(UserBase):
    id: int
    age: int
    sex: SexEnum
    weight: float
    height: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum
    preferred_cuisines: Optional[str] = ""
    disliked_ingredients: Optional[str] = ""

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
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
        orm_mode = True

class RecipeRating(BaseModel):
    recipe_id: int
    rating: int = Field(..., ge=1, le=5)  # 1 to 5 star rating
