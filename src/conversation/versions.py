"""
versions.py - keep every version of the talk, with the change that made it.

    v1  created
    v2  slide 2: "make it less technical"   (reason, diff, before/after metrics)
    v3  script:  "shorten to 90 seconds"
    undo -> back to v2
"""

from dataclasses import dataclass, field

from src.conversation.diff import FieldChange
from src.talks import Talk


@dataclass
class Metrics:
    """Measured on the part of the talk that was edited."""
    reading_ease: float  # Flesch: higher = easier to read
    supported_share: float  # provenance: share of claims supported by their cited source
    citation_coverage: float  # provenance: share of claims with a valid citation
    n_words: int


@dataclass
class Change:
    instruction: str  # what the user asked, e.g. "make it simpler and less technical"
    target: str  # "slide 2", "script", "whole talk"
    reason: str  # the LLM's explanation of what it changed and why
    field_changes: list[FieldChange] = field(default_factory=list)
    before: Metrics | None = None
    after: Metrics | None = None
    attempts: int = 1  # 2 = the first attempt missed its measured goal and was retried
    unmet_goal: str | None = None  # set if the goal was still missed after the retry


@dataclass
class Version:
    number: int
    talk: Talk
    change: Change | None  # None for the first version


class VersionHistory:
    def __init__(self):
        self.versions: list[Version] = []

    @property
    def current(self) -> Version | None:
        return self.versions[-1] if self.versions else None

    def add(self, talk: Talk, change: Change | None = None) -> Version:
        version = Version(len(self.versions) + 1, talk, change)
        self.versions.append(version)
        return version

    def undo(self) -> Version | None:
        """Remove the latest version (never the first one). Returns the removed version."""
        if len(self.versions) <= 1:
            return None
        return self.versions.pop()

    def reset(self) -> None:
        self.versions.clear()
