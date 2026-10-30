"""
Tests for src/llm.py helpers (no API calls).

Run:  pytest -v
"""

import json

from src.llm import _repair_latex


def test_unescaped_latex_in_json_is_repaired():
    # What the model sent: single backslashes inside a JSON string. \f \t \b \r are VALID JSON
    # escapes, so JSON silently turns "\frac" into <form feed> + "rac" (other sequences like \e fail loudly).
    raw_json = r'{"note": "softmax $q_i = \frac{\text{exp}(z_i/T)}{Z}$ and \big( \right)", "n": 3}'
    parsed = json.loads(raw_json)
    assert "\f" in parsed["note"] and "\t" in parsed["note"]  # corrupted...

    repaired = _repair_latex(parsed)
    assert repaired["note"] == r"softmax $q_i = \frac{\text{exp}(z_i/T)}{Z}$ and \big( \right)"  # ...fixed
    assert repaired["n"] == 3  # non-strings untouched


def test_correctly_escaped_latex_is_unchanged():
    parsed = json.loads(r'{"eq": "\\frac{1}{N}"}')
    assert _repair_latex(parsed) == {"eq": r"\frac{1}{N}"}
