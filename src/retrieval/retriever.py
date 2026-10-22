"""
retriever.py - the retrieval stage's front door: question -> best chunks.

    retriever = Retriever.load()                      # load the saved index
    results = retriever.retrieve("What is temperature in distillation?", k=5)
    results = retriever.retrieve("...", paper_id="P3")    # search one paper only

Search modes:
    "dense"  - meaning-based (embeddings + FAISS)
    "bm25"   - keyword-based
    "hybrid" - both, merged with Reciprocal Rank Fusion (default)
"""

import json
from pathlib import Path

from src import config
from src.chunking import Chunk, load_chunks, save_chunks
from src.retrieval.bm25_index import BM25Index
from src.retrieval.embedder import Embedder, passage_text
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.retrieved_chunk import RetrievedChunk
from src.retrieval.vector_store import VectorStore

CHUNKS_FILE = "chunks.json"
INFO_FILE = "index_info.json"
SEARCH_MODES = ("dense", "bm25", "hybrid")


class Retriever:
    def __init__(self, chunks: list[Chunk], vector_store: VectorStore, embedder: Embedder):
        self.chunks = chunks  # chunks[i] belongs to vector i in the vector store
        self._vectors = vector_store
        self._embedder = embedder
        self._bm25 = BM25Index([passage_text(c) for c in chunks])  # fast to rebuild, so not saved

    # ------------------------------------------------------------ build / save / load

    @classmethod
    def build(cls, chunks: list[Chunk], embedder: Embedder | None = None) -> "Retriever":
        """Embed every chunk and put the vectors in a new vector store."""
        embedder = embedder or Embedder()
        store = VectorStore(embedder.dimension)
        store.add(embedder.embed_passages([passage_text(c) for c in chunks]))
        return cls(chunks, store, embedder)

    def save(self, directory: Path = config.INDEX_DIR) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self._vectors.save(directory)
        save_chunks(self.chunks, directory / CHUNKS_FILE)
        info = {"embedding_model": self._embedder.model_name, "n_chunks": len(self.chunks)}
        (directory / INFO_FILE).write_text(json.dumps(info, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, directory: Path = config.INDEX_DIR) -> "Retriever":
        if not (directory / INFO_FILE).exists():
            raise FileNotFoundError(f"No index in {directory}. Run: python build_index.py")
        info = json.loads((directory / INFO_FILE).read_text(encoding="utf-8"))
        # The question MUST be embedded with the same model as the chunks
        embedder = Embedder(info["embedding_model"])
        return cls(load_chunks(directory / CHUNKS_FILE), VectorStore.load(directory), embedder)

    # ------------------------------------------------------------ search

    def retrieve(
        self, question: str, k: int = config.TOP_K, paper_id: str | None = None, mode: str = "hybrid"
    ) -> list[RetrievedChunk]:
        """Return the k chunks that best match the question, best first."""
        if mode not in SEARCH_MODES:
            raise ValueError(f"mode must be one of {SEARCH_MODES}")

        # Search everything, then filter. Fine for a few thousand chunks; a larger system
        # would store the filter inside the index (e.g. one index per paper).
        n_all = len(self.chunks)
        ranked_lists = []
        if mode in ("dense", "hybrid"):
            ranked_lists.append(self._vectors.search(self._embedder.embed_query(question), n_all))
        if mode in ("bm25", "hybrid"):
            ranked_lists.append(self._bm25.search(question, n_all))

        ranked = ranked_lists[0] if mode != "hybrid" else reciprocal_rank_fusion(ranked_lists)
        if paper_id:
            ranked = [(pos, score) for pos, score in ranked if self.chunks[pos].paper_id == paper_id]

        return [
            RetrievedChunk(chunk=self.chunks[pos], score=score, rank=rank)
            for rank, (pos, score) in enumerate(ranked[:k], start=1)
        ]
