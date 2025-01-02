from openai.types.beta.threads import TextContentBlock
from sqlalchemy import inspect
from utils.models import ChatsMetadata, create_chat_model, Recipe, Ingredient
from utils.database import recipe_session
from utils.schemas import model_to_json
from utils.database import Base
from recipes.recipes_utils import add_recipe_to_db
from openai import OpenAI, types, pagination
from openai.types.beta.thread import Thread
from openai.types.beta.assistant import Assistant
from openai.pagination import SyncCursorPage
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime as dt
import logging
import json
import os


# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

# Define a message model
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

# Define the response model
class MessagesResponse(BaseModel):
    data: List[Message]

wanted_response = model_to_json(Recipe)
logger = logging.getLogger("uvicorn")

def get_db():
    db = recipe_session()
    try:
        yield db
    finally:
        db.close()

def extract_json_from_messages(message):
    try:
        # 1. Split the content based on the triple backticks
        parts = message.split('```json')
        text_before = parts[0].strip()  # Everything before the ```json
        json_block_part = parts[1].split('```')  # Split the second part to isolate the JSON

        json_str = json_block_part[0].strip()  # This is the raw JSON string
        text_after = json_block_part[-1].strip()  # If there's anything after the closing ```

        # 2. Parse the JSON string into a Python dictionary
        parsed_data = json.loads(json_str)

        print("TEXT BEFORE:\n", text_before)
        print("\nJSON STRING:\n", json_str)
        print("\nPARSED JSON OBJECT:\n", parsed_data)
        print("\nTEXT AFTER (if any):\n", text_after)

        # return text_before,parsed_data,text_after

    except AttributeError as e:
        logger.error(f"Attribute error while parsing message: {e}")
        return None

def process_openai_tasks(data, display_name, current_user, db, chat_db, client: OpenAI, assistant:Assistant, thread:Thread):
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=json.dumps(data),
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=f"You are a master dietitian. The user is dutch, so please generate recipes in dutch. You take the data from the JSON provided and generate 3 recipes in this JSON format:{wanted_response}",
        )
        # assistant_response = run['choices'][0]['message']['content']
        # logger.error("first:",assistant_response)
        # if hasattr(run, "output") and run.output is not None:
        #     assistant_response = runZ.output["choices"][0]["message"]["content"]
        #     print("Assistant's response:", assistant_response)
        # else:
        #     print("Task did not complete successfully or output is not available.")
        if run.status == 'completed':
            response = client.beta.threads.messages.list(thread_id=thread.id)

            for message in response.data:
                if message.assistant_id == assistant.id and isinstance(message.content, TextContentBlock):
                    # Extract and process the TextContentBlock
                    text_block = message.content
                    if text_block.type == 'text':  # Ensure it's a text block
                        raw_text = text_block.text.value  # Get the raw text value
                        try:
                            # Parse the JSON from the text value if applicable
                            parsed_json = json.loads(raw_text)
                            print("Parsed JSON Content:", parsed_json)
                        except json.JSONDecodeError:
                            # Handle cases where the text isn't valid JSON
                            print("Text Content (Non-JSON):", raw_text)
                else:
                    print(f"failed: Message Content: {message.content}")

        # if run.status == 'completed':
        #     response = client.beta.threads.messages.list(thread_id=thread.id)
        #
        #     for message in response.data:
        #         if(message.assistant_id==assistant.id):
        #             print(f"{message.content}")
        #
        # else:
        #     logger.error(run.status)

    except Exception as e:
        logger.error(f"Error in background OpenAI task: {e}")
