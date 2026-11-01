"""
cases.py - WHAT we evaluate: one EvalCase = one script request to generate and score.

Two experiments share the same cases:
    retrieval  (ablation)  policymakers, plain English, 90s  x  hybrid / dense / bm25
    audience               hybrid, 90s  x  grad students (technical) / policymakers / press

    P1 x 3 search modes + P1 x 2 more audiences = 5 cases per paper (the hybrid
    policymakers case belongs to both experiments).
"""

from dataclasses import dataclass

from src.generation import ScriptRequest
from src.retrieval.retriever import SEARCH_MODES

TOPIC = "the problem the paper solves, its main idea, and its key results"  # same as generate.py
STYLE_FOR = {"grad_students": "technical", "policymakers": "plain_english", "press": "press_release"}
BASE_AUDIENCE = "policymakers"  # the retrieval experiment uses this audience (closest to the references)


@dataclass(frozen=True)
class EvalCase:
    paper_id: str
    audience: str
    mode: str = "hybrid"
    length: str = "90s"

    @property
    def style(self) -> str:
        return STYLE_FOR[self.audience]

    @property
    def case_id(self) -> str:
        return f"{self.paper_id}_{self.audience}_{self.style}_{self.mode}_{self.length}"

    def to_request(self) -> ScriptRequest:
        return ScriptRequest(TOPIC, audience=self.audience, length=self.length, style=self.style,
                             paper_id=self.paper_id, retrieval_mode=self.mode)


def default_cases(paper_ids: list[str]) -> list[EvalCase]:
    cases = []
    for paper_id in paper_ids:
        cases += [EvalCase(paper_id, BASE_AUDIENCE, mode) for mode in SEARCH_MODES]
        cases += [EvalCase(paper_id, audience) for audience in STYLE_FOR if audience != BASE_AUDIENCE]
    return cases
