"""
session.py - the rating loop in the terminal: show an item, ask, save, next.

    RatingSession(items, rater_file, chunks).run()

- BLIND: the rater sees the audience (needed to judge the fit) but not the search mode,
  the metrics or the checker's verdict - knowing them would bias the score.
- Each rater gets their own random ORDER (seeded by the name), so tiredness at the end
  does not always hit the same scripts.
- Already-rated items are skipped: quit with q at any time and continue later.

ask / show are input / print by default; tests pass fakes.
"""

import random
import textwrap
from collections.abc import Callable

from src.chunking import Chunk
from src.human_eval.items import ClaimItem, Items, ScriptItem
from src.human_eval.ratings import RaterFile
from src.human_eval.rubric import CLAIM_LABELS, CRITERIA, SKIP, claim_help_text, rubric_text

AUDIENCE_NAMES = {"grad_students": "graduate students", "policymakers": "policymakers", "press": "the press / public"}
WIDTH = 90


class Quit(Exception):
    pass


class RatingSession:
    def __init__(self, items: Items, rater_file: RaterFile, chunks: dict[str, Chunk],
                 ask: Callable[[str], str] = input, show: Callable[[str], None] = print):
        self._items = items
        self._file = rater_file
        self._chunks = chunks
        self._ask = ask
        self._show = show

    def run(self, part: str = "all") -> None:
        try:
            if part in ("all", "scripts"):
                self._rate_scripts()
            if part in ("all", "claims"):
                self._rate_claims()
        except Quit:
            self._show("\nSaved. Run the same command again to continue where you stopped.")
            return
        self._show("\nAll done - thank you! Report: eval/human/results.md")

    # ------------------------------------------------------------ scripts

    def _rate_scripts(self) -> None:
        todo = [s for s in self._shuffled(self._items.scripts) if s.case_id not in self._file.scripts]
        done = len(self._items.scripts) - len(todo)
        self._show(f"\n=== PART 1: whole scripts ({done}/{len(self._items.scripts)} done) ===\n{rubric_text()}\n"
                   "Type 1-5 · src = show the sources · ? = rubric again · q = save and quit")
        for n, item in enumerate(todo, start=done + 1):
            self._show(f"\n--- Script {n}/{len(self._items.scripts)} · for {AUDIENCE_NAMES[item.audience]} "
                       f"· 90 seconds ---\n{_wrap(item.text)}\n")
            scores = {c.name: self._ask_score(c.name, c.question, item) for c in CRITERIA}
            scores["comment"] = self._ask("  comment (optional, Enter to skip): ").strip()
            self._file.scripts[item.case_id] = scores
            self._file.save()

    def _ask_score(self, name: str, question: str, item: ScriptItem) -> int:
        while True:
            answer = self._ask(f"  {name} - {question} [1-5]: ").strip().lower()
            if answer == "q":
                raise Quit
            if answer == "?":
                self._show(rubric_text())
            elif answer == "src":
                for chunk_id in item.source_ids:
                    self._show(_source(self._chunks.get(chunk_id), chunk_id))
            elif answer in {"1", "2", "3", "4", "5"}:
                return int(answer)
            else:
                self._show("  please type a number 1-5 (or src / ? / q)")

    # ------------------------------------------------------------ claims

    def _rate_claims(self) -> None:
        todo = [c for c in self._shuffled(self._items.claims) if c.key not in self._file.claims]
        done = len(self._items.claims) - len(todo)
        self._show(f"\n=== PART 2: single sentences ({done}/{len(self._items.claims)} done) ===\n"
                   "Does the SOURCE support the SENTENCE?\n" + claim_help_text() +
                   "\n  m = show the whole source chunk · q = save and quit")
        for n, item in enumerate(todo, start=done + 1):
            page = f"page {item.page}" if item.page else "?"
            self._show(f"\n--- Sentence {n}/{len(self._items.claims)} (for {AUDIENCE_NAMES[item.audience]}) ---\n"
                       f"SENTENCE: {_wrap(item.claim, indent='  ').lstrip()}\n"
                       f"SOURCE ({item.chunk_id}, {page}): {_wrap(item.evidence, indent='  ').lstrip()}")
            label = self._ask_label(item)
            comment = self._ask("  comment (optional, Enter to skip): ").strip()
            self._file.claims[item.key] = {"label": label, "comment": comment}
            self._file.save()

    def _ask_label(self, item: ClaimItem) -> str:
        while True:
            answer = self._ask("  t / h / w / n / s: ").strip().lower()
            if answer == "q":
                raise Quit
            if answer == "s":
                return SKIP
            if answer == "m":
                self._show(_source(self._chunks.get(item.chunk_id), item.chunk_id))
            elif answer in CLAIM_LABELS:
                return CLAIM_LABELS[answer]
            else:
                self._show("  please type t, h, w, n or s (or m / q)")

    def _shuffled(self, items: list) -> list:
        items = list(items)
        random.Random(self._file.rater).shuffle(items)
        return items


def _source(chunk: Chunk | None, chunk_id: str) -> str:
    if chunk is None:
        return f"  [{chunk_id}] (chunk not found)"
    return f"  [{chunk_id} · page {chunk.page} · {chunk.section}]\n{_wrap(chunk.text, indent='    ')}"


def _wrap(text: str, indent: str = "") -> str:
    """Wrap every paragraph to WIDTH; every line starts with indent."""
    return "\n".join(textwrap.fill(p, WIDTH, initial_indent=indent, subsequent_indent=indent)
                     for p in text.split("\n") if p.strip())
