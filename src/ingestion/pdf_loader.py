"""
pdf_loader.py - read a PDF page by page into Blocks.

How it works, per page:
  1. PyMuPDF gives us the page's text blocks in reading order.
  2. Each block is cleaned; noise (page numbers, arXiv stamp) is dropped.
  3. A heading updates the current section name.
  4. A long block (>= PROSE_MIN_WORDS) is a paragraph -> "prose" Block.
  5. Short blocks are collected as "fragments" (equations come out of PDFs as
     many tiny pieces) and grouped into ONE Block - "math" if it looks like math.
  6. Reading stops at the reference list.
"""

from pathlib import Path

import pymupdf

from src import config
from src.ingestion.block import Block
from src.ingestion.block_rules import is_heading, is_noise, is_references_start, looks_like_math
from src.ingestion.text_cleaning import clean_text


def load_pdf(path: str | Path, paper_id: str) -> list[Block]:
    """Read a whole PDF and return its blocks in reading order."""
    blocks: list[Block] = []
    section = "Front matter"

    for page_no, page in enumerate(pymupdf.open(path), start=1):
        page_blocks, section, reached_references = _read_page(page, page_no, paper_id, section)
        blocks += page_blocks
        if reached_references:
            break
    return blocks


def _page_texts(page) -> list[str]:
    """Cleaned text of every text block on the page, without noise."""
    texts = []
    # get_text("blocks") -> (x0, y0, x1, y1, text, block_no, block_type); type 0 = text
    for *_, raw_text, _, block_type in page.get_text("blocks"):
        text = clean_text(raw_text)
        if block_type == 0 and not is_noise(text):
            texts.append(text)
    return texts


def _read_page(page, page_no: int, paper_id: str, section: str) -> tuple[list[Block], str, bool]:
    """Turn one page into blocks.
    Returns (blocks, section name at the end of the page, whether the references started)."""
    blocks: list[Block] = []
    fragments: list[str] = []  # small pieces waiting to be grouped

    for text in _page_texts(page):
        if is_references_start(text):
            blocks += _group_fragments(fragments, paper_id, page_no, section)
            return blocks, section, True

        if is_heading(text):
            blocks += _group_fragments(fragments, paper_id, page_no, section)
            fragments = []
            section = text
        elif len(text.split()) >= config.PROSE_MIN_WORDS:
            blocks += _group_fragments(fragments, paper_id, page_no, section)
            fragments = []
            blocks.append(_make_block(paper_id, page_no, section, "prose", text))
        else:
            fragments.append(text)

    blocks += _group_fragments(fragments, paper_id, page_no, section)
    return blocks, section, False


def _group_fragments(fragments: list[str], paper_id: str, page_no: int, section: str) -> list[Block]:
    """Join consecutive small pieces into one block (or none, if they are just noise)."""
    if not fragments:
        return []
    text = " ".join(fragments)
    if looks_like_math(text):
        return [_make_block(paper_id, page_no, section, "math", text)]
    if len(text.split()) >= config.MIN_FRAGMENT_WORDS:  # drop leftovers like "hidden", "output"
        return [_make_block(paper_id, page_no, section, "prose", text)]
    return []


def _make_block(paper_id: str, page_no: int, section: str, kind: str, text: str) -> Block:
    return Block(paper_id, page_no, f"p{page_no}", section, kind, text)
