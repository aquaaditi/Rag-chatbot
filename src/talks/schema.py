"""
schema.py - the exact JSON shape the LLM must return for a talk.

These Pydantic models are sent to Gemini as the "response schema", so the
answer always has these fields. The descriptions are part of the schema and
act as extra instructions for each field.
"""

from pydantic import BaseModel, Field


class Slide(BaseModel):
    title: str = Field(description="Short slide title, at most 8 words, no citation.")
    bullets: list[str] = Field(
        description="3-5 short bullet points (at most ~15 words each). "
        "End each bullet with its source chunk ID(s) in square brackets, e.g. [P3_p2_c06]."
    )
    equations: list[str] = Field(
        description="Key equations shown on this slide, in LaTeX WITHOUT $ signs, "
        "e.g. q_i = \\frac{\\exp(z_i/T)}{\\sum_j \\exp(z_j/T)}. Empty list if the slide has none."
    )
    speaker_notes: list[str] = Field(
        description="What the presenter says for this slide, beyond the bullets. 1-3 sentences each, "
        "math as inline LaTeX $...$, each fact followed by its chunk ID(s) in square brackets."
    )


class Talk(BaseModel):
    title: str = Field(description="Title of the whole talk.")
    slides: list[Slide]
    script: str = Field(
        description="The full spoken script of the talk, covering the slides in order, as continuous "
        "text. Every factual sentence ends with its chunk ID(s) in square brackets."
    )
