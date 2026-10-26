"""
Day 5: generate a structured slide talk (bullets + equations + speaker notes + full script).

The task's example - "Make a 7-slide talk for graduate students focusing on methods;
include 3 speaker notes per slide and preserve key equations":

    python make_talk.py --paper P3 --slides 7 --notes 3 --audience grad_students --focus methods --save

Other examples:
    python make_talk.py --paper P2 --slides 5 --audience policymakers --style plain_english --no-equations --save
    python make_talk.py --paper P1 --slides 4 --length 90s --show-prompt
"""

import argparse

from src import config
from src.generation import AUDIENCES, LENGTHS, STYLES
from src.retrieval import Retriever
from src.talks import GeneratedTalk, TalkGenerator, TalkRequest
from src.talks.export import save_talk_markdown

DEFAULT_TOPIC = "the paper's motivation, method, key equations and results"


def main():
    args = parse_args()
    request = TalkRequest(
        topic=args.topic,
        n_slides=args.slides,
        notes_per_slide=args.notes,
        audience=args.audience,
        style=args.style,
        length=args.length,
        focus=args.focus,
        preserve_equations=not args.no_equations,
        paper_id=args.paper,
    )

    print("Loading retriever and asking the LLM (a full talk can take a minute)...")
    result = TalkGenerator(Retriever.load()).generate(request)

    if args.show_prompt:
        print("\n========== PROMPT SENT TO THE LLM ==========\n" + result.prompt)
    print_talk(result)

    if args.save:
        path = save_talk_markdown(result, config.EXAMPLES_DIR, include_prompt=args.show_prompt)
        print(f"\nSaved -> {path.relative_to(config.PROJECT_ROOT)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a slide talk from the papers")
    parser.add_argument("topic", nargs="?", default=DEFAULT_TOPIC)
    parser.add_argument("--paper", help="e.g. P3 (default: all papers)")
    parser.add_argument("--slides", type=int, default=7)
    parser.add_argument("--notes", type=int, default=3, help="speaker notes per slide")
    parser.add_argument("--audience", default="grad_students", choices=list(AUDIENCES))
    parser.add_argument("--style", default="technical", choices=list(STYLES))
    parser.add_argument("--length", default="5min", choices=list(LENGTHS), help="speaker script length")
    parser.add_argument("--focus", default="", help='e.g. "methods"')
    parser.add_argument("--no-equations", action="store_true", help="don't require equations")
    parser.add_argument("--show-prompt", action="store_true")
    parser.add_argument("--save", action="store_true", help="save to examples/ as Markdown")
    return parser.parse_args()


def print_talk(result: GeneratedTalk):
    talk = result.talk
    print(f"\n================ {talk.title} ================")
    for number, slide in enumerate(talk.slides, start=1):
        print(f"\n--- Slide {number}: {slide.title}")
        for bullet in slide.bullets:
            print(f"  • {bullet}")
        for equation in slide.equations:
            print(f"  [equation]  {equation}")
        for i, note in enumerate(slide.speaker_notes, start=1):
            print(f"  note {i}: {note}")

    print("\n================ FULL SCRIPT ================\n" + talk.script)
    print("\n================ CHECKS ================")
    print(f"Attempts: {result.attempts}  |  Script words: {len(talk.script.split())} "
          f"(target ~{result.request.target_words})")
    print(f"Chunks cited: {len(result.cited_ids)} of {len(result.sources)} given")
    print("Problems left: " + ("none" if not result.problems else "\n  - " + "\n  - ".join(result.problems)))


if __name__ == "__main__":
    main()
