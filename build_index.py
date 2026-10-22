"""
Day 3, step 1: embed every chunk and save the search index.

Run:  python build_index.py        (after python chunk_papers.py)
Output: index/  (vectors.faiss, chunks.json, index_info.json)

Re-run it whenever the papers or the chunking change.
"""

import time

from src import config
from src.chunking import load_chunks
from src.retrieval import Retriever


def main():
    chunk_files = sorted(config.CHUNKS_DIR.glob("*.json"))
    if not chunk_files:
        raise SystemExit("No chunks found. Run: python chunk_papers.py")

    chunks = [chunk for f in chunk_files for chunk in load_chunks(f)]
    print(f"Loaded {len(chunks)} chunks from {len(chunk_files)} papers")

    print(f"Embedding with {config.EMBEDDING_MODEL} (first run downloads the model)...")
    start = time.time()
    retriever = Retriever.build(chunks)
    retriever.save()
    print(f"Done in {time.time() - start:.1f}s -> saved to {config.INDEX_DIR.relative_to(config.PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
