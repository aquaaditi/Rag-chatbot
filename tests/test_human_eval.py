"""
Tests for the human evaluation stage (src/human_eval/) - fake answers instead of a person
typing, so they run offline in a second.

Run:  pytest -v
"""

import pytest

from src.human_eval import Items, RaterFile, RatingSession
from src.human_eval.analysis import agreement, claim_labels, correlations, human_truth, labels_by_verdict
from src.human_eval.export import report_markdown
from src.human_eval.items import ClaimItem, ScriptItem, _audience_and_mode, select_claims
from src.provenance import Claim
from src.provenance.support import ClaimCheck, Evidence
from test_conversation import CHUNKS

CASE = "P3_press_press_release_hybrid_90s"


def check(text, verdict, score=0.9):
    evidence = Evidence(CHUNKS[1], "Softmax with a temperature produces soft targets.", score)
    return ClaimCheck(Claim(text, ["P3_p2_c06"], "script"), verdict, evidence, evidence)


@pytest.fixture
def items():
    scripts = [ScriptItem(CASE, "press", "hybrid", "Soft targets help small models.", ["P3_p2_c06"]),
               ScriptItem("P3_grad_students_technical_hybrid_90s", "grad_students", "hybrid", "Temperature T.",
                          ["P3_p2_c06"])]
    claims = [ClaimItem(f"{CASE}#{i}", CASE, "press", f"Sentence {i}.", "Source sentence.", "P3_p2_c06", 2, verdict, s)
              for i, verdict, s in [(1, "supported", 0.85), (2, "weak", 0.76), (3, "unsupported", 0.5)]]
    return Items(scripts, claims)


class Answers:
    """Plays the rater: returns the prepared answers one by one."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return self.answers.pop(0)


# ---------------------------------------------------------------- items.py


def test_select_claims_takes_every_doubtful_claim_plus_one_supported_control():
    checks = [check("A is true.", "supported"), check("B is true.", "weak", 0.75), check("C is true.", "supported"),
              check("D is true.", "uncited")]
    chosen = select_claims(checks, CASE, "press")
    assert [c.verdict for c in chosen].count("supported") == 1
    assert {c.claim for c in chosen} >= {"B is true.", "D is true."}
    assert chosen == select_claims(checks, CASE, "press")  # the same control every time
    assert chosen[0].key.startswith(CASE + "#") and chosen[0].page == 2


def test_case_id_gives_audience_and_search_mode():
    assert _audience_and_mode("P1_grad_students_technical_hybrid_90s") == ("grad_students", "hybrid")
    assert _audience_and_mode("P2_policymakers_plain_english_bm25_90s") == ("policymakers", "bm25")


# ---------------------------------------------------------------- session.py / ratings.py


def test_rating_is_blind_saved_after_every_item_and_resumable(tmp_path, items):
    shown = []
    rater = RaterFile.open("tester", tmp_path)
    # script 1: a wrong answer first (re-asked), then 4 / 5 / 3 + a comment; then quit at script 2
    RatingSession(items, rater, {}, Answers("7", "4", "5", "3", "good", "q"), shown.append).run()

    saved = RaterFile.open("tester", tmp_path)
    assert len(saved.scripts) == 1
    assert list(saved.scripts.values())[0] == {"factuality": 4, "audience_fit": 5, "helpfulness": 3, "comment": "good"}
    text = "\n".join(shown)
    assert "hybrid" not in text and "supported" not in text.replace("Does the SOURCE support", "")  # blind

    # 2nd run: script 1 is skipped, script 2 + all 3 sentences are rated
    ask = Answers("3", "3", "3", "", "t", "", "h", "", "w", "")
    RatingSession(items, saved, {}, ask, shown.append).run()
    again = RaterFile.open("tester", tmp_path)
    assert len(again.scripts) == 2 and len(again.claims) == 3 and not ask.answers
    assert sorted(a["label"] for a in again.claims.values()) == ["hype", "true", "wrong"]


def test_rater_name_must_be_a_simple_file_name(tmp_path):
    with pytest.raises(ValueError):
        RaterFile.open("../hack", tmp_path)


# ---------------------------------------------------------------- analysis.py / export.py


def rater(name, tmp_path, labels, factuality=4):
    r = RaterFile.open(name, tmp_path)
    r.scripts = {CASE: {"factuality": factuality, "audience_fit": 4, "helpfulness": 4, "comment": ""}}
    r.claims = {f"{CASE}#{i}": {"label": label, "comment": ""} for i, label in enumerate(labels, start=1)}
    return r


def test_majority_label_and_a_tie_goes_to_the_worse_label(tmp_path):
    a = rater("a", tmp_path, ["true", "true", "wrong"])
    b = rater("b", tmp_path, ["true", "hype", "wrong"])
    labels = claim_labels([a, b])
    assert labels == {f"{CASE}#1": "true", f"{CASE}#2": "hype", f"{CASE}#3": "wrong"}
    assert agreement([a, b])["sentence labels"].exact == pytest.approx(2 / 3)
    assert agreement([a]) == {}  # 1 rater: nothing to compare


def test_human_truth_combines_controls_with_rated_doubtful_claims(tmp_path, items):
    labels = claim_labels([rater("a", tmp_path, ["true", "true", "wrong"])])
    metrics = {CASE: {"n_claims": 4, "supported_share": 0.5, "grounded_share": 0.75}}
    truth = human_truth(items, labels, metrics)
    # 2 supported x 100% controls true + 1 weak rated true = 3 of 4 claims
    assert [(t.audience, t.human) for t in truth] == [("press", 0.75)]
    assert [(v, n) for v, n, _ in labels_by_verdict(items.claims, labels)] == \
        [("supported", 1), ("weak", 1), ("unsupported", 1)]

    # "The sources do not mention costs." is no claim: it leaves the count -> 2 true of 3 claims
    labels = claim_labels([rater("b", tmp_path, ["true", "no_claim", "wrong"])])
    assert human_truth(items, labels, metrics)[0].human == pytest.approx(2 / 3)


def test_report_works_with_one_rater_and_few_scripts(tmp_path, items):
    r = rater("a", tmp_path, ["true", "hype", "wrong"])
    metrics = {CASE: {"n_claims": 4, "supported_share": 0.5, "grounded_share": 0.75, "reading_ease": 40,
                      "bertscore": 0.4, "rougeL": 0.2}}
    assert all(c.rho is None for c in correlations({CASE: r.scripts[CASE]}, metrics))  # too few scripts
    report = report_markdown(items, [r], metrics)
    assert "| press | 1 | 4.0 | 4.0 | 4.0 |" in report and "Needs at least 2 raters" in report
