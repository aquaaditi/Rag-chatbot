"""
upload.py - add a paper uploaded in the chat UI to the running chatbot.

    result = add_paper("my_paper.pdf", file_bytes, retriever)
    -> UploadResult(paper_id="P4", n_chunks=31, ...)

The same pipeline as the offline scripts (chunk_papers.py + build_index.py),
for one file: save -> ingestion -> chunking -> safety scan -> retrieval index.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from src import config
from src.chunking import Chunk, chunk_blocks
from src.ingestion import LOADERS, load_paper
from src.retrieval import Retriever
from src.safety import find_injection


@dataclass
class UploadResult:
    paper_id: str
    n_chunks: int
    n_math: int  # chunks with equations
    dropped: list[str] = field(default_factory=list)  # chunk IDs removed by the injection scan


def add_paper(file_name: str, data: bytes, retriever: Retriever) -> UploadResult:
    suffix = Path(file_name).suffix.lower()
    if suffix not in LOADERS:
        raise ValueError(f"Please upload a .pdf or .tex file (got '{file_name}').")
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"The file is larger than {config.MAX_UPLOAD_MB} MB.")

    paper_id = next_paper_id(retriever.chunks)
    config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", file_name)  # never trust a file name from the internet
    path = config.UPLOADS_DIR / f"{paper_id}_{safe_name}"
    path.write_bytes(data)

    chunks = chunk_blocks(load_paper(path, paper_id))
    # Hidden instructions in a paper ("ignore previous instructions...") never reach the LLM
    dropped = [c.chunk_id for c in chunks if find_injection(c.text)]
    chunks = [c for c in chunks if c.chunk_id not in dropped]
    if not chunks:
        raise ValueError("No text could be read from this file (is it a scanned image PDF?).")

    retriever.add(chunks)
    return UploadResult(paper_id, len(chunks), sum(c.has_math for c in chunks), dropped)


def next_paper_id(chunks: list[Chunk]) -> str:
    """P1, P2, P3 exist -> "P4"."""
    numbers = [int(c.paper_id[1:]) for c in chunks if c.paper_id[1:].isdigit()]
    return f"P{max(numbers, default=0) + 1}"
