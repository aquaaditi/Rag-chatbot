"""
Day 2 tests: does ingestion clean text, and does chunking keep math intact?

Run:  pytest -v
"""

from pathlib import Path

import pytest

from src.chunker import chunk_blocks, split_sentences
from src.ingest import Block, clean_text, is_heading, load_paper, load_tex

PAPERS = Path("data/papers")


# ---------------------------------------------------------------- cleaning


def test_ligatures_are_fixed():
    assert clean_text("Classiﬁcation") == "Classification"


def test_words_broken_across_lines_are_joined():
    assert clean_text("a linear classi-\nfier") == "a linear classifier"


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


# ---------------------------------------------------------------- sentences


def test_sentence_split_never_cuts_inline_math():
    text = "We use $x. Y$ here. Then we stop."
    assert split_sentences(text) == ["We use $x. Y$ here.", "Then we stop."]


# ---------------------------------------------------------------- chunking


def make_block(kind, text, loc="p1", section="1 Intro"):
    return Block("T", 1, loc, section, kind, text)


def test_math_block_stays_with_its_lead_in_sentence():
    lead_in = make_block("prose", "word " * 9 + "The loss is:")
    equation = make_block("math", "L = - sum_i y_i log p_i (1)")
    chunks = chunk_blocks([lead_in, equation], max_words=10)  # tiny limit forces a split
    with_eq = [c for c in chunks if "sum_i" in c.text]
    assert len(with_eq) == 1
    assert "The loss is:" in with_eq[0].text  # equation was NOT separated from its lead-in


def test_chunks_never_mix_pages():
    blocks = [make_block("prose", "one two three", loc="p1"), make_block("prose", "four five", loc="p2")]
    chunks = chunk_blocks(blocks)
    assert [c.chunk_id for c in chunks] == ["T_p1_c01", "T_p2_c01"]


def test_latex_equations_survive_intact(tmp_path):
    equation = r"""\begin{equation}
q_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}.

\label{eq:softmax}
\end{equation}"""  # contains a blank line AND a full stop - both are split points normally
    tex = tmp_path / "paper.tex"
    tex.write_text(
        "\\begin{document}\n\\section{Distillation}\n"
        + "We soften the softmax with a temperature. " * 40
        + "\n\nThe softened probabilities are\n"
        + equation
        + "\nwhere $T$ is the temperature.\n\\end{document}",
        encoding="utf-8",
    )
    chunks = chunk_blocks(load_tex(tex, "T"), max_words=60)
    flat_equation = " ".join(equation.split())
    assert sum(flat_equation in c.text for c in chunks) == 1  # whole equation in exactly one chunk
    assert all(c.chunk_id.startswith("T_s1_") for c in chunks)


# ---------------------------------------------------------------- real papers


@pytest.mark.skipif(not (PAPERS / "paper3.pdf").exists(), reason="paper3.pdf not present")
def test_real_pdf_equation_1_is_in_one_chunk():
    chunks = chunk_blocks(load_paper(PAPERS / "paper3.pdf", "P3"))
    eq1 = [c for c in chunks if "qi = exp(zi/T" in c.text]
    assert len(eq1) == 1
    assert "(1)" in eq1[0].text  # equation number stayed with the equation
    assert eq1[0].page == 2 and eq1[0].has_math


@pytest.mark.skipif(not (PAPERS / "paper2.pdf").exists(), reason="paper2.pdf not present")
def test_real_pdf_chunks_are_clean():
    chunks = chunk_blocks(load_paper(PAPERS / "paper2.pdf", "P2"))
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))  # IDs are unique
    full_text = " ".join(c.text for c in chunks)
    assert "ﬁ" not in full_text  # ligatures fixed
    assert "[Agarwal et al.2014]" not in full_text  # reference list dropped
    assert all(c.n_words <= 250 or c.has_math for c in chunks)
