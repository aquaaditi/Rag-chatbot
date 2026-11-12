"""
items.py - WHAT a human rates, built once from the cached scripts in eval/runs/ and
frozen in eval/human/items.json, so every rater (and every later report) sees exactly
the same items.

    ScriptItem  one whole script: 1-5 on each criterion (rubric.py)
    ClaimItem   one sentence + the source sentence the checker matched it to: true / hype / wrong

Which claims: every claim the checker did NOT fully trust (weak, unsupported, uncited) -
the open question from Day 9 - plus one SUPPORTED claim per script as a control, to see
whether "supported" can be trusted too. The rater is never shown the verdict (blind rating).
"""

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from src.evaluation.cases import STYLE_FOR
from src.provenance import check_provenance, extract_claims
from src.provenance.claim import strip_citations
from src.provenance.support import ClaimCheck
from src.retrieval import Retriever

DOUBTFUL = ("weak", "unsupported", "uncited")


@dataclass
class ScriptItem:
    case_id: str
    audience: str
    mode: str  # search mode - hidden from the rater
    text: str  # without citations: what the audience would hear
    source_ids: list[str]


@dataclass
class ClaimItem:
    key: str  # "<case_id>#<claim number>"
    case_id: str
    audience: str
    claim: str
    evidence: str  # the source sentence the checker matched (cited chunk, or any source if uncited)
    chunk_id: str
    page: int | None
    verdict: str  # the checker's verdict - hidden from the rater
    score: float


@dataclass
class Items:
    scripts: list[ScriptItem]
    claims: list[ClaimItem]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"scripts": [asdict(s) for s in self.scripts], "claims": [asdict(c) for c in self.claims]}
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Items":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls([ScriptItem(**s) for s in data["scripts"]], [ClaimItem(**c) for c in data["claims"]])


def build_items(runs_dir: Path, retriever: Retriever) -> Items:
    chunks = {c.chunk_id: c for c in retriever.chunks}
    scripts, claims = [], []
    for path in sorted(runs_dir.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        audience, mode = _audience_and_mode(run["case_id"])
        scripts.append(ScriptItem(run["case_id"], audience, mode, strip_citations(run["text"]), run["source_ids"]))
        report = check_provenance(extract_claims(run["text"], "script"), [chunks[i] for i in run["source_ids"]],
                                  retriever.embedder)
        claims += select_claims(report.checks, run["case_id"], audience)
    return Items(scripts, claims)


def select_claims(checks: list[ClaimCheck], case_id: str, audience: str) -> list[ClaimItem]:
    """All doubtful claims + one supported claim (the control, picked the same way every time)."""
    chosen = [i for i, c in enumerate(checks) if c.verdict in DOUBTFUL]
    supported = [i for i, c in enumerate(checks) if c.verdict == "supported"]
    if supported:
        chosen.append(random.Random(case_id).choice(supported))
    return [_claim_item(checks[i], f"{case_id}#{i + 1}", case_id, audience) for i in sorted(chosen)]


def _claim_item(check: ClaimCheck, key: str, case_id: str, audience: str) -> ClaimItem:
    evidence = check.cited_evidence or check.best_evidence
    return ClaimItem(
        key, case_id, audience, check.claim.text,
        evidence=evidence.sentence if evidence else "",
        chunk_id=evidence.chunk.chunk_id if evidence else "",
        page=evidence.chunk.page if evidence else None,
        verdict=check.verdict, score=round(evidence.score, 3) if evidence else 0.0,
    )


def _audience_and_mode(case_id: str) -> tuple[str, str]:
    """'P1_grad_students_technical_hybrid_90s' -> ('grad_students', 'hybrid')"""
    audience = next(a for a in STYLE_FOR if f"_{a}_{STYLE_FOR[a]}_" in case_id)
    mode = case_id.split(f"_{STYLE_FOR[audience]}_")[1].split("_")[0]
    return audience, mode
