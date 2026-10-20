"""
sentences.py - split text into sentences, and long blocks into smaller ones.
LaTeX math is protected, so a full stop inside $...$ never causes a split.
"""

import re

from src.ingestion.block import Block
from src.ingestion.latex_math import protect_math, restore_math


def split_sentences(text: str) -> list[str]:
    """Split at '. ', '! ', '? ' - but never inside LaTeX math."""
    protected, spans = protect_math(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", protected)
    return [restore_math(p, spans) for p in parts if p.strip()]


def split_long_block(block: Block, max_words: int) -> list[Block]:
    """Break a too-long prose block into pieces made of whole sentences.
    Math blocks and short blocks are returned unchanged."""
    if block.kind == "math" or len(block.text.split()) <= max_words:
        return [block]

    pieces = _pack_sentences(_sentences_no_longer_than(block.text, max_words), max_words)
    return [Block(block.paper_id, block.page, block.loc, block.section, "prose", p) for p in pieces]


def _sentences_no_longer_than(text: str, max_words: int) -> list[str]:
    """Sentences, where any sentence over max_words (e.g. a table with no full
    stops) is cut into word windows."""
    result = []
    for sentence in split_sentences(text):
        words = sentence.split()
        result += [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]
    return result


def _pack_sentences(sentences: list[str], max_words: int) -> list[str]:
    """Greedily join sentences into pieces of at most max_words."""
    pieces, current = [], []
    for sentence in sentences:
        if current and len(" ".join(current + [sentence]).split()) > max_words:
            pieces.append(" ".join(current))
            current = []
        current.append(sentence)
    if current:
        pieces.append(" ".join(current))
    return pieces
