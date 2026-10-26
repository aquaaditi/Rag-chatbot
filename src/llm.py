"""
llm.py - the ONE place in the project that talks to the LLM (Gemini).

Every other module (generator, change-tracker, evaluator...) calls `ask_llm()`
(text answer) or `ask_llm_structured()` (JSON answer) instead of using the API directly. To switch models, change LLM_MODEL in .env;
to switch providers, only this file changes.
"""

from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from src import config

MODEL = config.LLM_MODEL
T = TypeVar("T", bound=BaseModel)  # "some Pydantic model class" - used by ask_llm_structured

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


def ask_llm_structured(user_message: str, schema: type[T], system_prompt: str = "", max_tokens: int = 16000) -> T:
    """Ask for JSON that matches a Pydantic `schema`, and return it as a schema object.

    Gemini's "structured output" mode only lets the model produce JSON of that shape,
    so we get e.g. Talk(slides=[Slide(...), ...]) instead of text we'd have to parse."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )
    if response.parsed is None:  # blocked, cut off by max_tokens, or invalid JSON
        raise ValueError(f"The model did not return valid {schema.__name__} JSON:\n{(response.text or '')[:500]}")
    return response.parsed
