# Updated backend/auth/utils.py
from datetime import datetime, timedelta
import datetime as dt
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from utils import models
from utils.models import User
from utils.database import SessionLocal
from pathlib import Path
import os
from dotenv import load_dotenv
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import logging
logging.basicConfig(level=logging.INFO)  # Configure logging level globally
logger = logging.getLogger(__name__)



# Load .env from two levels up
env_path = Path(__file__).resolve().parents[2] / ".env"
# print(f"Trying to load .env from: {env_path}")  # Debug print

load_dotenv(dotenv_path=env_path)

# Retrieve the SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Debugging to confirm the values are loaded
# print(f"SECRET_KEY: {SECRET_KEY}")  # Debug print
# print(f"ALGORITHM: {ALGORITHM}")  # Debug print
# print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")  # Debug print

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(dt.UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Add token to blacklist
def add_token_to_blacklist(token: str, db: Session):
    """Add the token to the blacklist table."""
    blacklisted_token = models.BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()


# Check if token is blacklisted
def is_token_blacklisted(token: str, db: Session) -> bool:
    """Check if the token is in the blacklist."""
    return db.query(models.BlacklistedToken).filter(models.BlacklistedToken.token == token).first() is not None


# Get the current user and check if the token is blacklisted
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logger.debug(f"Token passed to get_current_user: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.debug(f"Decoded payload: {payload}")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(models.User).filter(models.User.username == username).first()
        logger.debug(f"Found user: {user}")
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError as e:
        logger.debug(f"JWT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str):
    """Verifies a JWT token and returns the associated user."""
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Check if the user exists in the database
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == username).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            return user
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e