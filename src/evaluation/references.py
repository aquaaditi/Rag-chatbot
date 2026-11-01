"""
references.py - the HUMAN-written reference scripts that generated scripts are compared with.

    data/references/paper1_90s.txt  ->  reference for P1 (chunk_papers.py numbers papers in file order)

They were written by hand for a general audience, so they are closest to the
plain-English (policymakers / press) outputs.
"""

from pathlib import Path


def load_reference(paper_id: str, length: str, directory: Path) -> str | None:
    """The reference script, or None if there is none for this paper and length."""
    path = directory / f"paper{paper_id.removeprefix('P')}_{length}.txt"
    return path.read_text(encoding="utf-8").strip() if path.exists() else None
