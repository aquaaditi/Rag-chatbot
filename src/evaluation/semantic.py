"""
semantic.py - BERTScore: how close in MEANING a generated script is to the reference.

Every token of both texts gets a contextual embedding (from a BERT-like model);
each token is matched with its most similar token in the other text, and the
similarities are averaged into precision / recall / F1. So "cheap" and
"inexpensive" match, which ROUGE would miss.

rescale_with_baseline=True: raw BERTScores of ANY two English texts are already
around 0.8, which makes differences hard to see. Rescaling maps "unrelated
texts" to about 0, so the scores spread out (and can even be slightly negative).

The model (config.BERTSCORE_MODEL) is loaded only when first needed - it is slow.
"""

from functools import cache

from src import config
from src.provenance.claim import strip_citations


@cache
def _scorer():
    from bert_score import BERTScorer  # imported here: importing it alone takes several seconds

    return BERTScorer(model_type=config.BERTSCORE_MODEL, lang="en", rescale_with_baseline=True)


def bertscore_f1(candidates: list[str], references: list[str]) -> list[float]:
    """One F1 per (candidate, reference) pair, computed in one batch."""
    _, _, f1 = _scorer().score([strip_citations(c) for c in candidates], references)
    return [round(float(x), 4) for x in f1]
