"""
Retrieval stage:  question  ->  the most relevant Chunks

    retrieved_chunk.py  RetrievedChunk data type (chunk + score + rank)
    embedder.py         text -> embedding vectors (sentence-transformers, bge-small)
    vector_store.py     DENSE search over vectors (FAISS)
    bm25_index.py       SPARSE keyword search (BM25)
    hybrid.py           merge dense + sparse rankings (Reciprocal Rank Fusion)
    retriever.py        Retriever: build / save / load the index, retrieve()

Other stages only need `Retriever` and `RetrievedChunk`.
"""

from src.retrieval.retrieved_chunk import RetrievedChunk
from src.retrieval.retriever import Retriever

__all__ = ["RetrievedChunk", "Retriever"]
