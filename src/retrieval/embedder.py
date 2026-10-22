"""
embedder.py - turn text into embeddings (vectors of numbers that capture meaning).

Texts with similar meaning get vectors that point in a similar direction.
We normalise every vector to length 1, so the dot product of two vectors
equals their COSINE SIMILARITY (1 = same meaning, 0 = unrelated).
"""

import numpy as np

from src import config
from src.chunking import Chunk


class Embedder:
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        # Imported here because loading PyTorch is slow; only pay for it when embedding.
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        try:
            # Use the copy already on disk - skips a slow online check on every start
            self._model = SentenceTransformer(model_name, local_files_only=True)
        except OSError:
            self._model = SentenceTransformer(model_name)  # first run: download it (~130 MB)

    @property
    def dimension(self) -> int:
        return self._model.get_embedding_dimension()

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        """Embed document chunks. Returns an array of shape (len(texts), dimension)."""
        return self._encode(texts)

    def embed_query(self, question: str) -> np.ndarray:
        """Embed a search question (with the model's query instruction). Shape (1, dimension)."""
        return self._encode([config.EMBEDDING_QUERY_PREFIX + question])

    def _encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        return vectors.astype(np.float32)  # FAISS needs float32


def passage_text(chunk: Chunk) -> str:
    """The text we embed for a chunk: its section title + its text.
    The title adds context, e.g. a chunk under '2 Distillation' is about distillation
    even if that word never appears in the chunk itself."""
    return f"{chunk.section}. {chunk.text}"
