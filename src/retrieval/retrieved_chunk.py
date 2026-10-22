"""
retrieved_chunk.py - the RetrievedChunk data type: the output of the retrieval stage.

A chunk plus how well it matched the question. The generation stage (Day 4)
puts these chunks into the prompt and cites them by chunk_id.
"""

from dataclasses import dataclass

from src.chunking import Chunk


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float  # higher = more relevant (the scale depends on the search method)
    rank: int  # 1 = best match
