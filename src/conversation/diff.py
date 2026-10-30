"""
diff.py - the DELTA: what exactly changed between two versions.

Field by field (title, each bullet, each equation, each note, the script),
and word by word inside a field:

    word_diff("uses the cross-entropy gradient", "uses a simple learning signal")
    -> "uses ~~the cross-entropy gradient~~ **a simple learning signal**"
"""

import difflib
from dataclasses import dataclass

from src.talks import Slide, Talk


@dataclass
class FieldChange:
    where: str  # e.g. "slide 2 · bullet 1"
    old: str  # "" if the field was added
    new: str  # "" if the field was removed


def word_diff(old: str, new: str) -> str:
    """Markdown: ~~removed words~~ and **added words**, unchanged words as they are."""
    old_words, new_words = old.split(), new.split()
    parts = []
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(a=old_words, b=new_words).get_opcodes():
        if op == "equal":
            parts.append(" ".join(old_words[a1:a2]))
            continue
        if a2 > a1:  # replace or delete
            parts.append(f"~~{' '.join(old_words[a1:a2])}~~")
        if b2 > b1:  # replace or insert
            parts.append(f"**{' '.join(new_words[b1:b2])}**")
    return " ".join(parts)


def slide_changes(old: Slide, new: Slide, number: int) -> list[FieldChange]:
    changes = _compare(f"slide {number} · title", [old.title], [new.title])
    changes += _compare(f"slide {number} · bullet", old.bullets, new.bullets)
    changes += _compare(f"slide {number} · equation", old.equations, new.equations)
    changes += _compare(f"slide {number} · note", old.speaker_notes, new.speaker_notes)
    return changes


def talk_changes(old: Talk, new: Talk) -> list[FieldChange]:
    changes = _compare("talk title", [old.title], [new.title])
    for number, (old_slide, new_slide) in enumerate(zip(old.slides, new.slides), start=1):
        changes += slide_changes(old_slide, new_slide, number)
    changes += _compare("script", [old.script], [new.script])
    return changes


def talk_fields(talk: Talk) -> list[tuple[str, str]]:
    """Every text field of a talk with its name, e.g. ("slide 2 · bullet 1", "...").
    = the changes from an empty talk, so the names match the diffs (used by the safety checks)."""
    empty_slides = [Slide(title="", bullets=[], equations=[], speaker_notes=[]) for _ in talk.slides]
    return [(c.where, c.new) for c in talk_changes(Talk(title="", slides=empty_slides, script=""), talk)]


def _compare(where: str, old_items: list[str], new_items: list[str]) -> list[FieldChange]:
    """Compare two lists item by item; a missing item counts as "" (added / removed)."""
    numbered = len(old_items) > 1 or len(new_items) > 1 or "bullet" in where or "note" in where or "equation" in where
    changes = []
    for i in range(max(len(old_items), len(new_items))):
        old = old_items[i] if i < len(old_items) else ""
        new = new_items[i] if i < len(new_items) else ""
        if old.strip() != new.strip():
            changes.append(FieldChange(f"{where} {i + 1}" if numbered else where, old, new))
    return changes
