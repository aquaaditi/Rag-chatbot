"""
tex_loader.py - read a LaTeX source file into Blocks.

LaTeX is better than PDF for math: equations stay exactly as the authors wrote
them. Paragraphs are separated by blank lines; math is protected first so a
blank line or full stop inside an equation never splits it.
"""

import re
from pathlib import Path

from src.ingestion.block import Block
from src.ingestion.latex_math import has_display_math, protect_math, restore_math
from src.ingestion.text_cleaning import clean_text

SECTION_COMMAND = re.compile(r"\s*\\(sub)*section\*?\{(.+?)\}")


def load_tex(path: str | Path, paper_id: str) -> list[Block]:
    """Read a .tex file and return its blocks (one per paragraph)."""
    body, math_spans = protect_math(_read_body(path))

    blocks: list[Block] = []
    section, section_no = "Front matter", 0
    for paragraph in re.split(r"\n\s*\n", body):  # paragraphs are separated by blank lines
        heading = SECTION_COMMAND.match(paragraph)
        if heading:
            if not heading.group(1):  # \section (not \subsection) starts a new location
                section_no += 1
            section = heading.group(2)
            paragraph = paragraph[heading.end():]

        text = clean_text(restore_math(paragraph, math_spans))
        if text:
            kind = "math" if has_display_math(text) else "prose"
            blocks.append(Block(paper_id, None, f"s{section_no}", section, kind, text))
    return blocks


def _read_body(path: str | Path) -> str:
    """The document body without comments, preamble or bibliography."""
    source = Path(path).read_text(encoding="utf-8")
    source = re.sub(r"(?<!\\)%.*", "", source)  # remove LaTeX comments
    if r"\begin{document}" in source:
        source = source.split(r"\begin{document}", 1)[1]
    return re.split(r"\\end\{document\}|\\begin\{thebibliography\}|\\bibliography\{", source)[0]
