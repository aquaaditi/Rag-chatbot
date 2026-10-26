"""
prompts.py - the prompt template for a slide talk.

Same template family as src/generation/prompts.py ({audience}, {length},
{style}, {change_instruction}) plus the talk structure: number of slides,
notes per slide, focus and whether to preserve equations.
The grounding rules (only use sources, cite every fact...) are shared.
"""

from src.generation.options import AUDIENCES, STYLES
from src.generation.prompts import GROUNDING_RULES, change_block
from src.talks.request import TalkRequest

TALK_SYSTEM_PROMPT = f"""You turn research papers into slide talks for a specific audience.

{GROUNDING_RULES}
8. Return JSON that matches the given schema exactly."""

TALK_TEMPLATE = """TASK: Create a {n_slides}-slide talk about: {topic}
{focus_line}
AUDIENCE: {audience}
STYLE: {style}

STRUCTURE:
- Exactly {n_slides} slides in a logical order (e.g. motivation -> method -> results -> takeaway).
- Each slide: a short title, 3-5 bullets, and EXACTLY {notes_per_slide} speaker notes.
- {equation_rule}
- Speaker notes ADD to the bullets (an example, an explanation, a "why it matters") - never
  just repeat a bullet.
- "script": the full spoken talk covering all slides in order, about {target_words} words
  ({length} when read aloud at 150 words per minute). Write it as natural speech for this
  audience, with transitions between slides ("Now let's look at..."). Do NOT paste the bullets
  and notes together, and never say the same sentence twice.
- Cite chunk IDs in square brackets after every bullet, speaker note and script sentence that
  states a fact.
{change_block}
SOURCES:
{sources}"""

PRESERVE_EQUATIONS = (
    "PRESERVE KEY EQUATIONS: put the important equations from the sources in the slides' "
    '"equations" lists (LaTeX, no $ signs) and explain them in the speaker notes with inline '
    "LaTeX $...$. Copy every term; do not simplify an equation."
)
NO_EQUATIONS = 'Equations are optional; leave "equations" empty unless one is essential.'

RETRY_TEMPLATE = """{original_prompt}

YOUR PREVIOUS ANSWER HAD THESE PROBLEMS - fix all of them and return the complete talk again:
{problems}"""


def build_talk_prompt(request: TalkRequest, sources: str) -> str:
    return TALK_TEMPLATE.format(
        n_slides=request.n_slides,
        topic=request.topic,
        focus_line=f"FOCUS: spend most slides on {request.focus}.\n" if request.focus else "",
        audience=AUDIENCES[request.audience],
        style=STYLES[request.style],
        notes_per_slide=request.notes_per_slide,
        equation_rule=PRESERVE_EQUATIONS if request.preserve_equations else NO_EQUATIONS,
        target_words=request.target_words,
        length=request.length,
        change_block=change_block(request.change_instruction),
        sources=sources,
    )


def build_retry_prompt(original_prompt: str, problems: list[str]) -> str:
    return RETRY_TEMPLATE.format(
        original_prompt=original_prompt, problems="\n".join(f"- {p}" for p in problems)
    )
