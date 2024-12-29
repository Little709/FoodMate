from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.database import SessionLocal
from utils.schemas import UserRead, UserCreate, UserUpdate
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
def get_user_account(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/account", response_model=UserRead)
def update_user_account(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

