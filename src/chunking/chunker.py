"""
chunker.py - group Blocks into Chunks of the right size for retrieval.

Rules:
  1. A chunk never mixes two pages (PDF) or two sections, so every chunk has
     one clear location to cite.
  2. A "math" block is NEVER split, and it stays in the same chunk as the
     sentence that introduces it, even if that makes the chunk a bit too long.
  3. A long paragraph is split at sentence ends (see sentences.py).
  4. Neighbouring chunks overlap by one sentence, so an idea that sits on a
     chunk boundary is not lost.
"""

from src import config
from src.chunking.chunk import Chunk
from src.chunking.sentences import split_long_block, split_sentences
from src.ingestion.block import Block


def chunk_blocks(
    blocks: list[Block],
    max_words: int = config.MAX_CHUNK_WORDS,
    overlap_sentences: int = config.OVERLAP_SENTENCES,
) -> list[Chunk]:
    """Turn a paper's blocks into chunks, in order."""
    chunks: list[Chunk] = []
    chunks_per_location: dict[str, int] = {}  # numbering restarts on every page/section
    current: list[Block] = []  # blocks of the chunk being built
    overlap = ""  # text carried over from the previous chunk

    for block in _blocks_split_to_size(blocks, max_words):
        if current and _is_new_location(current, block):
            chunks.append(_build_chunk(current, overlap, chunks_per_location))
            current, overlap = [], ""  # no overlap across pages/sections
        elif current and _would_overflow(current, block, max_words) and block.kind != "math":
            chunks.append(_build_chunk(current, overlap, chunks_per_location))
            current, overlap = [], _overlap_for_next_chunk(current, overlap_sentences)
        current.append(block)

    if current:
        chunks.append(_build_chunk(current, overlap, chunks_per_location))
    return chunks


def _blocks_split_to_size(blocks: list[Block], max_words: int) -> list[Block]:
    return [piece for block in blocks for piece in split_long_block(block, max_words)]


def _is_new_location(current: list[Block], block: Block) -> bool:
    return block.loc != current[-1].loc or block.section != current[-1].section


def _would_overflow(current: list[Block], block: Block, max_words: int) -> bool:
    return _word_count(current) + len(block.text.split()) > max_words


def _word_count(blocks: list[Block]) -> int:
    return sum(len(b.text.split()) for b in blocks)


def _build_chunk(blocks: list[Block], overlap: str, chunks_per_location: dict[str, int]) -> Chunk:
    """Create the Chunk for these blocks and give it the next ID for its location."""
    first = blocks[0]
    chunks_per_location[first.loc] = chunks_per_location.get(first.loc, 0) + 1
    text = " ".join(([overlap] if overlap else []) + [b.text for b in blocks])
    return Chunk(
        chunk_id=f"{first.paper_id}_{first.loc}_c{chunks_per_location[first.loc]:02d}",
        paper_id=first.paper_id,
        page=first.page,
        section=first.section,
        text=text,
        has_math=any(b.kind == "math" for b in blocks),
        n_words=len(text.split()),
    )


def _overlap_for_next_chunk(blocks: list[Block], overlap_sentences: int) -> str:
    """The last sentence(s) of the last prose block - unless that is too long (e.g. a table)."""
    last_prose = next((b for b in reversed(blocks) if b.kind == "prose"), None)
    if not last_prose or not overlap_sentences:
        return ""
    overlap = " ".join(split_sentences(last_prose.text)[-overlap_sentences:])
    return overlap if len(overlap.split()) <= config.MAX_OVERLAP_WORDS else ""
