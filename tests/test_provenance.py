"""
Tests for the provenance stage (src/provenance/).

Most tests use a FakeEmbedder (vectors from word counts), so they are fast and
predictable. The last test uses the real model on cases we know are true/false.

Run:  pytest -v
"""

import re

import numpy as np
import pytest

from src import config
from src.chunking import Chunk
from src.provenance import Claim, check_provenance, extract_claims
from src.provenance.claim import strip_citations
from src.provenance.numbers import find_numbers, missing_numbers

VOCAB = ["distillation", "small", "model", "ensemble", "knowledge", "weather", "paris", "errors", "test"]


class FakeEmbedder:
    """Vector = counts of a few words -> sentences sharing words get high cosine similarity."""

    def embed_passages(self, texts):
        rows = []
        for text in texts:
            words = re.findall(r"[a-z]+", text.lower())
            v = np.array([words.count(w) for w in VOCAB], dtype=np.float32) + 1e-6
            rows.append(v / np.linalg.norm(v))
        return np.stack(rows)


def make_chunk(chunk_id, text):
    return Chunk(chunk_id, "P3", 4, "3 Results", text, False, len(text.split()))


SOURCES = [
    make_chunk("P3_p1_c03", "Distillation transfers knowledge from an ensemble to a small model."),
    make_chunk("P3_p4_c01", "The small model made 74 test errors."),
]


# ---------------------------------------------------------------- claim.py


def test_claims_are_split_per_sentence_with_their_citations():
    text = "Distillation works well [P3_p1_c03]. It made 74 errors [P3_p4_c01][P3_p1_c03]. Why does it work?"
    claims = extract_claims(text, "script")
    assert [c.text for c in claims] == ["Distillation works well.", "It made 74 errors."]  # question skipped
    assert claims[1].cited_ids == ["P3_p4_c01", "P3_p1_c03"]


def test_citation_after_the_full_stop_goes_to_the_right_sentence():
    claims = extract_claims("Distillation works well. [P3_p1_c03] The model is small.", "script")
    assert claims[0].cited_ids == ["P3_p1_c03"]
    assert claims[1].cited_ids == []


def test_strip_citations_keeps_normal_brackets():
    assert strip_citations("See Table [2] and [P1_p2_c01, P3_p2_c06].") == "See Table [2] and."


# ---------------------------------------------------------------- numbers.py


def test_numbers_are_normalised_and_math_is_ignored():
    assert find_numbers("15,000 times faster, 80% and $\\frac{1}{N}$") == {"15000", "80"}


def test_wrong_number_is_reported():
    assert missing_numbers("It made 47 errors", "It made 74 errors") == ["47"]


# ---------------------------------------------------------------- support.py + report.py


def test_verdicts_and_metrics():
    claims = [
        Claim("Distillation transfers knowledge from an ensemble to a small model.", ["P3_p1_c03"], "a"),
        Claim("The small model made 47 test errors.", ["P3_p4_c01"], "b"),  # wrong number
        Claim("The weather in Paris is nice.", ["P3_p1_c03"], "c"),  # cited, but not said
        Claim("Distillation makes a small model.", [], "d"),  # no citation
    ]
    report = check_provenance(claims, SOURCES, FakeEmbedder())
    verdicts = [c.verdict for c in report.checks]
    assert verdicts == ["supported", "unsupported", "unsupported", "uncited"]
    assert report.checks[1].missing_numbers == ["47"]
    assert report.checks[3].best_evidence.chunk.chunk_id == "P3_p1_c03"  # suggested provenance
    assert report.citation_coverage == 0.75
    assert report.supported_share == 0.25
    assert report.number_errors == 1
    assert len(report.flagged) == 3


def test_citation_to_unknown_chunk_counts_as_uncited():
    report = check_provenance([Claim("Distillation is small.", ["P9_p9_c99"], "a")], SOURCES, FakeEmbedder())
    assert report.checks[0].verdict == "uncited"
    assert report.checks[0].invalid_ids == ["P9_p9_c99"]


# ---------------------------------------------------------------- real model (calibration cases)


@pytest.mark.skipif(not (config.INDEX_DIR / "chunks.json").exists(), reason="run build_index.py first")
def test_real_model_catches_invented_framing_and_wrong_numbers():
    from src.chunking import load_chunks
    from src.retrieval.embedder import Embedder

    chunks = {c.chunk_id: c for c in load_chunks(config.INDEX_DIR / "chunks.json")}
    sources = [chunks["P2_p1_c02"], chunks["P3_p4_c01"]]
    claims = [
        Claim("fastText can train on more than one billion words in less than ten minutes.", ["P2_p1_c02"], "true"),
        Claim("Government agencies process massive volumes of text like citizen feedback.", ["P2_p1_c02"], "invented"),
        Claim("A small net trained on soft targets made 47 test errors.", ["P3_p4_c01"], "wrong number"),
    ]
    verdicts = [c.verdict for c in check_provenance(claims, sources, Embedder()).checks]
    assert verdicts == ["supported", "unsupported", "unsupported"]
