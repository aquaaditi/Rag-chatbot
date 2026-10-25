"""
citations.py - find the [chunk IDs] the LLM cited and check them.

A quick sanity check for now; Day 6 (provenance) will go further and check
that each sentence really is supported by the chunk it cites.
"""

import re

CITATION_GROUP = re.compile(r"\[([^\[\]]+)\]")  # anything inside [...]
CHUNK_ID = re.compile(r"P\d+_[ps]\d+_c\d+")  # e.g. P3_p2_c06


def find_citations(text: str) -> list[str]:
    """All chunk IDs cited in the text, in order of first use.
    Handles [P1_p2_c01], [P1_p2_c01][P3_p2_c06] and [P1_p2_c01, P3_p2_c06]."""
    found: list[str] = []
    for group in CITATION_GROUP.findall(text):
        for chunk_id in CHUNK_ID.findall(group):
            if chunk_id not in found:
                found.append(chunk_id)
    return found


def unknown_citations(cited: list[str], allowed: list[str]) -> list[str]:
    """Cited IDs that were NOT in the sources - a sign the LLM invented a citation."""
    return [c for c in cited if c not in allowed]
