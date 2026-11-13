"""
Day 9: automatic evaluation - generate scripts for many settings and score them.

Run:
    python evaluate.py                    # P1-P3: 15 scripts (cached in eval/runs/ after the 1st run)
    python evaluate.py --papers P3        # one paper only
    python evaluate.py --fresh            # generate new scripts instead of using the cached ones
    python evaluate.py --no-bertscore     # skip BERTScore (no model download, faster)
    python evaluate.py --out length_fix   # a separate experiment: eval/length_fix/ (runs + results)

Output: eval/results.md (tables) and eval/results.json (all numbers).
"""

import argparse

from src import config
from src.evaluation import Evaluator, default_cases, save_results
from src.evaluation.summary import audience_table, retrieval_table
from src.retrieval import Retriever


def main():
    args = parse_args()
    retriever = Retriever.load()
    bertscore = None
    if not args.no_bertscore:
        from src.evaluation.semantic import bertscore_f1  # loads a ~250 MB model on first use
        bertscore = bertscore_f1

    directory = config.EVAL_DIR / args.out  # args.out = "" -> eval/ itself
    evaluator = Evaluator(retriever, directory / "runs", bertscore=bertscore, fresh=args.fresh)
    rows = evaluator.evaluate(default_cases(args.papers), progress=print)
    path = save_results(rows, directory, evaluator.n_generated)

    print(f"\n{evaluator.n_generated} scripts generated, {len(rows) - evaluator.n_generated} from the cache")
    for title, table in [("RETRIEVAL ABLATION", retrieval_table(rows)), ("AUDIENCE ADAPTATION", audience_table(rows))]:
        print(f"\n{title}")
        for group, n, values in table:
            bert = values["BERTScore"]
            print(f"  {group:<14} supported {values['supported']:.0%} · grounded {values['grounded']:.0%} · "
                  f"cited {values['cited']:.0%} · "
                  f"ROUGE-L {values['ROUGE-L']:.3f} · BERTScore {'-' if bert is None else f'{bert:.3f}'} · "
                  f"readability {values['readability']:.0f} · warnings {values['warnings']:.1f}")
    print(f"\nSaved -> {path.relative_to(config.PROJECT_ROOT)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate the chatbot automatically")
    parser.add_argument("--papers", nargs="+", default=["P1", "P2", "P3"])
    parser.add_argument("--fresh", action="store_true", help="generate new scripts (ignore eval/runs/)")
    parser.add_argument("--no-bertscore", action="store_true", help="skip BERTScore")
    parser.add_argument("--out", default="", help="sub-folder of eval/ for a separate experiment")
    return parser.parse_args()


if __name__ == "__main__":
    main()
