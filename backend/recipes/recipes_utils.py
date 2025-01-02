from sqlalchemy.orm import Session
from typing import Dict
from utils.models import Recipe
from utils.schemas import RecipeBase
from pydantic import ValidationError
import logging

logger = logging.getLogger("uvicorn")

def add_recipe_to_db(recipe_data: Recipe, db: Session) -> Recipe:

    if not recipe_data:
        raise ValueError("Recipe data is None. Ensure valid data is passed.")

    # Create a new Recipe object
    print(recipe_data)
    recipe = Recipe(
        title=recipe_data.title,
        prepare_time=recipe_data.prepare_time,
        cuisine=recipe_data.cuisine,
        servings=recipe_data.servings,
        calories=recipe_data.calories,
        macros=recipe_data.macros,
        needed_equipment=recipe_data.needed_equipment,
        tags=recipe_data.tags,
        source=recipe_data.source,
        image_url=recipe_data.image_url,
        ingredients=recipe_data.ingredients,
        instructions=recipe_data.instructions,
        # macros=recipe_data.macros

    )


    # Add and commit the Recipe object
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe

def format_recipe_input(raw_recipe):
    try:
        formatted_recipe = {
            "title": raw_recipe.get("title"),
            "prepare_time": raw_recipe.get("prepare_time"),
            "cuisine": raw_recipe.get("cuisine"),
            "servings": raw_recipe.get("servings"),
            "calories": raw_recipe.get("calories"),
            "macros": {k: float(v) for k, v in (item.split(": ") for item in raw_recipe.get("macros", []))},
            "needed_equipment": {str(i): eq for i, eq in enumerate(raw_recipe.get("needed_equipment", []), start=1)},
            "ingredients": [
                {"name": ing.split(" (")[0], "unit": ing.split(" (")[1].rstrip(")")}
                for ing in raw_recipe.get("ingredients", [])
            ],
            "instructions": [
                {"step_number": i + 1, "text": step}
                for i, step in enumerate(raw_recipe.get("instructions", []))
            ],
        }
        return formatted_recipe
    except Exception as e:
        logger.error(f"Error formatting recipe data: {e}")
        raise ValueError("Invalid recipe format")

def transform_recipe_json(json_data):
    try:
        # Ensure numeric fields are correctly converted
        json_data["prepare_time"] = int(json_data["prepare_time"])
        json_data["servings"] = int(json_data["servings"])
        json_data["calories"] = float(json_data["calories"])

        # Validate that required fields are present and correct
        if not json_data.get("ingredients") or not isinstance(json_data["ingredients"], list):
            raise ValueError("Missing or invalid 'ingredients': must be a non-empty list of strings.")
        if not json_data.get("instructions") or not isinstance(json_data["instructions"], list):
            raise ValueError("Missing or invalid 'instructions': must be a non-empty list of strings.")
        if not json_data.get("macros") or not isinstance(json_data["macros"], list):
            raise ValueError("Missing or invalid 'macros': must be a list of strings.")
        if not json_data.get("needed_equipment") or not isinstance(json_data["needed_equipment"], list):
            raise ValueError("Missing or invalid 'needed_equipment': must be a list of strings.")

        # Ensure tags are a list or None
        json_data["tags"] = json_data.get("tags", None)
        if json_data["tags"] is not None and not isinstance(json_data["tags"], list):
            raise ValueError("Invalid 'tags': must be a list of strings or None.")

        # Validate and create RecipeBase object
        recipe = RecipeBase(**json_data)
        return recipe

    except ValidationError as e:
        print(f"Validation Error: {e}")
        return None
    except ValueError as e:
        print(f"Value Error: {e}")
        return None
