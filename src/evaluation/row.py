"""
row.py - EvalRow: every metric for one generated script (one row of the results table).
"""

from dataclasses import dataclass


@dataclass
class EvalRow:
    case_id: str
    paper_id: str
    audience: str
    style: str
    mode: str  # retrieval mode: hybrid / dense / bm25

    # length
    words: int
    target_words: int

    # grounding (provenance, Day 6)
    n_claims: int
    citation_coverage: float  # share of claims with a valid citation
    supported_share: float  # factuality proxy: share of claims supported by their cited source (>= 0.80)
    grounded_share: float  # lenient: supported OR weak (>= 0.70) - plain paraphrases often land in "weak"
    mean_similarity: float
    number_errors: int  # claims with a number that is not in the cited source
    invented_citations: int  # cited chunk IDs that were never given to the LLM

    # audience fit (Days 7-8)
    reading_ease: float  # Flesch: higher = easier
    safety_warnings: int  # long sentences, undefined acronyms, readability below the floor...

    # similarity to the human reference (None if there is no reference)
    rouge1: float | None = None
    rouge2: float | None = None
    rougeL: float | None = None
    bertscore: float | None = None

    @property
    def length_error(self) -> float:
        """How far from the target length: 0.10 = 10% too long or too short."""
        return abs(self.words - self.target_words) / self.target_words
