"""
claim.py - split generated text into CLAIMS: the smallest pieces we can check.

A claim is one sentence (of a script, a slide bullet or a speaker note) plus
the chunk IDs it cites. Example:

    "Distillation transfers knowledge to a small model [P3_p1_c03]."
    -> Claim(text="Distillation transfers knowledge to a small model.",
             cited_ids=["P3_p1_c03"], location="script")
"""

import re
from dataclasses import dataclass

from src.chunking.sentences import split_sentences
from src.generation.citations import find_citations
from src.generation.script_result import GeneratedScript
from src.talks.result import GeneratedTalk

# A [...] group that contains at least one chunk ID, e.g. [P3_p2_c06] or [P1_p2_c01, P3_p2_c06]
CITATION_GROUP = re.compile(r"\s*\[[^\[\]]*P\d+_[ps]\d+_c\d+[^\[\]]*\]")


@dataclass
class Claim:
    text: str  # the sentence without its citations
    cited_ids: list[str]
    location: str  # where it is: "script", "slide 2 · bullet 1", "slide 2 · note 3"


def strip_citations(text: str) -> str:
    return CITATION_GROUP.sub("", text).strip()


def extract_claims(text: str, location: str) -> list[Claim]:
    """One claim per sentence. Questions ("Why is it so fast?") are not claims."""
    claims: list[Claim] = []
    for sentence in split_sentences(text):
        # A citation written after the full stop ("... model. [P3_p1_c03]") ends up at the
        # start of the next sentence - give it back to the sentence it belongs to.
        leading = re.match(r"^(\s*\[[^\[\]]*\])+", sentence)
        if leading and claims and find_citations(leading.group(0)):
            claims[-1].cited_ids += [c for c in find_citations(leading.group(0)) if c not in claims[-1].cited_ids]
            sentence = sentence[leading.end():]

        clean = strip_citations(sentence)
        if len(clean.split()) >= 3 and not clean.endswith("?"):
            claims.append(Claim(clean, find_citations(sentence), location))
    return claims


def claims_from_script(result: GeneratedScript) -> list[Claim]:
    return extract_claims(result.text, "script")


def claims_from_talk(result: GeneratedTalk) -> list[Claim]:
    claims: list[Claim] = []
    for s, slide in enumerate(result.talk.slides, start=1):
        for b, bullet in enumerate(slide.bullets, start=1):
            claims += extract_claims(bullet, f"slide {s} · bullet {b}")
        for n, note in enumerate(slide.speaker_notes, start=1):
            claims += extract_claims(note, f"slide {s} · note {n}")
    claims += extract_claims(result.talk.script, "script")
    return claims
