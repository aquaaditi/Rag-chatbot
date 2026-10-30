"""
accessibility.py - is the text easy enough for its audience?

    - long sentences      (> MAX_SENTENCE_WORDS words) are hard to follow when spoken
    - undefined acronyms  "CNN" for the press, without "convolutional neural network (CNN)"
    - readability floor   Flesch score below the audience's minimum (config.READABILITY_FLOOR)

Acronyms and the readability floor only matter for non-expert audiences.
"""

import re

from src import config
from src.provenance.claim import strip_citations

LAY_AUDIENCES = {"policymakers", "press"}
COMMON_ACRONYMS = {"AI", "US", "USA", "UK", "EU", "UN", "TV", "CEO", "OK"}

LATEX_MATH = re.compile(r"\$[^$]+\$")
ACRONYM = re.compile(r"\b([A-Z][A-Z0-9]+)s?\b")  # CNN, CNNs (-> CNN), SST2, BERT
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def plain(text: str) -> str:
    """The words people read: no citations, no LaTeX."""
    return LATEX_MATH.sub("", strip_citations(text))


def long_sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_END.split(plain(text)) if len(s.split()) > config.MAX_SENTENCE_WORDS]


def undefined_acronyms(text: str, whole_talk: str) -> list[str]:
    """Acronyms in `text` that are never spelled out as "... (ACR)" anywhere in the talk."""
    found = dict.fromkeys(ACRONYM.findall(plain(text)))
    return [a for a in found if a not in COMMON_ACRONYMS and f"({a})" not in whole_talk and f"({a}s)" not in whole_talk]


def readability_problem(reading_ease: float, audience: str) -> str | None:
    floor = config.READABILITY_FLOOR.get(audience)
    if floor is not None and reading_ease < floor:
        return f"reading ease {reading_ease:.0f} is below {floor}, the minimum for {audience}"
    return None
