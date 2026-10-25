"""
options.py - the choices a user can make: audience, length and style.

Each choice has a short description that is pasted into the prompt, so the
LLM knows exactly what "policymakers" or "plain-English" means for us.
"""

from dataclasses import dataclass

from src import config

AUDIENCES = {
    "policymakers": (
        "policymakers and government officials: smart but not technical; they care about "
        "real-world impact, costs, risks and decisions, not about how the maths works"
    ),
    "grad_students": (
        "graduate students in machine learning: they know the basics and want the method, "
        "the key equations and the experimental evidence"
    ),
    "press": (
        "journalists and the general public: no technical background; they need a clear "
        "story, a concrete example and why it matters"
    ),
}

STYLES = {
    "technical": "technical: precise terms, mention the method and equations where they help",
    "plain_english": (
        "plain-English: short sentences, everyday words, explain or avoid every technical term"
    ),
    "press_release": (
        "press release: start with the headline finding, then context, then why it matters; "
        "confident and newsworthy, but never exaggerate beyond the sources"
    ),
}

# Spoken length in seconds
LENGTHS = {"30s": 30, "90s": 90, "5min": 300}

# How many chunks to retrieve: a longer script needs more material
CHUNKS_FOR_LENGTH = {"30s": 4, "90s": 6, "5min": 10}


@dataclass
class ScriptRequest:
    topic: str  # what the script is about, e.g. "the main idea and results of the paper"
    audience: str = "grad_students"
    length: str = "90s"
    style: str = "plain_english"
    paper_id: str | None = None  # e.g. "P3" to use only one paper
    change_instruction: str = ""  # used later for edits like "make #2 less technical"

    def __post_init__(self):
        _check_choice("audience", self.audience, AUDIENCES)
        _check_choice("length", self.length, LENGTHS)
        _check_choice("style", self.style, STYLES)

    @property
    def target_words(self) -> int:
        """90s at 150 words per minute -> 225 words."""
        return round(LENGTHS[self.length] / 60 * config.SPEAKING_WORDS_PER_MINUTE)

    @property
    def n_chunks(self) -> int:
        return CHUNKS_FOR_LENGTH[self.length]


def _check_choice(name: str, value: str, allowed: dict) -> None:
    if value not in allowed:
        raise ValueError(f"Unknown {name} '{value}'. Choose one of: {', '.join(allowed)}")
