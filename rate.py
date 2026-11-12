"""
Day 10: human evaluation - YOU rate the 15 cached scripts in eval/runs/, blind.

Run:
    python rate.py --rater aditi             # rate everything (quit with q, run again to continue)
    python rate.py --rater aditi --only claims
    python rate.py                           # no rater: only update eval/human/results.md
    python rate.py --rebuild-items           # after re-generating eval/runs/ (python evaluate.py --fresh)

Part 1: each script 1-5 on factuality, audience fit, helpfulness   (~15 x 1 min)
Part 2: the sentences the checker doubted: true / hype / wrong      (~1 x 10 s each)
"""

import argparse
import json

from src import config
from src.chunking import load_chunks
from src.human_eval import Items, RaterFile, RatingSession, build_items, load_all, save_report

ITEMS_FILE = config.HUMAN_EVAL_DIR / "items.json"


def main():
    args = parse_args()
    items = load_or_build_items(args.rebuild_items)
    print(f"{len(items.scripts)} scripts and {len(items.claims)} sentences to rate ({ITEMS_FILE.name})")

    if args.rater:
        chunks = {c.chunk_id: c for c in load_chunks(config.INDEX_DIR / "chunks.json")}
        RatingSession(items, RaterFile.open(args.rater, config.HUMAN_EVAL_DIR), chunks).run(args.only)

    raters = load_all(config.HUMAN_EVAL_DIR)
    if raters:
        metrics = {row["case_id"]: row for row in
                   json.loads((config.EVAL_DIR / "results.json").read_text(encoding="utf-8"))["rows"]}
        path = save_report(items, raters, metrics, config.HUMAN_EVAL_DIR / "results.md")
        print(f"Report -> {path.relative_to(config.PROJECT_ROOT)}")


def load_or_build_items(rebuild: bool) -> Items:
    if ITEMS_FILE.exists() and not rebuild:
        return Items.load(ITEMS_FILE)
    from src.retrieval import Retriever  # only needed to build the items (loads the embedding model)
    print("Building the items from eval/runs/ (checking every sentence once)...")
    items = build_items(config.EVAL_DIR / "runs", Retriever.load())
    items.save(ITEMS_FILE)
    return items


def parse_args():
    parser = argparse.ArgumentParser(description="Human evaluation of the generated scripts")
    parser.add_argument("--rater", help="your name, lowercase (e.g. aditi) - each rater gets their own file")
    parser.add_argument("--only", choices=["all", "scripts", "claims"], default="all")
    parser.add_argument("--rebuild-items", action="store_true", help="rebuild items.json from eval/runs/")
    return parser.parse_args()


if __name__ == "__main__":
    main()
