# backend/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from utils.database import general_session
from utils.authutils import create_access_token
from utils.schemas import UserRead, UserCreate, Token,LoginRequest
from utils.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
)


def get_db():
    db = general_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter_by(username=user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash password
    hashed_password = pwd_context.hash(user_data.password)

    # Create new user instance with additional fields
    new_user = User(
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


@router.post("/login", response_model=Token)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    print("Login endpoint hit")
    db_user = db.query(User).filter_by(username=login_data.username).first()

    # Check if the user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # Check if the password matches
    if not pwd_context.verify(login_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token
    access_token, expire = create_access_token(data={"sub": db_user.username})

    # Return the user data along with the generated token
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=db_user.id,
        username=db_user.username,
        expiry=expire
    )

