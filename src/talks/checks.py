"""
checks.py - does the generated talk follow the request?

Returns a list of problems in plain English (empty list = all good).
The generator sends these problems back to the LLM for one retry.
"""

from src.chunking.sentences import split_sentences
from src.generation.citations import find_citations, unknown_citations
from src.talks.request import TalkRequest
from src.talks.schema import Talk

SCRIPT_LENGTH_TOLERANCE = 0.35  # the script may be up to 35% shorter or longer than the target
# Transitions like "Now let's look at the results." need no citation, so not 100%
MIN_SCRIPT_CITED_SHARE = 0.6


def all_text(talk: Talk) -> str:
    """Every piece of text in the talk, joined - used to find citations."""
    parts = [talk.script]
    for slide in talk.slides:
        parts += slide.bullets + slide.speaker_notes
    return "\n".join(parts)


def check_talk(talk: Talk, request: TalkRequest, source_ids: list[str]) -> list[str]:
    problems = []

    if len(talk.slides) != request.n_slides:
        problems.append(f"The talk has {len(talk.slides)} slides; exactly {request.n_slides} are required.")

    for number, slide in enumerate(talk.slides, start=1):
        if len(slide.speaker_notes) != request.notes_per_slide:
            problems.append(
                f"Slide {number} has {len(slide.speaker_notes)} speaker notes; "
                f"exactly {request.notes_per_slide} are required."
            )
        if not 2 <= len(slide.bullets) <= 6:
            problems.append(f"Slide {number} has {len(slide.bullets)} bullets; use 3-5.")

    if request.preserve_equations and not any(slide.equations for slide in talk.slides):
        problems.append("No slide contains an equation, but key equations must be preserved.")

    n_words, target = len(talk.script.split()), request.target_words
    if abs(n_words - target) > SCRIPT_LENGTH_TOLERANCE * target:
        problems.append(f"The script has {n_words} words; it should have about {target}.")

    cited_share = share_of_sentences_cited(talk.script)
    if cited_share < MIN_SCRIPT_CITED_SHARE:
        problems.append(
            f"Only {cited_share:.0%} of the script's sentences cite a source. Every factual "
            "sentence in the script must end with its chunk ID(s) in square brackets."
        )

    invented = unknown_citations(find_citations(all_text(talk)), source_ids)
    if invented:
        problems.append(f"These cited IDs are not in the SOURCES: {', '.join(invented)}. Only cite given IDs.")

    return problems


def share_of_sentences_cited(text: str) -> float:
    """Fraction of sentences with at least one [chunk ID]. (Day 6 measures this properly.)"""
    sentences = [s for s in split_sentences(text) if len(s.split()) > 3]
    if not sentences:
        return 0.0
    return sum(bool(find_citations(s)) for s in sentences) / len(sentences)
