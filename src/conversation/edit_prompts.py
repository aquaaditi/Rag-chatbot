"""
edit_prompts.py - prompts for DELTA-ANCHORED edits.

Instead of regenerating the whole talk (which would change everything and could
drift away from the sources), we send the LLM:
  - ONLY the part to change (one slide, or the script),
  - the change instruction,
  - the SAME sources that part was built from (the "anchor"),
and ask for the new version plus the REASON for the change.
"""

from src.generation.options import AUDIENCES, STYLES
from src.generation.prompts import GROUNDING_RULES
from src.talks import Talk, TalkRequest

EDIT_SYSTEM_PROMPT = f"""You revise one part of an existing slide talk about a research paper.

{GROUNDING_RULES}
8. Change only what the change request asks for; keep everything else as it is.
9. Return JSON that matches the given schema exactly."""

SLIDE_TEMPLATE = """CHANGE REQUEST: {instruction}
Apply it to SLIDE {number} only.

AUDIENCE: {audience}
STYLE: {style}
TALK OUTLINE (for context - do not change other slides):
{outline}

CURRENT SLIDE {number} (JSON):
{slide_json}

Rules for the new slide:
- Keep the slide's topic and its place in the talk.
- 3-5 bullets and EXACTLY {notes} speaker notes.
- Every fact still cites its chunk ID(s) from the SOURCES. Add no facts that are not in the SOURCES.
- "reason": 1-2 sentences on WHAT you changed and WHY (refer to the change request).

SOURCES (the same sources the talk was built from):
{sources}"""

SCRIPT_TEMPLATE = """CHANGE REQUEST: {instruction}
Apply it to the SPOKEN SCRIPT of the talk.

AUDIENCE: {audience}
STYLE: {style}
TALK OUTLINE (the script must still follow these slides in order):
{outline}

CURRENT SCRIPT ({current_words} words):
{script}

Rules for the new script:
- Every factual sentence still cites its chunk ID(s) from the SOURCES. Add no new facts.
- {length_rule}
- "reason": 1-2 sentences on WHAT you changed and WHY (refer to the change request).

SOURCES:
{sources}"""

WHOLE_TALK_TEMPLATE = """CHANGE REQUEST: {instruction}
Apply it to the WHOLE talk (all slides and the script).

AUDIENCE: {audience}
STYLE: {style}

CURRENT TALK (JSON):
{talk_json}

Rules for the new talk:
- Keep the same number of slides ({n_slides}) and EXACTLY {notes} speaker notes per slide.
- Every fact still cites its chunk ID(s) from the SOURCES. Add no facts that are not in the SOURCES.
- "reason": 1-3 sentences on WHAT you changed and WHY (refer to the change request).

SOURCES:
{sources}"""


def outline(talk: Talk) -> str:
    return "\n".join(f"{i}. {slide.title}" for i, slide in enumerate(talk.slides, start=1))


def build_slide_edit_prompt(talk: Talk, number: int, instruction: str, request: TalkRequest, sources: str) -> str:
    return SLIDE_TEMPLATE.format(
        instruction=instruction, number=number, audience=AUDIENCES[request.audience], style=STYLES[request.style],
        outline=outline(talk), slide_json=talk.slides[number - 1].model_dump_json(indent=2),
        notes=request.notes_per_slide, sources=sources,
    )


def build_script_edit_prompt(talk: Talk, instruction: str, request: TalkRequest, sources: str,
                             target_words: int | None = None) -> str:
    length_rule = (
        f"The new script MUST have about {target_words} words (150 words per minute) - "
        f"the current one has {len(talk.script.split())}, so {'cut' if target_words < len(talk.script.split()) else 'extend'} it."
        if target_words else "Keep about the same length unless the request asks otherwise."
    )
    return SCRIPT_TEMPLATE.format(
        instruction=instruction, audience=AUDIENCES[request.audience], style=STYLES[request.style],
        outline=outline(talk), script=talk.script, current_words=len(talk.script.split()),
        length_rule=length_rule, sources=sources,
    )


RETRY_BLOCK = """

YOUR PREVIOUS ATTEMPT AT THIS CHANGE FAILED A MEASURED CHECK:
{feedback}
Start again from the CURRENT version above and make the change properly."""


def with_feedback(prompt: str, feedback: str) -> str:
    """Add the result of a failed check to a prompt (for the one retry)."""
    return prompt + RETRY_BLOCK.format(feedback=feedback) if feedback else prompt


def build_whole_talk_edit_prompt(talk: Talk, instruction: str, request: TalkRequest, sources: str) -> str:
    return WHOLE_TALK_TEMPLATE.format(
        instruction=instruction, audience=AUDIENCES[request.audience], style=STYLES[request.style],
        talk_json=talk.model_dump_json(indent=2), n_slides=len(talk.slides),
        notes=request.notes_per_slide, sources=sources,
    )
