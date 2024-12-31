# backend/chatgpt_integration.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_recipe_suggestion(user_preferences, previous_ratings):
    prompt = f"""
    Given these user preferences: {user_preferences},
    and these recipe ratings: {previous_ratings},
    suggest a new recipe with ingredients and instructions...
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
    )
    return response.choices[0].text
