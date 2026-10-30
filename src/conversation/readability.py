"""
readability.py - how easy is a text to read? (Flesch Reading Ease, via textstat)

    90-100 very easy · 60-70 plain English · 30-50 hard · 0-30 very hard (academic)

Used to MEASURE edits like "make it less technical": the score should go up.
Citations and LaTeX are removed first, so they don't distort the score.
"""

import re

import textstat

from src.provenance.claim import strip_citations
from src.talks import Slide, Talk

LATEX_MATH = re.compile(r"\$[^$]+\$")


def reading_ease(texts: list[str]) -> float:
    plain = " ".join(LATEX_MATH.sub("it", strip_citations(t)) for t in texts if t.strip())
    return round(textstat.flesch_reading_ease(plain), 1) if plain else 0.0


def slide_texts(slide: Slide) -> list[str]:
    return [slide.title] + slide.bullets + slide.speaker_notes


def talk_texts(talk: Talk) -> list[str]:
    return [text for slide in talk.slides for text in slide_texts(slide)] + [talk.script]
