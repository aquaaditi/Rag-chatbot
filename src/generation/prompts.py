"""
prompts.py - the prompt template family.

One template, filled in with four parameters:
    {audience}            who will listen   (policymakers / grad students / press)
    {length}              how long          (30s / 90s / 5min -> a word target)
    {style}               how it sounds     (technical / plain-English / press release)
    {change_instruction}  an edit request   ("make it more visual") - empty for a first draft

The SYSTEM prompt holds the rules that never change: use only the sources,
cite every sentence, stay safe and accessible. This is what keeps RAG grounded.
"""

from src.generation.options import AUDIENCES, STYLES, ScriptRequest

# Rules 1-7 are shared by every output type (scripts here, slide decks in src/talks/)
GROUNDING_RULES = """Rules - follow all of them:
1. Use ONLY facts from the SOURCES below. Never add facts, numbers or claims from your own memory.
2. After EVERY sentence that states a fact, cite the source chunk ID(s) in square brackets,
   exactly as written in the sources, e.g. [P3_p2_c06] or [P3_p2_c06][P3_p3_c01].
3. If the sources do not contain something the user asked for, say so briefly instead of guessing.
4. Keep numbers exactly as they appear in the sources.
5. Write equations and math symbols in LaTeX inline, e.g. $q_i = \\exp(z_i/T) / \\sum_j \\exp(z_j/T)$.
   Plain numbers stay plain text: write 80% or 10M, not $80\\%$ or $10\\text{M}$.
   Equations in the sources were extracted from PDFs and may be scrambled: a big sum sign
   can appear as "P" or "X", and fractions lose their line ("-1 N N X n=1" means
   $-\\frac{1}{N}\\sum_{n=1}^{N}$). Rebuild them carefully and keep EVERY term.
6. Safety and accessibility: no offensive, discriminatory or sensational language;
   explain jargon for non-expert audiences; prefer short, clear sentences.
7. Adapting to the audience changes HOW you say things, never WHAT is true. Do not invent
   use cases, organisations (e.g. "government agencies"), scenarios, benefits or numbers that
   the sources do not state. A citation must point to a chunk that really says that thing."""

SYSTEM_PROMPT = f"""You write spoken scripts that explain research papers to a specific audience.

{GROUNDING_RULES}
8. Output only the script text - no title, no headings, no notes to the user."""

CHANGE_BLOCK = """
CHANGE REQUEST: {change_instruction}
Apply this change while keeping every rule above (still cite every fact).
"""


def change_block(change_instruction: str) -> str:
    """The CHANGE REQUEST part of a prompt - empty for a first draft."""
    return CHANGE_BLOCK.format(change_instruction=change_instruction) if change_instruction else ""


SCRIPT_TEMPLATE = """TASK: Write a spoken script about: {topic}

AUDIENCE: {audience}
STYLE: {style}
LENGTH: about {target_words} words ({length} when read aloud at 150 words per minute).
{change_block}
SOURCES:
{sources}"""


def build_script_prompt(request: ScriptRequest, sources: str) -> str:
    """Fill the template for one request. `sources` comes from context.format_sources()."""
    return SCRIPT_TEMPLATE.format(
        topic=request.topic,
        audience=AUDIENCES[request.audience],
        style=STYLES[request.style],
        target_words=request.target_words,
        length=request.length,
        change_block=change_block(request.change_instruction),
        sources=sources,
    )
