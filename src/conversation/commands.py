"""
commands.py - understand what the user wants from a chat message.

Two paths:
  1. FAST PATH (no LLM): exact commands like "undo", "history", "show #2", "save".
  2. LLM PATH: anything else is turned into a ParsedMessage by Gemini (structured
     output), e.g. "dumb down #3" -> action="edit", slide_numbers=[3],
     instruction="make it simpler and less technical for non-experts".
"""

import re
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, Field

from src.llm import ask_llm_structured
from src.talks import TalkRequest

DEFAULT_TOPIC = "the paper's motivation, method, key equations and results"


class ParsedMessage(BaseModel):
    action: Literal["create", "edit", "show", "undo", "history", "save", "other"]
    slide_numbers: list[int] = Field(description='Slides the user refers to: "#2", "slide 2", "the second slide" -> [2]. Empty if none.')
    target: Literal["slides", "script", "whole_talk"] = Field(
        description='"slides" if specific slides are named, "script" for the spoken script, otherwise "whole_talk".'
    )
    instruction: str = Field(description='For edit: the change as a clear instruction, e.g. "dumb down" -> '
                                         '"make it simpler and less technical for non-experts". Else empty.')
    # Only for action="create" - null when the user did not say it
    paper_id: str | None = Field(description="For create: the paper's ID from the list, e.g. P3.")
    n_slides: int | None
    notes_per_slide: int | None
    audience: Literal["policymakers", "grad_students", "press"] | None
    style: Literal["technical", "plain_english", "press_release"] | None
    length: Literal["30s", "90s", "5min", "7min"] | None = Field(description="Length of the spoken script.")
    focus: str | None = Field(description='What to focus on, e.g. "methods".')
    preserve_equations: bool | None


PARSE_TEMPLATE = """You are the command parser of a chatbot that turns research papers into slide talks.
Read the user's MESSAGE and fill in the JSON.

Actions:
- create:  the user wants a NEW talk ("make a 7-slide talk on the distillation paper for policymakers")
- edit:    the user wants to change the current talk ("make #2 less technical", "dumb down slide 3",
           "make the whole talk more visual", "shorten the script")
- show:    the user wants to see the talk or some slides ("show slide 4")
- undo:    go back to the previous version
- history: list the versions / changes so far
- save:    save the talk / the conversation
- other:   anything else (greetings, questions)

Papers available: {papers}
{current_talk}

MESSAGE: {message}"""

META_COMMANDS = {
    "undo": "undo", "back": "undo",
    "history": "history", "versions": "history",
    "show": "show", "show talk": "show",
    "save": "save",
}


def match_meta_command(message: str) -> ParsedMessage | None:
    """Exact short commands are handled without calling the LLM (instant, free)."""
    text = message.strip().lower().rstrip(".!")
    show_slide = re.fullmatch(r"show (?:slide |#)?(\d+)", text)
    if show_slide:
        return _parsed("show", slide_numbers=[int(show_slide.group(1))], target="slides")
    if text in META_COMMANDS:
        return _parsed(META_COMMANDS[text])
    return None


def parse_message(
    message: str, papers: dict[str, str], n_slides: int | None,
    llm_structured: Callable[..., ParsedMessage] = ask_llm_structured,
) -> ParsedMessage:
    meta = match_meta_command(message)
    if meta:
        return meta
    current = f"The current talk has {n_slides} slides." if n_slides else "There is no talk yet."
    paper_list = "; ".join(f"{pid} = {title}" for pid, title in papers.items())
    prompt = PARSE_TEMPLATE.format(papers=paper_list, current_talk=current, message=message)
    return llm_structured(prompt, schema=ParsedMessage)


def to_talk_request(parsed: ParsedMessage) -> TalkRequest:
    """Turn a "create" message into a TalkRequest, with sensible defaults for what was not said."""
    audience = parsed.audience or "grad_students"
    return TalkRequest(
        topic=DEFAULT_TOPIC,
        n_slides=parsed.n_slides or 7,
        notes_per_slide=parsed.notes_per_slide or 3,
        audience=audience,
        style=parsed.style or ("technical" if audience == "grad_students" else "plain_english"),
        length=parsed.length or "5min",
        focus=parsed.focus or "",
        preserve_equations=parsed.preserve_equations if parsed.preserve_equations is not None
        else audience == "grad_students",
        paper_id=parsed.paper_id,
    )


def _parsed(action: str, slide_numbers: list[int] | None = None, target: str = "whole_talk") -> ParsedMessage:
    return ParsedMessage(
        action=action, slide_numbers=slide_numbers or [], target=target, instruction="",
        paper_id=None, n_slides=None, notes_per_slide=None, audience=None, style=None,
        length=None, focus=None, preserve_equations=None,
    )
