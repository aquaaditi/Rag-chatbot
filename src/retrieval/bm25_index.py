"""
bm25_index.py - SPARSE (keyword) search with BM25.

BM25 scores a chunk by the words it shares with the question:
  - rare words count more than common ones ("softmax" > "the"),
  - repeating a word helps, but with diminishing returns,
  - long chunks are not favoured just for being long.
It catches EXACT terms that embeddings can miss: names, symbols, dataset names
like "MNIST" or "SST-2".
"""

import re

from rank_bm25 import BM25Okapi

STOPWORDS = set(
    "a an and are as at be by for from has have in is it its of on or that the this to was were "
    "what which with how why do does we our".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase words and numbers, without stopwords. 'SST-2' -> ['sst-2']."""
    words = re.findall(r"[a-z0-9]+(?:[-.][a-z0-9]+)*", text.lower())
    return [w for w in words if w not in STOPWORDS]


class BM25Index:
    def __init__(self, texts: list[str]):
        self._bm25 = BM25Okapi([tokenize(t) for t in texts])
        self._size = len(texts)

    def search(self, question: str, k: int) -> list[tuple[int, float]]:
        """Return up to k (position, BM25 score) pairs, best first. Chunks with score 0 are skipped."""
        scores = self._bm25.get_scores(tokenize(question))
        best = sorted(range(self._size), key=lambda i: scores[i], reverse=True)[:k]
        return [(i, float(scores[i])) for i in best if scores[i] > 0]
