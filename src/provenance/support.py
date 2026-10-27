"""
support.py - is each claim really supported by the chunk it cites?

For every claim we look for the source sentence that says the same thing:
  1. SEMANTIC match: embed the claim and every sentence of the source chunks
     (also pairs of neighbouring sentences, for claims that merge two, and the
     section heading), and take the highest cosine similarity.
  2. EXACT match for numbers (see numbers.py).

Verdicts:
    supported    cited chunk says it  (similarity >= SUPPORTED_THRESHOLD, numbers OK)
    weak         loosely related      (similarity >= WEAK_THRESHOLD, numbers OK)
    unsupported  the cited chunk does not say it, or a number is wrong / invented
    uncited      no (valid) citation at all

The best-matching sentence among ALL sources is also recorded: that is the
claim's provenance (chunk ID + page + the exact source sentence).
"""

import re
from dataclasses import dataclass, field

import numpy as np

from src import config
from src.chunking import Chunk
from src.chunking.sentences import split_sentences
from src.provenance.claim import Claim
from src.provenance.numbers import missing_numbers
from src.retrieval.embedder import Embedder


@dataclass
class Evidence:
    chunk: Chunk
    sentence: str  # the source sentence(s) that best match the claim
    score: float  # cosine similarity between claim and that sentence


@dataclass
class ClaimCheck:
    claim: Claim
    verdict: str  # "supported" | "weak" | "unsupported" | "uncited"
    cited_evidence: Evidence | None  # best match inside the CITED chunks
    best_evidence: Evidence | None  # best match inside ALL source chunks
    missing_numbers: list[str] = field(default_factory=list)
    invalid_ids: list[str] = field(default_factory=list)  # cited IDs that were not in the sources

    @property
    def score(self) -> float:
        return self.cited_evidence.score if self.cited_evidence else 0.0


class SupportChecker:
    def __init__(self, embedder: Embedder, sources: list[Chunk]):
        self._embedder = embedder
        self._sources = {c.chunk_id: c for c in sources}
        # Every source sentence (and pair of neighbouring sentences), plus each chunk's section
        # heading (a heading like "Matching logits is a special case of distillation" is a claim
        # of the paper too), embedded once
        self._units = [(chunk, text) for chunk in sources for text in _evidence_units(chunk)]
        self._unit_vectors = embedder.embed_passages([text for _, text in self._units])

    def check_all(self, claims: list[Claim]) -> list[ClaimCheck]:
        if not claims:
            return []
        claim_vectors = self._embedder.embed_passages([c.text for c in claims])
        similarities = claim_vectors @ self._unit_vectors.T  # cosine, because vectors are normalised
        return [self._check(claim, row) for claim, row in zip(claims, similarities)]

    def _check(self, claim: Claim, sims: np.ndarray) -> ClaimCheck:
        valid = [c for c in claim.cited_ids if c in self._sources]
        invalid = [c for c in claim.cited_ids if c not in self._sources]
        best = self._best(sims, allowed_ids=None)

        if not valid:
            return ClaimCheck(claim, "uncited", None, best, invalid_ids=invalid)

        cited = self._best(sims, allowed_ids=set(valid))
        cited_text = " ".join(self._sources[c].text for c in valid)
        missing = missing_numbers(claim.text, cited_text)
        return ClaimCheck(claim, _verdict(cited.score, missing), cited, best, missing, invalid)

    def _best(self, sims: np.ndarray, allowed_ids: set[str] | None) -> Evidence | None:
        best_i = max(
            (i for i, (chunk, _) in enumerate(self._units) if allowed_ids is None or chunk.chunk_id in allowed_ids),
            key=lambda i: sims[i],
            default=None,
        )
        if best_i is None:
            return None
        chunk, text = self._units[best_i]
        return Evidence(chunk, text, float(sims[best_i]))


def _verdict(score: float, missing: list[str]) -> str:
    if missing:
        return "unsupported"
    if score >= config.SUPPORTED_THRESHOLD:
        return "supported"
    if score >= config.WEAK_THRESHOLD:
        return "weak"
    return "unsupported"


NON_CLAIM_SECTIONS = ("Front matter", "Abstract", "Introduction", "Acknowledgments", "Acknowledgements")


def _evidence_units(chunk: Chunk) -> list[str]:
    """Each sentence, each pair of neighbouring sentences, and the section heading."""
    sentences = split_sentences(chunk.text)
    pairs = [f"{a} {b}" for a, b in zip(sentences, sentences[1:])]
    heading = re.sub(r"^[\d.]+\s*", "", chunk.section)  # "2.1 Matching logits..." -> "Matching logits..."
    headings = [heading] if heading not in NON_CLAIM_SECTIONS and len(heading.split()) >= 3 else []
    return sentences + pairs + headings
