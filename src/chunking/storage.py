"""
storage.py - save chunks to JSON and load them back.

The chunking stage writes data/chunks/<paper>.json; the retrieval stage
(Day 3) reads them back with load_chunks() instead of re-reading the PDFs.
"""

import json
from pathlib import Path

from src.chunking.chunk import Chunk


def save_chunks(chunks: list[Chunk], path: str | Path) -> None:
    data = [c.to_dict() for c in chunks]
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_chunks(path: str | Path) -> list[Chunk]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Chunk(**item) for item in data]
