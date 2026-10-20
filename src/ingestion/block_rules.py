"""
block_rules.py - rules that decide what a piece of (cleaned) PDF text is:
noise to drop, a section heading, the start of the reference list, or math.
"""

import re

# Characters that suggest a piece of text is (part of) an equation
MATH_SYMBOLS = set("=∑∏∂≈≤≥±×÷→∞√∫∇∈∀∃λσθαβγδεμπφωΣΠ")

UNNUMBERED_HEADINGS = ("Abstract", "Introduction", "Conclusion", "Acknowledgments", "Acknowledgements")


def is_noise(text: str) -> bool:
    """Page numbers, arXiv side stamps, empty blocks."""
    return not text or re.fullmatch(r"\d{1,3}", text) is not None or text.startswith("arXiv:")


def is_heading(text: str) -> bool:
    """Section headings like '2 Distillation' or '4.1 Multichannel vs. Single Channel Models'."""
    if text in UNNUMBERED_HEADINGS:
        return True
    # Number + capitalised title, short, not ending like a sentence (full stops inside are allowed)
    return (
        re.fullmatch(r"\d+(\.\d+)*\.? [A-Z].{0,80}", text) is not None
        and len(text.split()) <= 10
        and not text.endswith((".", ":", "!", "?"))
    )


def is_references_start(text: str) -> bool:
    """The reference list starts here - everything after it is skipped."""
    return re.match(r"^(\d+\.? )?(References|Bibliography)\b", text) is not None


def looks_like_math(text: str) -> bool:
    """Guess whether a group of small PDF fragments is an equation."""
    if any(ch in MATH_SYMBOLS for ch in text):
        return True
    if re.search(r"\(\d{1,2}\)$", text):  # ends with an equation number like "(3)"
        return True
    return bool(re.search(r"\b(exp|log|softmax|arg ?max)\s*\(", text))
