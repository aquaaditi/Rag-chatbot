"""
report.py - run every OUTPUT check on generated text and collect the issues.

    report = check_output(fields, audience="press", sources_text=..., whole_talk=..., reading_ease=48)
    report.blocked   -> True if anything must not be shown (offensive words)
    report.issues    -> [SafetyIssue("acronym", "slide 2 · bullet 1", "CNN is not spelled out"), ...]

`fields` are (where, text) pairs, e.g. ("slide 2 · bullet 1", "..."), so every
issue says exactly where it is.
"""

from dataclasses import dataclass, field

from src.safety.accessibility import LAY_AUDIENCES, long_sentences, readability_problem, undefined_acronyms
from src.safety.inclusive import find_non_inclusive
from src.safety.offensive import find_offensive, words_in


@dataclass
class SafetyIssue:
    kind: str  # "offensive" | "inclusive" | "long sentence" | "acronym" | "readability"
    where: str  # "slide 2 · bullet 1", "script", ...
    detail: str
    blocking: bool = False  # True = do not show this text to the user


@dataclass
class SafetyReport:
    issues: list[SafetyIssue] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(issue.blocking for issue in self.issues)


def check_output(
    fields: list[tuple[str, str]], audience: str, sources_text: str,
    whole_talk: str = "", reading_ease: float | None = None,
) -> SafetyReport:
    allowed = words_in(sources_text)  # words the paper itself uses are not "offensive" (names, quotes)
    whole_talk = whole_talk or " ".join(text for _, text in fields)
    issues = []
    for where, text in fields:
        if bad := find_offensive(text, allowed):
            issues.append(SafetyIssue("offensive", where, f"offensive wording: {', '.join(bad)}", blocking=True))
        for term, alternative in find_non_inclusive(text):
            issues.append(SafetyIssue("inclusive", where, f'"{term}" - consider "{alternative}"'))
        if "equation" in where:
            continue  # LaTeX: no sentences or acronyms to check
        for sentence in long_sentences(text):
            issues.append(SafetyIssue("long sentence", where, f"{len(sentence.split())} words: \"{sentence[:60]}...\""))
        if audience in LAY_AUDIENCES and (acronyms := undefined_acronyms(text, whole_talk)):
            issues.append(SafetyIssue("acronym", where, f"not spelled out for {audience}: {', '.join(acronyms)}"))
    if reading_ease is not None and (problem := readability_problem(reading_ease, audience)):
        issues.append(SafetyIssue("readability", "overall", problem))
    return SafetyReport(issues)
