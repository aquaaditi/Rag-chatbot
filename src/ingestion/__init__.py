"""
Ingestion stage:  paper file (.pdf / .tex)  ->  list of Blocks

    block.py          the Block data type
    text_cleaning.py  fix ligatures, broken words, whitespace
    block_rules.py    is this text noise / a heading / references / math?
    latex_math.py     protect LaTeX math from being split
    pdf_loader.py     PDF  -> Blocks
    tex_loader.py     .tex -> Blocks

Other stages only need `load_paper()` and `Block`.
"""

from pathlib import Path

from src.ingestion.block import Block
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.tex_loader import load_tex

LOADERS = {".pdf": load_pdf, ".tex": load_tex}


def load_paper(path: str | Path, paper_id: str) -> list[Block]:
    """Pick the right loader from the file extension."""
    suffix = Path(path).suffix.lower()
    if suffix not in LOADERS:
        raise ValueError(f"Unsupported file type: {suffix} (use .pdf or .tex)")
    return LOADERS[suffix](path, paper_id)


__all__ = ["Block", "load_paper", "load_pdf", "load_tex"]
