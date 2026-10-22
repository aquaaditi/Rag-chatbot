"""
Tests for the retrieval stage (src/retrieval/).

The first tests use tiny hand-made vectors, so they run instantly without
downloading the embedding model. The last test uses the real index.

Run:  pytest -v
"""

import numpy as np
import pytest

from src import config
from src.retrieval.bm25_index import BM25Index, tokenize
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.vector_store import VectorStore


# ---------------------------------------------------------------- vector_store.py


def unit(v):
    v = np.array(v, dtype=np.float32)
    return v / np.linalg.norm(v)


def test_vector_store_returns_most_similar_first(tmp_path):
    store = VectorStore(dimension=2)
    store.add(np.stack([unit([1, 0]), unit([0, 1]), unit([1, 1])]))
    results = store.search(unit([1, 0.1]).reshape(1, -1), k=3)
    assert [pos for pos, _ in results] == [0, 2, 1]
    assert results[0][1] == pytest.approx(0.995, abs=0.01)  # cosine similarity

    store.save(tmp_path)  # and it survives saving + loading
    assert len(VectorStore.load(tmp_path)) == 3


# ---------------------------------------------------------------- bm25_index.py


def test_tokenize_keeps_dataset_names_and_drops_stopwords():
    assert tokenize("What is the accuracy on SST-2?") == ["accuracy", "sst-2"]


def test_bm25_finds_exact_keyword():
    index = BM25Index(["we use a hierarchical softmax", "results on MNIST digits", "a cat sat"])
    assert index.search("MNIST", k=3)[0][0] == 1
    assert index.search("dog", k=3) == []  # no shared words -> no results


# ---------------------------------------------------------------- hybrid.py


def test_rrf_rewards_chunks_ranked_high_by_both_methods():
    dense = [(7, 0.9), (3, 0.8), (5, 0.7)]
    bm25 = [(3, 12.0), (9, 10.0), (7, 2.0)]
    fused = [pos for pos, _ in reciprocal_rank_fusion([dense, bm25])]
    assert fused[:2] == [3, 7]  # both appear in both lists
    assert set(fused) == {3, 5, 7, 9}  # chunks found by only one method are kept too


# ---------------------------------------------------------------- real index (needs build_index.py)


@pytest.mark.skipif(not (config.INDEX_DIR / "index_info.json").exists(), reason="run build_index.py first")
def test_real_index_finds_the_softmax_equation():
    from src.retrieval import Retriever

    retriever = Retriever.load()
    # Note: the Equation 1 chunk never says "temperature" - its explanation ("where T is a
    # temperature") is on the next page, in another chunk. So we ask with the chunk's own wording.
    results = retriever.retrieve("softmax output layer converts logits into class probabilities", k=3)
    assert results[0].chunk.chunk_id == "P3_p2_c06"  # the chunk with Equation 1 of the distillation paper

    only_p1 = retriever.retrieve("softmax with temperature", k=5, paper_id="P1")
    assert all(r.chunk.paper_id == "P1" for r in only_p1)  # paper filter works
