from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils.database import general_session, Base, general_engine
from utils.authutils import get_current_user  # Assuming this function decodes and verifies JWT
from utils import models, schemas
import logging

router = APIRouter()

def get_db():
    db = general_session()
    try:
        yield db
    finally:
        db.close()


logger = logging.getLogger("uvicorn")

Base.metadata.create_all(bind=general_engine)
logger.info(f"Tables in metadata: {Base.metadata.tables.keys()}")
logger.info("Recipe tables created successfully.")


# Protect routes by requiring authentication
@router.post("/create", response_model=schemas.RecipeRead)
def create_recipe(recipe_data: schemas.RecipeBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipe = models.Recipe(
        title=recipe_data.title,
        instructions=recipe_data.instructions,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe

@router.post("/rate")
def rate_recipe(rating_data: schemas.RecipeRating, user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # user_id might come from the JWT (current_user is already authenticated)
    rating = models.UserRecipeRating(
        user_id=user_id,
        recipe_id=rating_data.recipe_id,
        rating=rating_data.rating
    )
    db.add(rating)
    db.commit()
    return {"detail": "Rating saved"}

@router.get("/list", response_model=list[schemas.RecipeRead])
def list_recipes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Recipe).all()

@router.get("/{recipe_id}", response_model=schemas.RecipeRead)
def get_recipe(recipe_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Recipe).filter_by(id=recipe_id).first()
