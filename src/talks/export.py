"""
export.py - write a GeneratedTalk as a readable Markdown file:
the request, every slide (bullets, equations, speaker notes), the full script,
the checks and the sources.
"""

from datetime import datetime
from pathlib import Path

from src.talks.result import GeneratedTalk


def talk_to_markdown(result: GeneratedTalk, include_prompt: bool = False) -> str:
    r, talk = result.request, result.talk
    lines = [
        f"# {talk.title}",
        "",
        f"_Generated {datetime.now():%Y-%m-%d %H:%M}_",
        "",
        "## Request",
        f"- **Topic:** {r.topic}" + (f"  |  **Focus:** {r.focus}" if r.focus else ""),
        f"- **Paper:** {r.paper_id or 'all papers'}  |  **Audience:** {r.audience}  |  **Style:** {r.style}",
        f"- **Slides:** {r.n_slides}  |  **Notes per slide:** {r.notes_per_slide}"
        f"  |  **Preserve equations:** {'yes' if r.preserve_equations else 'no'}"
        f"  |  **Script:** {r.length} (~{r.target_words} words)",
        "",
        "## Slides",
    ]
    for number, slide in enumerate(talk.slides, start=1):
        lines += ["", f"### Slide {number}: {slide.title}", ""]
        lines += [f"- {bullet}" for bullet in slide.bullets]
        for equation in slide.equations:
            lines += ["", f"$$ {equation} $$"]
        lines += ["", "**Speaker notes:**", ""]
        lines += [f"{i}. {note}" for i, note in enumerate(slide.speaker_notes, start=1)]

    lines += [
        "", "## Full speaker script", "", talk.script, "",
        "## Checks",
        f"- Attempts: {result.attempts} ({'right first time' if result.attempts == 1 else 'self-corrected once'})",
        f"- Script words: {len(talk.script.split())} (target ~{r.target_words})",
        f"- Remaining problems: {'none' if not result.problems else ''}",
    ]
    lines += [f"  - {p}" for p in result.problems]
    lines += ["", "## Sources given to the LLM", ""]
    for chunk in result.sources:
        mark = "cited" if chunk.chunk_id in result.cited_ids else "not cited"
        math = ", equation" if chunk.has_math else ""
        lines.append(f"- `{chunk.chunk_id}` — page {chunk.page}, {chunk.section} ({mark}{math})")
    if include_prompt:
        lines += ["", "## Full prompt", "", "```text", result.prompt, "```"]
    return "\n".join(lines) + "\n"


def save_talk_markdown(result: GeneratedTalk, directory: Path, include_prompt: bool = False, extra: str = "") -> Path:
    """`extra` = more Markdown to add at the end (e.g. the provenance report)."""
    directory.mkdir(parents=True, exist_ok=True)
    r = result.request
    path = directory / f"talk_{r.paper_id or 'all'}_{r.n_slides}slides_{r.audience}_{r.style}.md"
    path.write_text(talk_to_markdown(result, include_prompt) + extra, encoding="utf-8")
    return path
