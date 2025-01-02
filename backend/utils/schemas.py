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
    expiry: datetime

class Message(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str


# class IngredientSchema(BaseModel):
#     name: str
#     unit: Optional[str]
#
#     class Config:
#         from_attributes = True
#
#
# class InstructionStepSchema(BaseModel):
#     step_number: int
#     text: str
#
#     class Config:
#         from_attributes = True


class RecipeBase(BaseModel):
    title: str
    prepare_time: int
    cuisine: Optional[str]
    servings: int
    calories: float
    macros: List[str]  # Updated to match ARRAY(String) in the database
    needed_equipment: List[str]  # Updated to match ARRAY(String) in the database
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: List[str]  # Updated to match ARRAY(String)
    instructions: List[str]  # Updated to match ARRAY(String)

    class Config:
        from_attributes = True


class RecipeRead(RecipeBase):
    id: int

    class Config:
        from_attributes = True

class RecipeRating(BaseModel):
    recipe_id: int
    rating: int = Field(..., ge=1, le=5)  # 1 to 5 star rating

class CreateChatSchema(BaseModel):
    participants: List[UUID]

    class Config:
        json_schema_extra = {
            "example": {
                "participants": [1, 2, 3]
            }
        }

class ChatResponseSchema(BaseModel):
    id: UUID  # UUID serialized as a string
    display_name: str
    participants: List[UUID]  # Ensure participants are serialized as strings
    creation_date: datetime
    last_activity: datetime

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models


class ChatSummary(BaseModel):
    id: UUID
    display_name: str
    last_activity: datetime

    class Config:
        from_attributes = True

class UpdateChatMetadata(BaseModel):
    display_name: Optional[str] = None
    last_activity: Optional[datetime] = None
    participants: Optional[List[UUID]] = None  # Example of updating participants, if needed

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




# def model_to_json(model):
#     """Convert a SQLAlchemy model to a JSON schema."""
#     schema = {
#         "type": "object",
#         "properties": {}
#     }
#
#     # Process columns
#     for column in model.__table__.columns:
#         schema["properties"][column.name] = {
#             "type": map_column_type_to_json(str(column.type)),
#             "nullable": column.nullable,
#             "primary_key": column.primary_key
#         }
#
#     # Process relationships
#     for relationship in model.__mapper__.relationships:
#         if relationship.key == "ingredients":
#             schema["properties"][relationship.key] = {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": model_to_json(relationship.mapper.class_).get("properties")
#                 }
#             }
#         elif relationship.key == "instructions":
#             schema["properties"][relationship.key] = {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "step_number": {"type": "integer"},
#                         "text": {"type": "string"}
#                     }
#                 }
#             }
#
#     return schema
#
#
#
#
# def model_to_json_old(model):
#     """Convert a SQLAlchemy model to a JSON schema."""
#     schema = {}
#
#     schema = {
#         "properties": {}
#     }
#     for column in model.__table__.columns:
#         schema[column.name] = {}
#
#     for relationship in model.__mapper__.relationships:
#         if relationship.key == "ingredients":
#             schema["properties"][relationship.key] = {
#                 "items": {
#                     "properties": model_to_json(relationship.mapper.class_).get("properties")
#                 }
#             }
#         elif relationship.key == "instructions":
#             schema["properties"][relationship.key] = {
#                 "items": {
#                     "properties": {
#                         "step_number": {"type": "integer"},
#                         "text": {"type": "string"}
#                     }
#                 }
#             }
#     return schema
#
# def map_column_type_to_json(column_type):
#     """Map SQLAlchemy column types to JSON schema types."""
#     if column_type.startswith("Integer"):
#         return "integer"
#     elif column_type.startswith("String") or column_type.startswith("Text"):
#         return "string"
#     elif column_type.startswith("Float"):
#         return "number"
#     elif column_type.startswith("Boolean"):
#         return "boolean"
#     elif column_type.startswith("JSON") or column_type.startswith("JSONB"):
#         return "object"
#     elif column_type.startswith("DateTime"):
#         return "string"  # ISO 8601 format
#     else:
#         return "string"  # Fallback for unsupported types

