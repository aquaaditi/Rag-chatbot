"""
request.py - TalkRequest: everything the user asks for in a slide talk.

Example from the task:
    "Make a 7-slide talk for graduate students focusing on methods;
     include 3 speaker notes per slide and preserve key equations"
becomes
    TalkRequest(topic="the methods", n_slides=7, notes_per_slide=3,
                audience="grad_students", focus="methods", preserve_equations=True)
"""

from dataclasses import dataclass

from src.generation.options import (
    AUDIENCES, CHUNKS_FOR_LENGTH, LENGTHS, STYLES, check_choice, target_words_for,
)

# Extra equation chunks added to the sources. Was 3, but then the distillation paper's most
# important equation (softmax with temperature, ranked 4th) was left out - see NOTES.md Day 5.
MATH_CHUNKS_WHEN_PRESERVING = 5


@dataclass
class TalkRequest:
    topic: str
    n_slides: int = 7
    notes_per_slide: int = 3
    audience: str = "grad_students"
    style: str = "technical"
    length: str = "5min"  # length of the full speaker script
    focus: str = ""  # e.g. "methods" - what to spend most slides on
    preserve_equations: bool = True
    paper_id: str | None = None
    change_instruction: str = ""

    def __post_init__(self):
        check_choice("audience", self.audience, AUDIENCES)
        check_choice("style", self.style, STYLES)
        check_choice("length", self.length, LENGTHS)
        if not 1 <= self.n_slides <= 20:
            raise ValueError("n_slides must be between 1 and 20")
        if not 1 <= self.notes_per_slide <= 6:
            raise ValueError("notes_per_slide must be between 1 and 6")

    @property
    def target_words(self) -> int:
        return target_words_for(self.length)

    @property
    def n_chunks(self) -> int:
        """More slides need more material: at least 2 chunks per slide."""
        return max(CHUNKS_FOR_LENGTH[self.length], 2 * self.n_slides)

    @property
    def n_math_chunks(self) -> int:
        return MATH_CHUNKS_WHEN_PRESERVING if self.preserve_equations else 0
