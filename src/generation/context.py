"""
context.py - turn retrieved chunks into the "SOURCES" block of the prompt.

Each chunk is shown with its ID and location, so the LLM can cite it:

    [P3_p2_c06] (paper P3, page 2, section "2 Distillation")
    Neural networks typically produce class probabilities by ...
"""

from src.chunking import Chunk


def format_sources(chunks: list[Chunk]) -> str:
    return "\n\n".join(_format_one(chunk) for chunk in chunks)


def _format_one(chunk: Chunk) -> str:
    where = f"page {chunk.page}" if chunk.page else "no page numbers"
    return f'[{chunk.chunk_id}] (paper {chunk.paper_id}, {where}, section "{chunk.section}")\n{chunk.text}'
