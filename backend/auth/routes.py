# backend/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from utils.database import SessionLocal
from utils import models, schemas, authutils
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter_by(username=user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash password
    hashed_password = pwd_context.hash(user_data.password)

    # Create new user instance with additional fields
    new_user = models.User(
        username=user_data.username,
        hashed_password=hashed_password,
        preferred_cuisines=user_data.preferred_cuisines,
        disliked_ingredients=user_data.disliked_ingredients,
        age=user_data.age,
        sex=user_data.sex.value,  # Assuming enums are used in schemas
        weight=user_data.weight,
        height=user_data.height,
        activity_level=user_data.activity_level.value,
        goal=user_data.goal.value
    )

    # Add to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login_user(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    print("Login endpoint hit")
    db_user = db.query(models.User).filter_by(username=login_data.username).first()

    # Check if the user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # Check if the password matches
    if not pwd_context.verify(login_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token
    access_token = authutils.create_access_token(data={"sub": db_user.username})

    # Return the user data along with the generated token
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_id=db_user.id,
        username=db_user.username
    )


@router.get("/account", response_model=schemas.UserRead)
def get_account(current_user: models.User = Depends(authutils.get_current_user)):
    """
    Retrieves the account information of the currently authenticated user.
    """
    return current_user


@router.post("/logout", response_model=schemas.Message)
def logout_user(token: str = Depends(authutils.oauth2_scheme), db: Session = Depends(get_db)):
    """
    Logs the user out by adding the token to the blacklist.
    The token will no longer be valid after this operation.
    """
    authutils.add_token_to_blacklist(token, db)
    return schemas.Message(message="Successfully logged out")


@router.get("/test")
def test_route():
    return {"message": "Test route works"}
