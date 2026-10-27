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
from src.provenance import ProvenanceReport, check_provenance, claims_from_script
from src.provenance.export import explain, report_to_markdown, summary_lines
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
    retriever = Retriever.load()
    result = ScriptGenerator(retriever).generate(request)

    if args.show_prompt:
        print("\n========== PROMPT SENT TO THE LLM ==========\n" + result.prompt)
    print_result(result)

    report = None
    if not args.no_check:
        report = check_provenance(claims_from_script(result), result.sources, retriever.embedder)
        print_provenance(report)

    if args.save:
        extra = report_to_markdown(report) if report else ""
        path = save_markdown(result, config.EXAMPLES_DIR, include_prompt=args.show_prompt, extra=extra)
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
    parser.add_argument("--no-check", action="store_true", help="skip the provenance check")
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


def print_provenance(report: ProvenanceReport):
    print("\n========== PROVENANCE ==========")
    print("\n".join(summary_lines(report)))
    for check in report.flagged:
        print(f"  [{check.verdict}] {check.claim.text[:100]}\n      -> {explain(check)}")


if __name__ == "__main__":
    main()
