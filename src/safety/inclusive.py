"""
inclusive.py - suggest inclusive alternatives for exclusionary words.

    "manpower" -> "workforce", "blacklist" -> "blocklist", "crazy" -> "surprising"

These are not offensive enough to block, so they only become warnings with a suggestion.
"""

import re

ALTERNATIVES = {
    "manpower": "workforce / staff",
    "mankind": "humanity",
    "man-made": "artificial / human-made",
    "chairman": "chair",
    "guys": "everyone",
    "blacklist": "blocklist",
    "whitelist": "allowlist",
    "sanity check": "quick check",
    "crazy": "surprising",
    "insane": "remarkable",
    "lame": "weak",
    "crippled": "limited",
    "dumb": "simple",
}

_PATTERN = re.compile(r"\b(" + "|".join(re.escape(term) for term in ALTERNATIVES) + r")\b", re.IGNORECASE)


def find_non_inclusive(text: str) -> list[tuple[str, str]]:
    """[(word found, suggested alternative), ...] in order, without repeats."""
    found = dict.fromkeys(m.group(1).lower() for m in _PATTERN.finditer(text))
    return [(term, ALTERNATIVES[term]) for term in found]
