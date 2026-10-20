"""
latex_math.py - find LaTeX math and protect it from being split.

protect_math() swaps every math span for a placeholder like ⟦0⟧, so splitting
on blank lines or sentence ends can never cut through an equation.
restore_math() puts the original math back afterwards.

Used by the LaTeX loader AND by the chunker's sentence splitter.
"""

import re

# Display math: \begin{equation}...\end{equation}, \[...\], $$...$$
DISPLAY_MATH = re.compile(
    r"\\begin\{(equation|align|gather|multline|eqnarray)\*?\}.*?\\end\{\1\*?\}"
    r"|\\\[.*?\\\]"
    r"|\$\$.*?\$\$",
    re.DOTALL,
)
# Inline math: $...$
INLINE_MATH = re.compile(r"(?<!\\)\$[^$]+?(?<!\\)\$")


def protect_math(text: str) -> tuple[str, list[str]]:
    """Return (text with placeholders, list of the math spans that were removed)."""
    spans: list[str] = []

    def stash(match):
        spans.append(match.group(0))
        return f"⟦{len(spans) - 1}⟧"

    text = DISPLAY_MATH.sub(stash, text)
    text = INLINE_MATH.sub(stash, text)
    return text, spans


def restore_math(text: str, spans: list[str]) -> str:
    """Put the math spans back in place of their placeholders."""
    return re.sub(r"⟦(\d+)⟧", lambda m: spans[int(m.group(1))], text)


def has_display_math(text: str) -> bool:
    return DISPLAY_MATH.search(text) is not None
