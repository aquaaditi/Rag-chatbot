"""
Provenance stage:  generated text + its sources  ->  every claim linked to the
source sentence that supports it (or flagged when nothing does)

    claim.py    split scripts / slides into claims (sentence + cited IDs)
    numbers.py  EXACT-match check: numbers in a claim must be in its source
    support.py  SEMANTIC check: best-matching source sentence + verdict per claim
    report.py   ProvenanceReport + metrics (citation coverage, supported share...)
    export.py   Markdown table + terminal summary

    report = check_provenance(claims_from_talk(result), result.sources, retriever.embedder)
"""

from src.provenance.claim import Claim, claims_from_script, claims_from_slide, claims_from_talk, extract_claims
from src.provenance.report import ProvenanceReport, check_provenance

__all__ = [
    "Claim", "ProvenanceReport", "check_provenance",
    "claims_from_script", "claims_from_slide", "claims_from_talk", "extract_claims",
]
