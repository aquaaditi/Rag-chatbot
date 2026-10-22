"""
vector_store.py - DENSE search: store chunk embeddings and find the most similar ones.

Uses FAISS (Facebook AI Similarity Search). IndexFlatIP compares the query with
every stored vector using the inner (dot) product; because our vectors are
normalised, that is cosine similarity. Exact and fast enough for thousands of
chunks; FAISS has approximate indexes (e.g. IVF, HNSW) for millions.
"""

from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    INDEX_FILE = "vectors.faiss"

    def __init__(self, dimension: int):
        self._index = faiss.IndexFlatIP(dimension)

    def add(self, vectors: np.ndarray) -> None:
        """Add vectors; the i-th vector added gets position i (= the i-th chunk)."""
        self._index.add(vectors)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[int, float]]:
        """Return up to k (position, cosine similarity) pairs, best first."""
        k = min(k, self._index.ntotal)
        scores, positions = self._index.search(query_vector, k)
        return [(int(p), float(s)) for p, s in zip(positions[0], scores[0]) if p != -1]

    def __len__(self) -> int:
        return self._index.ntotal

    def save(self, directory: Path) -> None:
        faiss.write_index(self._index, str(directory / self.INDEX_FILE))

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        store = cls.__new__(cls)
        store._index = faiss.read_index(str(directory / cls.INDEX_FILE))
        return store
