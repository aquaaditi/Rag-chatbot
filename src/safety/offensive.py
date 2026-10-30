"""
offensive.py - find offensive words (profanity, insults, slurs).

Uses the better-profanity word list. A word list is blunt, so two exceptions
(both found by running it on our own papers - see NOTES.md Day 8):

1. Words that are normal in research text ("kill the process", "sexual
   harassment detection") are always allowed.
2. Words that also appear in the SOURCES are allowed: the list flags author
   surnames such as "Wang" and "Dong", and a paper about sentiment may quote
   "stupid" from a movie review. Blocking them would block the paper itself
   (and people's names - that would be the discriminatory part).
"""

import re

from better_profanity import profanity

profanity.load_censor_words()

ALWAYS_ALLOWED = {"kill", "killed", "kills", "sexual", "hell", "screw", "screws"}
WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def words_in(text: str) -> set[str]:
    """Lower-case words of a text, e.g. the vocabulary of the sources."""
    return {w.lower() for w in WORD.findall(text)}


def find_offensive(text: str, allowed: set[str] = frozenset()) -> list[str]:
    """Offensive words in `text`, except ALWAYS_ALLOWED and the `allowed` words (lower case)."""
    found = {
        word for word in WORD.findall(text)
        if word.lower() not in ALWAYS_ALLOWED and word.lower() not in allowed and profanity.contains_profanity(word)
    }
    return sorted(found)
