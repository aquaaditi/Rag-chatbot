"""
source_selection.py - choose which chunks go into the prompt.

Shared by every output type (scripts, slide decks...):
  1. the paper's ABSTRACT first - a reliable summary of the whole paper,
  2. the chunks that best match the topic (hybrid retrieval),
  3. optionally, MATH-AWARE boosting: the best-matching chunks that contain
     equations, so a request like "preserve key equations" really has equations
     to preserve (even if their chunks ranked a bit lower).
Duplicates are removed; the order is kept.
"""

from src.chunking import Chunk
from src.retrieval import Retriever


def select_sources(
    retriever: Retriever,
    topic: str,
    k: int,
    paper_id: str | None = None,
    n_math: int = 0,
) -> list[Chunk]:
    abstract = [
        c for c in retriever.chunks
        if c.section == "Abstract" and (paper_id is None or c.paper_id == paper_id)
    ]
    top = [r.chunk for r in retriever.retrieve(topic, k=k, paper_id=paper_id)]
    math = _best_math_chunks(retriever, topic, paper_id, n_math) if n_math else []
    return _unique(abstract + top + math)


def _best_math_chunks(retriever: Retriever, topic: str, paper_id: str | None, n: int) -> list[Chunk]:
    """The n math chunks that rank highest for the topic."""
    ranked = retriever.retrieve(topic, k=len(retriever.chunks), paper_id=paper_id)
    return [r.chunk for r in ranked if r.chunk.has_math][:n]


def _unique(chunks: list[Chunk]) -> list[Chunk]:
    seen: list[Chunk] = []
    for chunk in chunks:
        if chunk not in seen:
            seen.append(chunk)
    return seen
