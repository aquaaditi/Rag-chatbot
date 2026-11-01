"""
Evaluation stage:  many generated scripts  ->  numbers that say how good the chatbot is

    cases.py       WHAT to evaluate: papers x search modes x audiences (EvalCase)
    references.py  the human-written reference scripts (data/references/)
    overlap.py     ROUGE-1/2/L: shared words with the reference
    semantic.py    BERTScore: shared meaning with the reference
    row.py         EvalRow: all metrics of one script
    runner.py      Evaluator: generate (cached in eval/runs/) -> measure each case
    summary.py     the two experiment tables (means per search mode / per audience)
    export.py      eval/results.md + eval/results.json

Grounding metrics come from the provenance stage, readability from the conversation
stage and warnings from the safety stage - evaluation reuses them, it does not copy them.
"""

from src.evaluation.cases import EvalCase, default_cases
from src.evaluation.export import save_results
from src.evaluation.row import EvalRow
from src.evaluation.runner import Evaluator

__all__ = ["EvalCase", "EvalRow", "Evaluator", "default_cases", "save_results"]
