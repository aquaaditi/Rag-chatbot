"""
numbers.py - EXACT-MATCH check for numbers.

Embeddings are bad at numbers: "74 errors" and "47 errors" look almost the same
to them. So every number in a claim must also appear, exactly, in the source.
"""

import re

NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
LATEX_MATH = re.compile(r"\$[^$]+\$")  # numbers inside equations ("\frac{1}{N}") are not checked


def find_numbers(text: str) -> set[str]:
    """Numbers in the text, normalised: '15,000' -> '15000'. Equations are ignored."""
    text = LATEX_MATH.sub(" ", text)
    return {n.replace(",", "") for n in NUMBER.findall(text)}


def missing_numbers(claim_text: str, source_text: str) -> list[str]:
    """Numbers in the claim that do not appear in the source text."""
    return sorted(find_numbers(claim_text) - find_numbers(source_text))
