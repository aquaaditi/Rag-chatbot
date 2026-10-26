"""
Talks stage:  TalkRequest + retrieved chunks  ->  slide deck (JSON) with bullets,
equations, speaker notes and a full script - all citing [chunk IDs]

    schema.py     Slide / Talk: the JSON shape the LLM must return (Pydantic)
    request.py    TalkRequest: slides, notes per slide, audience, focus, equations...
    prompts.py    talk prompt template + self-correction (retry) prompt
    checks.py     does the talk follow the request? -> list of problems
    result.py     GeneratedTalk data type
    generator.py  TalkGenerator: sources -> prompt -> JSON -> check -> retry once
    export.py     save a talk as Markdown (examples/)

Reuses from src/generation/: options, grounding rules, source selection, citations.
"""

from src.talks.generator import TalkGenerator
from src.talks.request import TalkRequest
from src.talks.result import GeneratedTalk
from src.talks.schema import Slide, Talk

__all__ = ["GeneratedTalk", "Slide", "Talk", "TalkGenerator", "TalkRequest"]
