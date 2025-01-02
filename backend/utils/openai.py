from openai.types.beta.threads import TextContentBlock
from sqlalchemy import inspect
from utils.models import ChatsMetadata, create_chat_model, Recipe
from utils.database import general_session
from utils.schemas import RecipeBase
from recipes.recipes_utils import add_recipe_to_db, transform_recipe_json
from openai import OpenAI, types, pagination
from openai.types.beta.thread import Thread
from openai.types.beta.assistant import Assistant
from utils.schemas import RecipeBase
from pydantic import ValidationError


from pydantic import BaseModel
from typing import List, Literal

import logging
import json
import traceback
import re

# Define a message model
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

# Define the response model
class MessagesResponse(BaseModel):
    data: List[Message]


logger = logging.getLogger("uvicorn")

wanted_response = RecipeBase.schema()

llm_model = "gpt-4o-mini"
instructions = (
            "You are a master dietitian. The user is Dutch, so generate 3 unique recipes in Dutch. "
            "Use the ingredients and data provided in the JSON input to create new recipes. "
            "Ensure the response is in JSON format containing exactly 3 recipes, with no extra text or examples. "
            f"The JSON example is {wanted_response}"
            "Do not return the provided example or input JSON. Only provide new recipes."
            "Please respond with valid JSON only. No explanations, just the JSON."
        )

def get_db():
    db = general_session()
    try:
        yield db
    finally:
        db.close()

def sanitize_json(json_str):
    """
    Attempt to fix common JSON issues like trailing commas.
    """
    # Remove trailing commas before closing brackets or braces
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
    return json_str

def extract_json_from_messages(message):
    try:
        # Regex to match the first JSON block
        json_pattern = r'\{(?:[^{}]*|\{[^{}]*\})*\}|\[.*\]'  # Includes lists and objects
        match = re.search(json_pattern, message, re.DOTALL)

        if not match:
            raise ValueError("No JSON object found in the message.")

        # Extract the matched JSON string
        json_str = match.group(0).strip()

        # Sanitize the JSON string to fix common errors
        sanitized_json_str = sanitize_json(json_str)

        # Parse the sanitized JSON string into a Python object
        try:
            parsed_data = json.loads(sanitized_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Sanitized JSON still invalid: {e}") from e

        # Check if it's a dictionary containing "recipes" or a direct list
        if isinstance(parsed_data, dict) and "recipes" in parsed_data:
            recipes = parsed_data["recipes"]
        elif isinstance(parsed_data, list):
            recipes = parsed_data
        else:
            raise ValueError("Unexpected JSON format: Could not find recipes.")

        # Get text before and after the JSON object
        start_index = match.start()
        end_index = match.end()
        text_before = message[:start_index].strip()
        text_after = message[end_index:].strip()

        return text_before, recipes, text_after

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}") from e
    except Exception as e:
        raise ValueError(f"Error extracting JSON: {e}") from e




def process_openai_tasks(data, display_name, current_user, db, chat_db, client: OpenAI, assistant: Assistant,
                         thread: Thread):
    try:

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=instructions,
        )

        if run.status == 'completed':
            response = client.beta.threads.messages.list(thread_id=thread.id)

            for message in response.data:
                if message.assistant_id == assistant.id and isinstance(message.content, list):
                    for content_block in message.content:
                        if isinstance(content_block, TextContentBlock):
                            if content_block.type == 'text':  # Ensure it's a text block
                                raw_text = content_block.text.value  # Extract the raw text value
                                try:
                                    before, recipes, after = extract_json_from_messages(raw_text)
                                    logger.error(recipes, before, after)
                                    recipes = recipes

                                    for recipe in recipes:
                                        try:
                                            recipe = transform_recipe_json(recipe)
                                            processed_recipe = add_recipe_to_db(recipe, db)
                                            logger.info(f"Converted to RecipeBase: {processed_recipe}")
                                        except Exception as e:
                                            logger.error("An error occurred during recipe processing.")
                                            logger.error(f"Raw recipe: {recipe}")
                                            logger.error(f"Traceback: {traceback.format_exc()}")

                                except Exception as e:
                                    logger.error("An error occurred during recipe processing.")
                                    logger.error(f"Raw text: {raw_text}")
                                    logger.error(f"Traceback: {traceback.format_exc()}")

                        else:
                            print(f"Unexpected content block type: {type(content_block)} - {content_block}")
    except Exception as e:
        logger.error(f"Error in background OpenAI task: {e}")
