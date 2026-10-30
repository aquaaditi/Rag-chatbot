"""
Safety stage:  messages, papers and generated text  ->  refused / blocked / warnings

Layers (each catches what the one before misses):
    1. Gemini's own safety filter        src/llm.py (config.GEMINI_SAFETY_THRESHOLD)
    2. INPUT checks before the LLM       input_guard.py (too long, prompt injection, offensive)
    3. Grounding rule: sources are data  src/generation/prompts.py rule 6
    4. OUTPUT checks after the LLM       report.py (offensive -> blocked; inclusive,
                                         long sentences, acronyms, readability -> warnings)

    offensive.py      offensive words (word list + allowed research words + the paper's own words)
    inclusive.py      exclusionary words -> inclusive alternatives
    injection.py      "ignore previous instructions"-style text in messages or uploaded papers
    accessibility.py  long sentences, undefined acronyms, readability floor per audience
    input_guard.py    check_message() for chat messages
    report.py         check_output() -> SafetyReport for generated text

Other stages only need `check_message`, `check_output`, `find_injection` and `SafetyReport`.
"""

from src.safety.injection import find_injection
from src.safety.input_guard import check_message
from src.safety.report import SafetyIssue, SafetyReport, check_output

__all__ = ["SafetyIssue", "SafetyReport", "check_message", "check_output", "find_injection"]
