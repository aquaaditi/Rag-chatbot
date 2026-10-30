"""
goals.py - turn an edit request into a MEASURABLE goal, and check it.

The LLM's own "reason" can be wrong (in testing it said "made it less technical"
while readability went DOWN, and "shortened the script" while it got LONGER).
So we measure:

    "less technical" / "simpler" / "dumb down"  -> reading ease must rise by >= 5 points
    "90 seconds" / "2 minutes"                  -> about 150 words per minute (+-25%)
    "shorten" / "shorter" / "more concise"      -> at least 15% fewer words
    "expand" / "longer" / "more detail"         -> at least 15% more words

If the goal is missed, the session retries once and gives the LLM this feedback.
"""

import re

from src import config
from src.conversation.versions import Metrics

SIMPLER = re.compile(r"less technical|simpl|dumb|plain|easier|non-expert|layperson|accessible", re.I)
SHORTER = re.compile(r"shorten|shorter|concise|condense|trim|cut", re.I)
LONGER = re.compile(r"expand|longer|more detail|elaborate", re.I)
DURATION = re.compile(r"(\d+(?:\.\d+)?)\s*(s|sec|secs|seconds|min|mins|minutes)\b", re.I)

MIN_READABILITY_GAIN = 5
LENGTH_TOLERANCE = 0.25
LENGTH_CHANGE = 0.15


def target_words(instruction: str) -> int | None:
    """'shorten the script to 90 seconds' -> 225 words (at 150 words per minute)."""
    match = DURATION.search(instruction)
    if not match:
        return None
    amount, unit = float(match.group(1)), match.group(2).lower()
    seconds = amount * 60 if unit.startswith("min") else amount
    return round(seconds / 60 * config.SPEAKING_WORDS_PER_MINUTE)


def check_goal(instruction: str, before: Metrics, after: Metrics) -> str | None:
    """None if the edit reached its measurable goal (or has none), else feedback for a retry."""
    problems = []
    if SIMPLER.search(instruction) and after.reading_ease < before.reading_ease + MIN_READABILITY_GAIN:
        problems.append(
            f"Readability did not improve enough (Flesch {before.reading_ease:.0f} -> {after.reading_ease:.0f}; "
            f"higher = easier). Use much shorter sentences, everyday words, fewer long technical terms."
        )

    target = target_words(instruction)
    if target and abs(after.n_words - target) > LENGTH_TOLERANCE * target:
        problems.append(f"The text has {after.n_words} words; the request needs about {target} words.")
    elif not target and SHORTER.search(instruction) and after.n_words > (1 - LENGTH_CHANGE) * before.n_words:
        problems.append(f"It was not shortened: {before.n_words} -> {after.n_words} words. Cut it by at least 25%.")
    elif not target and LONGER.search(instruction) and after.n_words < (1 + LENGTH_CHANGE) * before.n_words:
        problems.append(f"It was not expanded: {before.n_words} -> {after.n_words} words. Add at least 25%.")

    return " ".join(problems) or None
