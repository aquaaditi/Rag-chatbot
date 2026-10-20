"""
block.py - the Block data type: the output of the ingestion stage.

A block is one piece of a paper that must stay together:
  - "prose": a normal paragraph
  - "math":  an equation (the chunker never splits it)
"""

from dataclasses import dataclass


@dataclass
class Block:
    paper_id: str  # e.g. "P3"
    page: int | None  # PDF page number (None for LaTeX, which has no pages)
    loc: str  # location tag used in chunk IDs: "p3" (page 3) or "s2" (section 2)
    section: str  # heading of the section this block is in, e.g. "2 Distillation"
    kind: str  # "prose" or "math"
    text: str
