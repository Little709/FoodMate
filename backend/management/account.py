from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.database import SessionLocal
from utils.schemas import UserRead, UserCreate
from utils.models import User
from utils.authutils import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/account", response_model=UserRead)
# def get_user_account():
#     print("hi")
def get_user_account(current_user: User = Depends(get_current_user)):
    print(current_user)
    return current_user

@router.put("/account", response_model=UserRead)
def update_user_account(

    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(current_user)
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/test")
def test_route():
    return {"message": "Test route works"}
