"""
export.py - write the evaluation as eval/results.md (for people) and eval/results.json (for code).
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from src import config
from src.evaluation.row import EvalRow
from src.evaluation.summary import COLUMNS, Table, audience_table, retrieval_table

PERCENT_COLUMNS = {"supported", "grounded", "cited", "length error"}

METRIC_GUIDE = """## What the columns mean

| Column | Meaning | Better |
|---|---|---|
| supported | share of claims whose cited chunk really says it (embedding match >= 0.80): our **factuality proxy** | higher |
| grounded | lenient version: supported OR weak (match >= 0.70). True plain-English paraphrases often score 0.70-0.80, so the truth is usually between the two | higher |
| cited | **citation coverage**: share of claims with a valid [chunk ID] | higher |
| number errors | claims with a number that is not in the cited chunk (per script) | 0 |
| invented IDs | cited chunk IDs that were never given to the model (per script) | 0 |
| ROUGE-1 / ROUGE-L | shared words / longest shared word sequence with the **human reference** | higher* |
| BERTScore | similarity in meaning to the human reference (rescaled: ~0 = unrelated) | higher* |
| readability | Flesch reading ease (60+ plain English, <30 academic) | depends on the audience |
| warnings | safety & accessibility warnings (long sentences, undefined acronyms, readability floor) | lower |
| length error | distance from the target length (90s = 225 words) | lower |

\\* The references were written by hand for a general audience, so a technical script for
graduate students SHOULD score lower against them - that is adaptation, not a mistake.
"""


def save_results(rows: list[EvalRow], directory: Path, n_generated: int) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    data = {"model": config.LLM_MODEL, "evaluated": f"{datetime.now():%Y-%m-%d %H:%M}",
            "rows": [asdict(r) for r in rows]}
    (directory / "results.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    path = directory / "results.md"
    path.write_text(results_markdown(rows, n_generated), encoding="utf-8")
    return path


def results_markdown(rows: list[EvalRow], n_generated: int) -> str:
    papers = sorted({r.paper_id for r in rows})
    lines = [
        "# Automatic evaluation",
        "",
        f"_{datetime.now():%Y-%m-%d %H:%M} · model `{config.LLM_MODEL}` · {len(rows)} scripts "
        f"({', '.join(papers)}; 90 seconds; {n_generated} newly generated, the rest from eval/runs/) · "
        f"BERTScore model `{config.BERTSCORE_MODEL}`_",
        "",
        "## 1. Retrieval ablation (policymakers, plain English): does hybrid search help?",
        "",
        *table_markdown(retrieval_table(rows), "search mode"),
        "",
        "## 2. Audience adaptation (hybrid search): does the output change with the audience?",
        "",
        *table_markdown(audience_table(rows), "audience"),
        "",
        "## 3. Every script",
        "",
        *rows_markdown(rows),
        "",
        METRIC_GUIDE,
    ]
    return "\n".join(lines)


def table_markdown(table: Table, group_title: str) -> list[str]:
    titles = [title for title, _ in COLUMNS]
    lines = [f"| {group_title} | n | " + " | ".join(titles) + " |", "|---" * (len(titles) + 2) + "|"]
    for group, n, values in table:
        lines.append(f"| {group} | {n} | " + " | ".join(_fmt(t, values[t]) for t in titles) + " |")
    return lines


def rows_markdown(rows: list[EvalRow]) -> list[str]:
    titles = [title for title, _ in COLUMNS]
    lines = ["| script | words | " + " | ".join(titles) + " |", "|---" * (len(titles) + 2) + "|"]
    for row in rows:
        values = " | ".join(_fmt(title, get(row)) for title, get in COLUMNS)
        lines.append(f"| `{row.case_id}` | {row.words} | {values} |")
    return lines


def _fmt(title: str, value: float | None) -> str:
    if value is None:
        return "-"
    if title in PERCENT_COLUMNS:
        return f"{value:.0%}"
    if title in ("readability", "warnings", "number errors", "invented IDs"):
        return f"{value:.1f}" if value != int(value) else f"{int(value)}"
    return f"{value:.3f}"
