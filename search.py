"""
Day 3, step 2: ask a question and see which chunks come back.

Run:
    python search.py "What is the temperature in distillation?"
    python search.py "hierarchical softmax" --mode bm25
    python search.py "results on movie reviews" --paper P1 --k 3
    python search.py "how is the model trained" --compare     (dense vs bm25 vs hybrid)
"""

import argparse

from src import config
from src.retrieval import RetrievedChunk, Retriever


def main():
    parser = argparse.ArgumentParser(description="Search the papers")
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=config.TOP_K, help="number of results")
    parser.add_argument("--paper", help="only search one paper, e.g. P3")
    parser.add_argument("--mode", default="hybrid", choices=["dense", "bm25", "hybrid"])
    parser.add_argument("--compare", action="store_true", help="show all three modes side by side")
    args = parser.parse_args()

    retriever = Retriever.load()
    modes = ["dense", "bm25", "hybrid"] if args.compare else [args.mode]
    for mode in modes:
        results = retriever.retrieve(args.question, k=args.k, paper_id=args.paper, mode=mode)
        print_results(mode, results, short=args.compare)


def print_results(mode: str, results: list[RetrievedChunk], short: bool = False):
    print(f"\n=== {mode.upper()} ===")
    if not results:
        print("  (no matches)")
    for r in results:
        c = r.chunk
        print(f"  #{r.rank}  [{c.chunk_id}]  score {r.score:.3f}   page {c.page}, {c.section}"
              + ("  (math)" if c.has_math else ""))
        if not short:
            print(f"       {c.text[:220]}{'...' if len(c.text) > 220 else ''}\n")


if __name__ == "__main__":
    main()
