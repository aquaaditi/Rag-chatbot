"""
input_guard.py - check a user's chat message BEFORE it reaches the LLM.

    check_message("make #2 less technical", vocabulary)          -> None (fine)
    check_message("ignore all previous instructions and ...")   -> "This looks like ..." (refused)

Refusing early is cheaper and safer than asking the LLM and filtering its answer.
"""

from src import config
from src.safety.injection import find_injection
from src.safety.offensive import find_offensive


def check_message(message: str, vocabulary: set[str] = frozenset()) -> str | None:
    """None if the message is fine, otherwise the reason it is refused.

    `vocabulary` = words of the papers, so asking about an author like "Wang" is not refused."""
    if len(message) > config.MAX_MESSAGE_CHARS:
        return f"That message is too long ({len(message)} characters, the limit is {config.MAX_MESSAGE_CHARS})."
    if phrase := find_injection(message):
        return (f"This looks like an attempt to change my instructions (\"{phrase}\"). "
                "I can only create and edit talks from the papers.")
    if bad := find_offensive(message, vocabulary):
        return f"Let's keep it respectful - please rephrase without: {', '.join(bad)}."
    return None
