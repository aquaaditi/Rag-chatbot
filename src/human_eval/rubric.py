"""
rubric.py - the questions a human rater answers, with a description for every score.

Scripts get 1-5 on the task's three criteria. Single claims get one of three labels.
Writing down what each score MEANS makes raters (and the same rater on another day)
score the same way - without it, one person's "4" is another person's "3".
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Criterion:
    name: str
    question: str
    scale: dict[int, str]  # anchors: what a 5, 3 and 1 mean


CRITERIA = [
    Criterion("factuality", "Is everything it says true to the paper?", {
        5: "everything correct",
        3: "mostly correct, a small slip or exaggeration",
        1: "major errors or invented facts",
    }),
    Criterion("audience_fit", "Is it right for THIS audience (words, depth, tone)?", {
        5: "exactly right for them",
        3: "OK, but parts are too technical or too simple",
        1: "written for the wrong audience",
    }),
    Criterion("helpfulness", "Would you use it as a 90-second talk?", {
        5: "use it as it is",
        3: "usable after some editing",
        1: "start over",
    }),
]

# key the rater types -> label
CLAIM_LABELS = {
    "t": "true",  # the source says this (a paraphrase is fine)
    "h": "hype",  # the idea is in the source, but exaggerated or with added opinion ("striking")
    "w": "wrong",  # the source does not say this, or says something different
    "n": "no_claim",  # says nothing about the paper ("The sources do not mention costs.")
}
CLAIM_HELP = {
    "true": "the source says this (a paraphrase in simpler words is fine)",
    "hype": "the idea is there, but exaggerated or with added opinion ('the results are striking')",
    "wrong": "the source does not say this, or says something different",
    "no_claim": "not a claim about the paper, e.g. 'The sources do not mention costs.'",
}


def rubric_text() -> str:
    lines = []
    for c in CRITERIA:
        anchors = " · ".join(f"{score} = {meaning}" for score, meaning in c.scale.items())
        lines.append(f"  {c.name}: {c.question}\n      {anchors}  (2 and 4 are in between)")
    return "\n".join(lines)


def claim_help_text() -> str:
    return "\n".join(f"  {key} = {label}: {CLAIM_HELP[label]}" for key, label in CLAIM_LABELS.items())
