"""
llm.py - the ONE place in the project that talks to the LLM.

Every other module (generator, change-tracker, evaluator...) will call
`ask_llm()` instead of using the API directly. If you ever want to switch
models or providers, you only change this file.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Read GEMINI_API_KEY and LLM_MODEL from the .env file into environment variables
load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_llm(user_message: str, system_prompt: str = "", max_tokens: int = 8000) -> str:
    """Send one message to the LLM and return its text reply."""
    response = client.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            max_output_tokens=max_tokens,
        ),
    )

    # response.text is None when the model returns no text (e.g. blocked by a safety filter)
    return response.text or "[The model returned no text for this request.]"
