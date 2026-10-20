"""
text_cleaning.py - fix the usual problems in text extracted from PDFs.
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """Return the text with ligatures, broken words and extra whitespace fixed."""
    # Ligatures: "ﬁ" (one character) -> "fi" (two letters), "ﬂ" -> "fl", ...
    text = unicodedata.normalize("NFKC", text)
    # Words broken across lines: "classi-\nfier" -> "classifier"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Newlines and repeated spaces -> a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()
