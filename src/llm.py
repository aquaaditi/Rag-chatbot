"""
llm.py - the ONE place in the project that talks to the LLM (Gemini).

Every other module (generator, change-tracker, evaluator...) calls `ask_llm()`
instead of using the API directly. To switch models, change LLM_MODEL in .env;
to switch providers, only this file changes.
"""

from google import genai
from google.genai import types

from src import config

MODEL = config.LLM_MODEL

_client = genai.Client(
    api_key=config.GEMINI_API_KEY,
    http_options=types.HttpOptions(
        # Give up on a single request instead of waiting forever
        timeout=config.LLM_TIMEOUT_MS,
        # If Google is overloaded (429 / 503 / 504...), wait a bit and try again
        retry_options=types.HttpRetryOptions(
            attempts=config.LLM_RETRY_ATTEMPTS,
            http_status_codes=config.LLM_RETRY_STATUS_CODES,
        ),
    ),
)


def ask_llm(user_message: str, system_prompt: str = "", max_tokens: int = 8000) -> str:
    """Send one message to the LLM and return its text reply."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            max_output_tokens=max_tokens,
        ),
    )

    # response.text is None when the model returns no text (e.g. blocked by a safety filter)
    return response.text or "[The model returned no text for this request.]"
