"""
overlap.py - ROUGE: how many WORDS a generated script shares with the human reference.

    ROUGE-1  shared single words          ("knowledge", "distillation")
    ROUGE-2  shared word pairs            ("knowledge distillation")
    ROUGE-L  longest common subsequence   (same words in the same order)

Each is an F1 score from 0 to 1 (precision and recall of the shared words).
ROUGE only sees exact words (after stemming: "models" = "model"), so a correct
paraphrase scores low - that is why we also use BERTScore (semantic.py).
Citations like [P3_p2_c06] are removed first: the human reference has none.
"""

from rouge_score import rouge_scorer

from src.provenance.claim import strip_citations

ROUGE_TYPES = ("rouge1", "rouge2", "rougeL")
_scorer = rouge_scorer.RougeScorer(list(ROUGE_TYPES), use_stemmer=True)


def rouge(candidate: str, reference: str) -> dict[str, float]:
    scores = _scorer.score(reference, strip_citations(candidate))  # (target, prediction)
    return {name: round(scores[name].fmeasure, 4) for name in ROUGE_TYPES}
