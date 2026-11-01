"""
Tests for the evaluation stage (src/evaluation/) - fake LLM, fake retriever and a fake
BERTScore, so they run offline in about a second.

Run:  pytest -v
"""

import json

import pytest

from src.evaluation import EvalCase, Evaluator, default_cases
from src.evaluation.export import results_markdown
from src.evaluation.overlap import rouge
from src.evaluation.references import load_reference
from src.evaluation.summary import audience_table, retrieval_table
from test_conversation import FakeRetriever

SCRIPT = "Distillation trains a small model with soft targets [P3_p2_c06]. It is great [P9_p1_c01]."


class CountingLLM:
    def __init__(self):
        self.calls = 0

    def __call__(self, prompt, system_prompt=""):
        self.calls += 1
        return SCRIPT


def fake_bertscore(candidates, references):
    return [0.5] * len(candidates)


@pytest.fixture
def references(tmp_path):
    directory = tmp_path / "references"
    directory.mkdir()
    (directory / "paper3_90s.txt").write_text("Distillation trains a small model with soft targets.", encoding="utf-8")
    return directory


# ---------------------------------------------------------------- overlap.py / references.py / cases.py


def test_rouge_ignores_citations_and_rewards_shared_words():
    assert rouge("Soft targets help [P3_p2_c06].", "Soft targets help.") == {"rouge1": 1.0, "rouge2": 1.0, "rougeL": 1.0}
    assert rouge("Cats sleep.", "Soft targets help.")["rouge1"] == 0.0


def test_reference_file_matches_paper_id(references):
    assert load_reference("P3", "90s", references).startswith("Distillation")
    assert load_reference("P1", "90s", references) is None


def test_default_cases_cover_both_experiments_without_duplicates():
    cases = default_cases(["P1", "P2"])
    assert len(cases) == 10 and len({c.case_id for c in cases}) == 10
    assert EvalCase("P1", "policymakers", "hybrid") in cases  # shared by both experiments
    assert EvalCase("P1", "press").to_request().style == "press_release"


# ---------------------------------------------------------------- runner.py


def test_evaluator_measures_and_caches_scripts(tmp_path, references):
    llm = CountingLLM()
    cases = [EvalCase("P3", "policymakers", "hybrid"), EvalCase("P3", "policymakers", "bm25"), EvalCase("P1", "press")]
    evaluator = Evaluator(FakeRetriever(), tmp_path / "runs", llm=llm, bertscore=fake_bertscore,
                          references_dir=references)
    rows = evaluator.evaluate(cases)

    assert llm.calls == 3 and evaluator.n_generated == 3
    row = rows[0]
    assert row.words == 11 and row.target_words == 225  # citations are not words
    assert row.invented_citations == 1  # P9_p1_c01 was never given to the model
    assert row.citation_coverage == 0.5  # an invented ID is not a valid citation
    assert row.rouge1 is not None and row.bertscore == 0.5
    assert rows[2].rouge1 is None and rows[2].bertscore is None  # no reference for P1
    saved = json.loads((tmp_path / "runs" / f"{cases[0].case_id}.json").read_text(encoding="utf-8"))
    assert saved["text"] == SCRIPT and saved["source_ids"]

    # 2nd evaluation: same scripts from the cache, no LLM calls
    again = Evaluator(FakeRetriever(), tmp_path / "runs", llm=llm, references_dir=references).evaluate(cases)
    assert llm.calls == 3 and again[0].rouge1 == row.rouge1


# ---------------------------------------------------------------- summary.py / export.py


def test_tables_group_rows_by_search_mode_and_by_audience(tmp_path, references):
    cases = default_cases(["P3"])
    rows = Evaluator(FakeRetriever(), tmp_path / "runs", llm=CountingLLM(), references_dir=references).evaluate(cases)

    assert [(group, n) for group, n, _ in retrieval_table(rows)] == [("dense", 1), ("bm25", 1), ("hybrid", 1)]
    assert [(group, n) for group, n, _ in audience_table(rows)] == \
        [("grad_students", 1), ("policymakers", 1), ("press", 1)]
    report = results_markdown(rows, n_generated=5)
    assert "## 1. Retrieval ablation" in report and "| hybrid | 1 |" in report
