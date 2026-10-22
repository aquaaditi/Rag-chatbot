"""
hybrid.py - combine several ranked result lists into one (Reciprocal Rank Fusion).

Dense scores (cosine, about 0-1) and BM25 scores (0-20+) are on different scales,
so we can't just add them. RRF only uses each chunk's RANK in each list:

    score(chunk) = sum over lists of  1 / (RRF_K + rank)

A chunk ranked high by both methods wins; a chunk found by only one still counts.
(Cormack, Clarke & Buettcher, 2009, "Reciprocal Rank Fusion outperforms Condorcet
and individual rank learning methods".)
"""

from src import config


def reciprocal_rank_fusion(
    ranked_lists: list[list[tuple[int, float]]], k: int = config.RRF_K
) -> list[tuple[int, float]]:
    """Each input list holds (position, score) pairs, best first.
    Returns (position, fused score) pairs, best first."""
    fused: dict[int, float] = {}
    for ranked in ranked_lists:
        for rank, (position, _score) in enumerate(ranked, start=1):
            fused[position] = fused.get(position, 0.0) + 1.0 / (k + rank)
    return sorted(fused.items(), key=lambda item: item[1], reverse=True)
