"""
chunker.py - Day 2: group blocks into chunks that are the right size for retrieval.

Rules:
  1. A chunk never mixes two pages (PDF) or two sections - so every chunk has
     one clear location to cite.
  2. A "math" block is NEVER split, and it stays in the same chunk as the
     sentence that introduces it, even if that makes the chunk a bit too long.
  3. A long paragraph is split at sentence ends (never inside $...$ math).
  4. Neighbouring chunks overlap by one sentence, so an idea that sits on a
     chunk boundary is not lost.

Every chunk gets an ID like "P1_p3_c02" = paper 1, page 3, chunk 2 on that page.
"""

import re
from dataclasses import asdict, dataclass

from src.ingest import Block, protect_math, restore_math

MAX_WORDS = 250  # about 330 tokens
OVERLAP_SENTENCES = 1
MAX_OVERLAP_WORDS = 40  # a "sentence" longer than this (e.g. a table) is not repeated


@dataclass
class Chunk:
    chunk_id: str
    paper_id: str
    page: int | None
    section: str
    text: str
    has_math: bool
    n_words: int

    def to_dict(self) -> dict:
        return asdict(self)


def split_sentences(text: str) -> list[str]:
    """Split at '. ', '! ', '? ' - but never inside LaTeX math."""
    protected, spans = protect_math(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", protected)
    return [restore_math(p, spans) for p in parts if p.strip()]


def split_long_block(block: Block, max_words: int) -> list[Block]:
    """Break a too-long prose block into pieces of whole sentences."""
    if block.kind == "math" or len(block.text.split()) <= max_words:
        return [block]

    # Sentences longer than max_words (e.g. a table with no full stops) are cut into word windows
    sentences = []
    for sentence in split_sentences(block.text):
        words = sentence.split()
        sentences += [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]

    pieces, current = [], []
    for sentence in sentences:
        if current and len(" ".join(current + [sentence]).split()) > max_words:
            pieces.append(" ".join(current))
            current = []
        current.append(sentence)
    if current:
        pieces.append(" ".join(current))
    return [Block(block.paper_id, block.page, block.loc, block.section, "prose", p) for p in pieces]


def chunk_blocks(
    blocks: list[Block], max_words: int = MAX_WORDS, overlap_sentences: int = OVERLAP_SENTENCES
) -> list[Chunk]:
    chunks: list[Chunk] = []
    count_per_loc: dict[str, int] = {}

    current: list[Block] = []
    overlap_text = ""

    def emit():
        nonlocal overlap_text
        if not current:
            return
        first = current[0]
        count_per_loc[first.loc] = count_per_loc.get(first.loc, 0) + 1
        text = " ".join(([overlap_text] if overlap_text else []) + [b.text for b in current])
        chunks.append(
            Chunk(
                chunk_id=f"{first.paper_id}_{first.loc}_c{count_per_loc[first.loc]:02d}",
                paper_id=first.paper_id,
                page=first.page,
                section=first.section,
                text=text,
                has_math=any(b.kind == "math" for b in current),
                n_words=len(text.split()),
            )
        )
        # Remember the last sentence(s) of the last prose block to start the next chunk
        last_prose = next((b for b in reversed(current) if b.kind == "prose"), None)
        overlap_text = (
            " ".join(split_sentences(last_prose.text)[-overlap_sentences:])
            if last_prose and overlap_sentences
            else ""
        )
        if len(overlap_text.split()) > MAX_OVERLAP_WORDS:
            overlap_text = ""
        current.clear()

    for big_block in blocks:
        for block in split_long_block(big_block, max_words):
            if current:
                new_place = block.loc != current[-1].loc or block.section != current[-1].section
                too_big = sum(len(b.text.split()) for b in current) + len(block.text.split()) > max_words
                if new_place:
                    emit()
                    overlap_text = ""  # don't carry text across pages/sections
                elif too_big and block.kind != "math":  # math stays with its lead-in sentence
                    emit()
            current.append(block)
    emit()
    return chunks
