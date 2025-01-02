from utils.database import recipe_session
from utils.models import Recipe, Ingredient, InstructionStep, recipe_ingredient_association, instruction_step_association
from utils.schemas import RecipeBase
from sqlalchemy.exc import IntegrityError

def add_recipe_to_db(db: recipe_session, recipe_data: RecipeBase):
    """
    Add a new recipe to the database.

    Args:
        db (Session): SQLAlchemy session for the database.
        recipe_data (RecipeBase): Recipe data as a Pydantic model.

    Returns:
        dict: Result message or created recipe.
    """
    try:
        # Create the Recipe object
        recipe = Recipe(
            title=recipe_data.title,
            prepare_time=recipe_data.prepare_time,
            servings=recipe_data.servings,
            calories=recipe_data.calories,
            macros=recipe_data.macros,
            needed_equipment=recipe_data.needed_equipment,
            cuisine=recipe_data.cuisine,
            tags=recipe_data.tags,
            source=recipe_data.source,
            image_url=recipe_data.image_url
        )

        # Handle ingredients
        for ingredient in recipe_data.ingredients:
            db_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient["name"]).first()
            if not db_ingredient:
                db_ingredient = Ingredient(name=ingredient["name"], unit=ingredient.get("unit"))
                db.add(db_ingredient)
                db.commit()
            db.execute(recipe_ingredient_association.insert().values(
                recipe_id=recipe.id, ingredient_id=db_ingredient.id, quantity=ingredient["quantity"]
            ))

        # Handle instructions
        for idx, step in enumerate(recipe_data.instructions, start=1):
            instruction = InstructionStep(step_number=idx, text=step)
            db.add(instruction)
            db.commit()
            db.execute(instruction_step_association.insert().values(
                recipe_id=recipe.id, instruction_id=instruction.id, step_number=idx
            ))

        # Add and commit the recipe
        db.add(recipe)
        db.commit()

        return {"message": "Recipe added successfully", "recipe": recipe}
    except IntegrityError:
        db.rollback()
        return {"error": "Failed to add recipe. Integrity constraints violated."}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
