"""
chunk.py - the Chunk data type: the output of the chunking stage.

A chunk is the unit that gets embedded, retrieved and cited.
Its ID, e.g. "P3_p2_c06", means paper 3, page 2, 6th chunk on that page.
"""

from dataclasses import asdict, dataclass


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
