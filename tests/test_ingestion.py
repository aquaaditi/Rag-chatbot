"""
Tests for the ingestion stage (src/ingestion/): cleaning, rules, loaders.

Run:  pytest -v
"""

from pathlib import Path

import pytest

from src.ingestion import load_paper, load_tex
from src.ingestion.block_rules import is_heading, looks_like_math
from src.ingestion.text_cleaning import clean_text

PAPERS = Path("data/papers")


# ---------------------------------------------------------------- text_cleaning.py


def test_ligatures_are_fixed():
    assert clean_text("Classiﬁcation") == "Classification"


def test_words_broken_across_lines_are_joined():
    assert clean_text("a linear classi-\nfier") == "a linear classifier"


# ---------------------------------------------------------------- block_rules.py


@pytest.mark.parametrize(
    "text, expected",
    [
        ("2 Distillation", True),
        ("2.1 Hierarchical softmax", True),
        ("4.1 Multichannel vs. Single Channel Models", True),
        ("2 20 10662 18765", False),  # a table row
        ("3 It was a good result.", False),  # a sentence, not a heading
    ],
)
def test_heading_detection(text, expected):
    assert is_heading(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [("qi = exp(zi/T ) P j exp(zj/T ) (1)", True), ("hidden output", False)],
)
def test_math_detection(text, expected):
    assert looks_like_math(text) == expected


# ---------------------------------------------------------------- tex_loader.py


def test_latex_section_and_math_kind(tmp_path):
    tex = tmp_path / "paper.tex"
    tex.write_text(
        "\\begin{document}\n\\section{Method}\nWe use a softmax.\n\n"
        "\\[ q_i = e^{z_i} \\]\n\\end{document}",
        encoding="utf-8",
    )
    blocks = load_tex(tex, "T")
    assert [b.kind for b in blocks] == ["prose", "math"]
    assert all(b.section == "Method" and b.loc == "s1" for b in blocks)


# ---------------------------------------------------------------- pdf_loader.py (real paper)


@pytest.mark.skipif(not (PAPERS / "paper2.pdf").exists(), reason="paper2.pdf not present")
def test_real_pdf_is_clean():
    text = " ".join(b.text for b in load_paper(PAPERS / "paper2.pdf", "P2"))
    assert "ﬁ" not in text  # ligatures fixed
    assert "[Agarwal et al.2014]" not in text  # reference list dropped
    assert "arXiv:" not in text  # side stamp dropped


def test_unsupported_file_type_is_rejected():
    with pytest.raises(ValueError):
        load_paper("notes.docx", "X")
