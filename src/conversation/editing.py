"""
editing.py - apply ONE change to a talk and return the new talk + the reason.

    new_talk, reason = editor.edit_slide(talk, 2, "make it less technical", request, sources)

The original talk is never modified: we return a new copy, so every version
can be kept (and undone). `feedback` is used for a retry after a failed check
(see goals.py).
"""

from collections.abc import Callable

from pydantic import BaseModel, Field

from src.chunking import Chunk
from src.conversation.edit_prompts import (
    EDIT_SYSTEM_PROMPT, build_script_edit_prompt, build_slide_edit_prompt, build_whole_talk_edit_prompt,
    with_feedback,
)
from src.conversation.goals import target_words
from src.generation.context import format_sources
from src.llm import ask_llm_structured
from src.talks import Slide, Talk, TalkRequest

REASON = "1-3 sentences: what was changed and why, referring to the change request."


class SlideEdit(BaseModel):
    slide: Slide
    reason: str = Field(description=REASON)


class ScriptEdit(BaseModel):
    script: str
    reason: str = Field(description=REASON)


class TalkEdit(BaseModel):
    talk: Talk
    reason: str = Field(description=REASON)


class Editor:
    def __init__(self, llm_structured: Callable[..., BaseModel] = ask_llm_structured):
        self._llm = llm_structured

    def edit_slide(self, talk: Talk, number: int, instruction: str, request: TalkRequest,
                   sources: list[Chunk], feedback: str = "") -> tuple[Talk, str]:
        prompt = build_slide_edit_prompt(talk, number, instruction, request, format_sources(sources))
        edit = self._ask(prompt, feedback, SlideEdit)
        new_talk = talk.model_copy(deep=True)
        new_talk.slides[number - 1] = edit.slide
        return new_talk, edit.reason

    def edit_script(self, talk: Talk, instruction: str, request: TalkRequest,
                    sources: list[Chunk], feedback: str = "") -> tuple[Talk, str]:
        prompt = build_script_edit_prompt(talk, instruction, request, format_sources(sources),
                                          target_words=target_words(instruction))
        edit = self._ask(prompt, feedback, ScriptEdit)
        new_talk = talk.model_copy(deep=True)
        new_talk.script = edit.script
        return new_talk, edit.reason

    def edit_whole_talk(self, talk: Talk, instruction: str, request: TalkRequest,
                        sources: list[Chunk], feedback: str = "") -> tuple[Talk, str]:
        prompt = build_whole_talk_edit_prompt(talk, instruction, request, format_sources(sources))
        edit = self._ask(prompt, feedback, TalkEdit)
        return edit.talk, edit.reason

    def _ask(self, prompt: str, feedback: str, schema: type[BaseModel]) -> BaseModel:
        return self._llm(with_feedback(prompt, feedback), schema=schema, system_prompt=EDIT_SYSTEM_PROMPT)
