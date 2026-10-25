"""
Day 4: generate an audience-adaptive script with citations (end-to-end RAG).

Run (after build_index.py):
    python generate.py --paper P3 --audience policymakers --length 90s --style plain_english
    python generate.py "how the method works" --paper P2 --audience grad_students --style technical
    python generate.py --paper P1 --length 30s --style press_release --save --show-prompt

Choices:
    --audience  policymakers | grad_students | press
    --length    30s | 90s | 5min
    --style     technical | plain_english | press_release
"""

import argparse

from src import config
from src.generation import AUDIENCES, LENGTHS, STYLES, GeneratedScript, ScriptGenerator, ScriptRequest
from src.generation.export import save_markdown
from src.retrieval import Retriever

DEFAULT_TOPIC = "the problem the paper solves, its main idea, and its key results"


def main():
    args = parse_args()
    request = ScriptRequest(
        topic=args.topic,
        audience=args.audience,
        length=args.length,
        style=args.style,
        paper_id=args.paper,
    )

    print("Loading retriever and asking the LLM...")
    result = ScriptGenerator(Retriever.load()).generate(request)

    if args.show_prompt:
        print("\n========== PROMPT SENT TO THE LLM ==========\n" + result.prompt)
    print_result(result)

    if args.save:
        path = save_markdown(result, config.EXAMPLES_DIR, include_prompt=args.show_prompt)
        print(f"\nSaved -> {path.relative_to(config.PROJECT_ROOT)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a script from the papers")
    parser.add_argument("topic", nargs="?", default=DEFAULT_TOPIC)
    parser.add_argument("--paper", help="e.g. P3 (default: all papers)")
    parser.add_argument("--audience", default="grad_students", choices=list(AUDIENCES))
    parser.add_argument("--length", default="90s", choices=list(LENGTHS))
    parser.add_argument("--style", default="plain_english", choices=list(STYLES))
    parser.add_argument("--show-prompt", action="store_true", help="print the full prompt")
    parser.add_argument("--save", action="store_true", help="save to examples/ as Markdown")
    return parser.parse_args()


def print_result(result: GeneratedScript):
    r = result.request
    print(f"\n========== SCRIPT ({r.audience}, {r.length}, {r.style}) ==========\n")
    print(result.text)
    print("\n========== CHECKS ==========")
    print(f"Words: {result.n_words} (target ~{r.target_words})")
    print(f"Chunks given: {result.source_ids}")
    print(f"Chunks cited: {result.cited_ids}")
    print(f"Invented citations: {result.unknown_ids or 'none'}")


if __name__ == "__main__":
    main()
