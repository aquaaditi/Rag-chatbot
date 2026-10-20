"""
ingest.py - Day 2: read a paper (PDF or LaTeX) into clean "blocks".

A block is one piece of the paper that should stay together:
  - "prose": a normal paragraph
  - "math":  an equation (never split later!)

Every block remembers WHERE it came from (page number + section heading).
That location is what later lets the chatbot cite its sources.
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pymupdf

# A PDF block with at least this many words is treated as a normal paragraph.
# Shorter blocks are usually pieces of equations, figure labels or table cells.
PROSE_MIN_WORDS = 12

# Characters that suggest a block is (part of) an equation
MATH_SYMBOLS = set("=∑∏∂≈≤≥±×÷→∞√∫∇∈∀∃λσθαβγδεμπφωΣΠ")

# Display-math in LaTeX: \begin{equation}...\end{equation}, \[...\], $$...$$
LATEX_DISPLAY_MATH = re.compile(
    r"\\begin\{(equation|align|gather|multline|eqnarray)\*?\}.*?\\end\{\1\*?\}"
    r"|\\\[.*?\\\]"
    r"|\$\$.*?\$\$",
    re.DOTALL,
)
# Inline math in LaTeX: $...$
LATEX_INLINE_MATH = re.compile(r"(?<!\\)\$[^$]+?(?<!\\)\$")


@dataclass
class Block:
    paper_id: str
    page: int | None  # PDF page number (None for LaTeX, which has no pages)
    loc: str  # location tag used in chunk IDs: "p3" (page 3) or "s2" (section 2)
    section: str  # heading of the section this block is in, e.g. "2 Distillation"
    kind: str  # "prose" or "math"
    text: str


# ---------------------------------------------------------------- cleaning


def clean_text(text: str) -> str:
    """Fix the usual PDF text problems."""
    # Ligatures: "ﬁ" (one character) -> "fi" (two letters), "ﬂ" -> "fl", ...
    text = unicodedata.normalize("NFKC", text)
    # Words broken across lines: "classi-\nfier" -> "classifier"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Newlines and repeated spaces -> a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def looks_like_math(text: str) -> bool:
    """Guess whether a group of small PDF fragments is an equation."""
    if any(ch in MATH_SYMBOLS for ch in text):
        return True
    if re.search(r"\(\d{1,2}\)$", text):  # ends with an equation number like "(3)"
        return True
    return bool(re.search(r"\b(exp|log|softmax|arg ?max)\s*\(", text))


def is_heading(text: str) -> bool:
    """Numbered section headings like '2 Distillation' or '2.1 Hierarchical softmax'."""
    if text in ("Abstract", "Introduction", "Conclusion", "Acknowledgments", "Acknowledgements"):
        return True
    # Number + capitalised title, short, not ending like a sentence.
    # (Full stops inside are allowed: "4.1 Multichannel vs. Single Channel Models")
    return (
        re.fullmatch(r"\d+(\.\d+)*\.? [A-Z].{0,80}", text) is not None
        and len(text.split()) <= 10
        and not text.endswith((".", ":", "!", "?"))
    )


def is_noise(text: str) -> bool:
    """Page numbers, arXiv side stamps, empty blocks."""
    return (
        not text
        or re.fullmatch(r"\d{1,3}", text) is not None
        or text.startswith("arXiv:")
    )


def is_references_start(text: str) -> bool:
    return re.match(r"^(\d+\.? )?(References|Bibliography)\b", text) is not None


# ---------------------------------------------------------------- PDF


def load_pdf(path: str | Path, paper_id: str) -> list[Block]:
    """Read a PDF page by page and return its blocks in reading order."""
    doc = pymupdf.open(path)
    blocks: list[Block] = []
    section = "Front matter"

    for page_no, page in enumerate(doc, start=1):
        fragments: list[str] = []  # small pieces waiting to be grouped

        def flush_fragments():
            """Turn the collected small pieces into one block."""
            if not fragments:
                return
            text = " ".join(fragments)
            fragments.clear()
            if looks_like_math(text):
                blocks.append(Block(paper_id, page_no, f"p{page_no}", section, "math", text))
            elif len(text.split()) >= 4:  # drop tiny leftovers like "hidden", "output"
                blocks.append(Block(paper_id, page_no, f"p{page_no}", section, "prose", text))

        # get_text("blocks") -> (x0, y0, x1, y1, text, block_no, block_type); type 0 = text
        for *_, raw_text, _, block_type in page.get_text("blocks"):
            if block_type != 0:
                continue
            text = clean_text(raw_text)
            if is_noise(text):
                continue
            if is_references_start(text):
                flush_fragments()
                return blocks  # stop: the reference list is not useful for retrieval
            if is_heading(text):
                flush_fragments()
                section = text
            elif len(text.split()) >= PROSE_MIN_WORDS:
                flush_fragments()
                blocks.append(Block(paper_id, page_no, f"p{page_no}", section, "prose", text))
            else:
                fragments.append(text)
        flush_fragments()

    return blocks


# ---------------------------------------------------------------- LaTeX


def protect_math(text: str) -> tuple[str, list[str]]:
    """Replace every math span with a placeholder like ⟦0⟧ so later
    splitting (on blank lines or sentence ends) can never cut through math."""
    spans: list[str] = []

    def stash(match):
        spans.append(match.group(0))
        return f"⟦{len(spans) - 1}⟧"

    text = LATEX_DISPLAY_MATH.sub(stash, text)
    text = LATEX_INLINE_MATH.sub(stash, text)
    return text, spans


def restore_math(text: str, spans: list[str]) -> str:
    return re.sub(r"⟦(\d+)⟧", lambda m: spans[int(m.group(1))], text)


def load_tex(path: str | Path, paper_id: str) -> list[Block]:
    """Read a LaTeX source file. Math stays exactly as written in LaTeX."""
    source = Path(path).read_text(encoding="utf-8")
    source = re.sub(r"(?<!\\)%.*", "", source)  # remove LaTeX comments

    # Keep only the document body, without the bibliography
    if r"\begin{document}" in source:
        source = source.split(r"\begin{document}", 1)[1]
    source = re.split(r"\\end\{document\}|\\begin\{thebibliography\}|\\bibliography\{", source)[0]

    body, spans = protect_math(source)

    blocks: list[Block] = []
    section, section_no = "Front matter", 0
    for para in re.split(r"\n\s*\n", body):  # paragraphs are separated by blank lines
        heading = re.match(r"\s*\\(sub)*section\*?\{(.+?)\}", para)
        if heading:
            if not heading.group(1):  # \section (not \subsection) starts a new location
                section_no += 1
            section = heading.group(2)
            para = para[heading.end():]
        text = clean_text(restore_math(para, spans))
        if not text:
            continue
        kind = "math" if LATEX_DISPLAY_MATH.search(text) else "prose"
        blocks.append(Block(paper_id, None, f"s{section_no}", section, kind, text))
    return blocks


def load_paper(path: str | Path, paper_id: str) -> list[Block]:
    """Pick the right loader from the file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path, paper_id)
    if suffix == ".tex":
        return load_tex(path, paper_id)
    raise ValueError(f"Unsupported file type: {suffix} (use .pdf or .tex)")
