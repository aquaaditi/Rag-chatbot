"""
Chunking stage:  list of Blocks  ->  list of Chunks (saved as JSON)

    chunk.py      the Chunk data type
    sentences.py  sentence splitting (math-safe) and splitting long blocks
    chunker.py    the chunking rules: size, page/section boundaries, overlap, IDs
    storage.py    save / load chunks as JSON

Other stages only need `chunk_blocks()`, `Chunk`, `save_chunks()` and `load_chunks()`.
"""

from src.chunking.chunk import Chunk
from src.chunking.chunker import chunk_blocks
from src.chunking.storage import load_chunks, save_chunks

__all__ = ["Chunk", "chunk_blocks", "load_chunks", "save_chunks"]
