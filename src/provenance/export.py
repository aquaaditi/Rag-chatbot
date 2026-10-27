"""
export.py - show a ProvenanceReport as Markdown (saved under each example) and
as a short summary for the terminal.
"""

from src.provenance.report import ProvenanceReport
from src.provenance.support import ClaimCheck

ICONS = {"supported": "✅", "weak": "⚠️", "unsupported": "❌", "uncited": "➖"}


def summary_lines(report: ProvenanceReport) -> list[str]:
    counts = "  ".join(f"{ICONS[v]} {v} {report.count(v)}" for v in ICONS)
    return [
        f"Claims checked: {report.n_claims}   {counts}",
        f"Citation coverage: {report.citation_coverage:.0%}   "
        f"Supported (factuality proxy): {report.supported_share:.0%}   "
        f"Mean similarity: {report.mean_similarity:.2f}   Number errors: {report.number_errors}",
    ]


def explain(check: ClaimCheck) -> str:
    """One short reason, for flagged claims."""
    if check.verdict == "uncited":
        best = check.best_evidence
        hint = f" (closest source: {best.chunk.chunk_id}, similarity {best.score:.2f})" if best else ""
        return "no valid citation" + hint
    if check.missing_numbers:
        return f"number(s) not in the cited source: {', '.join(check.missing_numbers)}"
    if check.verdict == "unsupported":
        return f"cited chunk does not say this (similarity {check.score:.2f})"
    return f"similarity {check.score:.2f}"


def report_to_markdown(report: ProvenanceReport) -> str:
    lines = ["", "## Provenance (every claim -> its source)", ""]
    lines += [f"- {line}" for line in summary_lines(report)]
    lines += [
        "",
        "| | Where | Claim | Cited | Score | Best source sentence (page) |",
        "|---|---|---|---|---|---|",
    ]
    for check in report.checks:
        evidence = check.cited_evidence or check.best_evidence
        source = f"{_cell(evidence.sentence, 90)} (`{evidence.chunk.chunk_id}`, p.{evidence.chunk.page})" if evidence else ""
        note = "" if check.verdict in ("supported", "weak") else f"<br>_{explain(check)}_"
        lines.append(
            f"| {ICONS[check.verdict]} | {check.claim.location} | {_cell(check.claim.text, 110)}{note} "
            f"| {', '.join(check.claim.cited_ids) or '—'} | {check.score:.2f} | {source} |"
        )
    return "\n".join(lines) + "\n"


def _cell(text: str, limit: int) -> str:
    text = text.replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"
