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
    return schema.model_validate(_repair_latex(response.parsed.model_dump()))


# When the model writes LaTeX like \frac or \text inside JSON without escaping the backslash,
# JSON reads "\f" as a form-feed character, "\t" as a tab, "\b" as backspace, "\r" as a carriage
# return - so "\frac" arrives as "<form feed>rac". These characters never belong in our text,
# so we turn them back into the backslash + letter the model meant.
CONTROL_TO_LATEX = {"\f": "\\f", "\b": "\\b", "\t": "\\t", "\r": "\\r"}


def _repair_latex(value):
    """Recursively fix strings inside the parsed JSON (dicts, lists, strings)."""
    if isinstance(value, str):
        for char, latex in CONTROL_TO_LATEX.items():
            value = value.replace(char, latex)
        return value
    if isinstance(value, list):
        return [_repair_latex(v) for v in value]
    if isinstance(value, dict):
        return {k: _repair_latex(v) for k, v in value.items()}
    return value
