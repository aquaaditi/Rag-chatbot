"""
export.py - eval/human/results.md: the human evaluation, next to the automatic one.
"""

from datetime import datetime
from pathlib import Path

from src.evaluation.cases import BASE_AUDIENCE
from src.human_eval.analysis import (CRITERION_NAMES, LABELS, agreement, claim_labels, correlations, group_means,
                                     human_truth, labels_by_verdict, script_means)
from src.human_eval.items import Items
from src.human_eval.ratings import RaterFile
from src.human_eval.rubric import rubric_text


def save_report(items: Items, raters: list[RaterFile], metrics: dict[str, dict], path: Path) -> Path:
    path.write_text(report_markdown(items, raters, metrics), encoding="utf-8")
    return path


def report_markdown(items: Items, raters: list[RaterFile], metrics: dict[str, dict]) -> str:
    means = script_means(raters)
    labels = claim_labels(raters)
    n_rated = sum(len(r.scripts) for r in raters)
    lines = [
        "# Human evaluation",
        "",
        f"_{datetime.now():%Y-%m-%d %H:%M} · {len(raters)} rater(s): {', '.join(r.rater for r in raters) or '-'} · "
        f"{n_rated} script ratings · {sum(len(r.claims) for r in raters)} sentence labels · "
        "blind: raters saw the audience, not the search mode, the metrics or the checker's verdict_",
        "",
        "## 1. Scripts (1-5, higher is better)",
        "",
        "**Per audience** (hybrid search)",
        "",
        *_group_table(group_means(items.scripts, means, lambda s: s.audience, lambda s: s.mode == "hybrid"),
                      "audience"),
        "",
        f"**Per search mode** ({BASE_AUDIENCE})",
        "",
        *_group_table(group_means(items.scripts, means, lambda s: s.mode, lambda s: s.audience == BASE_AUDIENCE),
                      "search mode"),
        "",
        "## 2. Sentences the checker doubted: what did the human say?",
        "",
        "| checker verdict | n | " + " | ".join(LABELS) + " |",
        "|---" * (len(LABELS) + 2) + "|",
        *[f"| {verdict} | {n} | " + " | ".join(f"{shares[label]:.0%}" for label in LABELS) + " |"
          for verdict, n, shares in labels_by_verdict(items.claims, labels)],
        "",
        "_supported = 1 random supported sentence per script (a control: can 'supported' be trusted?)_",
        "",
        "## 3. How many claims are really true? (checker vs human)",
        "",
        "| audience | scripts | supported (strict) | grounded (lenient) | **true according to the human** |",
        "|---|---|---|---|---|",
        *[f"| {t.audience} | {t.n_scripts} | {t.supported:.0%} | {t.grounded:.0%} | **{t.human:.0%}** |"
          for t in human_truth(items, labels, metrics)],
        "",
        "_true = supported claims x (share of controls rated true) + doubtful claims rated true; "
        "hype counts as NOT true_",
        "",
        "## 4. Do the automatic metrics agree with the human? (Spearman, all scripts)",
        "",
        "| human score | metric | n | rho | p |",
        "|---|---|---|---|---|",
        *[f"| {c.criterion} | {c.metric} | {c.n} | {_num(c.rho, '+.2f')} | {_num(c.p, '.2f')} |"
          for c in correlations(means, metrics)],
        "",
        "_rho: +1 = the metric ranks the scripts like the human, 0 = unrelated. "
        "With ~15 scripts only a large rho (about 0.5+) means much._",
        "",
        "## 5. Do the raters agree with each other?",
        "",
        *_agreement_lines(raters),
        "",
        "## Rubric",
        "",
        "```",
        rubric_text(),
        "```",
        "",
        "## Comments",
        "",
        *_comments(items, raters),
    ]
    return "\n".join(lines)


def _group_table(table, group_title: str) -> list[str]:
    lines = [f"| {group_title} | scripts | " + " | ".join(CRITERION_NAMES) + " |",
             "|---" * (len(CRITERION_NAMES) + 2) + "|"]
    for group, n, values in table:
        lines.append(f"| {group} | {n} | " + " | ".join(f"{values[c]:.1f}" for c in CRITERION_NAMES) + " |")
    return lines


def _agreement_lines(raters: list[RaterFile]) -> list[str]:
    result = agreement(raters)
    if not result:
        return ["_Needs at least 2 raters (ask a friend: `python rate.py --rater <their name>`)._"]
    lines = ["| what | comparisons | same answer | at most 1 apart |", "|---|---|---|---|"]
    for name, a in result.items():
        lines.append(f"| {name} | {a.n_pairs} | {a.exact:.0%} | {_num(a.within_one, '.0%')} |")
    return lines


def _comments(items: Items, raters: list[RaterFile]) -> list[str]:
    claims = {c.key: c for c in items.claims}
    lines = []
    for rater in raters:
        for case_id, rating in rater.scripts.items():
            if rating.get("comment"):
                lines.append(f"- **{rater.rater}** on `{case_id}`: {rating['comment']}")
        for key, answer in rater.claims.items():
            if answer.get("comment") and key in claims:
                lines.append(f"- **{rater.rater}** on \"{claims[key].claim}\" ({answer['label']}): {answer['comment']}")
    return lines or ["_none_"]


def _num(value: float | None, fmt: str) -> str:
    return "-" if value is None else format(value, fmt)
