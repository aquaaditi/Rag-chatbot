"""
report.py - the ProvenanceReport: every claim's check + the summary metrics.

Metrics (the task's "automatic evaluation"):
    citation coverage   share of claims with at least one valid citation
    supported share     share of claims fully supported by their cited chunk
                        (our factuality proxy)
    mean similarity     average claim-to-best-source-sentence similarity
    number errors       claims with a number that is not in their cited source
"""

from dataclasses import dataclass

from src.chunking import Chunk
from src.provenance.claim import Claim
from src.provenance.support import ClaimCheck, SupportChecker
from src.retrieval.embedder import Embedder

VERDICTS = ("supported", "weak", "unsupported", "uncited")


@dataclass
class ProvenanceReport:
    checks: list[ClaimCheck]

    @property
    def n_claims(self) -> int:
        return len(self.checks)

    def count(self, verdict: str) -> int:
        return sum(c.verdict == verdict for c in self.checks)

    @property
    def citation_coverage(self) -> float:
        return self._share(lambda c: c.verdict != "uncited")

    @property
    def supported_share(self) -> float:
        return self._share(lambda c: c.verdict == "supported")

    @property
    def mean_similarity(self) -> float:
        scores = [c.best_evidence.score for c in self.checks if c.best_evidence]
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def number_errors(self) -> int:
        return sum(bool(c.missing_numbers) for c in self.checks)

    @property
    def flagged(self) -> list[ClaimCheck]:
        """Claims a human should look at: unsupported or uncited."""
        return [c for c in self.checks if c.verdict in ("unsupported", "uncited")]

    def _share(self, condition) -> float:
        return sum(condition(c) for c in self.checks) / self.n_claims if self.checks else 0.0


def check_provenance(claims: list[Claim], sources: list[Chunk], embedder: Embedder) -> ProvenanceReport:
    return ProvenanceReport(SupportChecker(embedder, sources).check_all(claims))
