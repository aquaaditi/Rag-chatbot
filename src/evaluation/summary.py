"""
summary.py - turn many EvalRows into the two experiment tables (averages per group).

    retrieval_table(rows)  policymakers rows, grouped by search mode   (hybrid vs dense vs bm25)
    audience_table(rows)   hybrid rows, grouped by audience            (grad students vs policymakers vs press)

Each table cell is the MEAN over the papers, so one lucky or unlucky paper
matters less. (With 3 papers and one run each this is still a small sample -
small differences are noise, see NOTES.md Day 9.)
"""

from collections.abc import Callable
from statistics import mean

from src.evaluation.cases import BASE_AUDIENCE, STYLE_FOR
from src.evaluation.row import EvalRow
from src.retrieval.retriever import SEARCH_MODES

# (column title, how to get the value from a row)
COLUMNS: list[tuple[str, Callable[[EvalRow], float | None]]] = [
    ("supported", lambda r: r.supported_share),
    ("grounded", lambda r: r.grounded_share),
    ("cited", lambda r: r.citation_coverage),
    ("number errors", lambda r: r.number_errors),
    ("invented IDs", lambda r: r.invented_citations),
    ("ROUGE-1", lambda r: r.rouge1),
    ("ROUGE-L", lambda r: r.rougeL),
    ("BERTScore", lambda r: r.bertscore),
    ("readability", lambda r: r.reading_ease),
    ("warnings", lambda r: r.safety_warnings),
    ("length error", lambda r: r.length_error),
]

Table = list[tuple[str, int, dict[str, float | None]]]  # (group, number of rows, {column: mean})


def retrieval_table(rows: list[EvalRow]) -> Table:
    return _grouped([r for r in rows if r.audience == BASE_AUDIENCE], lambda r: r.mode, SEARCH_MODES)


def audience_table(rows: list[EvalRow]) -> Table:
    return _grouped([r for r in rows if r.mode == "hybrid"], lambda r: r.audience, list(STYLE_FOR))


def _grouped(rows: list[EvalRow], key: Callable[[EvalRow], str], order) -> Table:
    table = []
    for group in order:
        members = [r for r in rows if key(r) == group]
        if members:
            table.append((group, len(members), {title: _mean(members, get) for title, get in COLUMNS}))
    return table


def _mean(rows: list[EvalRow], get) -> float | None:
    values = [get(r) for r in rows if get(r) is not None]
    return mean(values) if values else None
