"""
export.py - write a GeneratedScript as a readable Markdown file
(input -> output -> sources -> checks), used for the examples/ folder.
"""

from datetime import datetime
from pathlib import Path

from src.generation.script_result import GeneratedScript


def script_to_markdown(result: GeneratedScript, include_prompt: bool = False) -> str:
    r = result.request
    lines = [
        f"# Script: {r.topic}",
        "",
        f"_Generated {datetime.now():%Y-%m-%d %H:%M}_",
        "",
        "## Input",
        f"- **Topic:** {r.topic}",
        f"- **Paper:** {r.paper_id or 'all papers'}",
        f"- **Audience:** {r.audience}  |  **Length:** {r.length} (target ~{r.target_words} words)"
        f"  |  **Style:** {r.style}",
        "",
        "## Output",
        "",
        result.text,
        "",
        "## Checks",
        f"- Words: {result.n_words} (target ~{r.target_words})",
        f"- Chunks cited: {len(result.cited_ids)} of {len(result.sources)} provided",
        f"- Unknown (invented) citations: {result.unknown_ids or 'none'}",
        "",
        "## Sources given to the LLM",
        "",
    ]
    for chunk in result.sources:
        mark = "✅ cited" if chunk.chunk_id in result.cited_ids else "not cited"
        lines.append(f"- `{chunk.chunk_id}` — page {chunk.page}, {chunk.section} ({mark})")
    if include_prompt:
        lines += ["", "## Full prompt", "", "```text", result.prompt, "```"]
    return "\n".join(lines) + "\n"


def save_markdown(result: GeneratedScript, directory: Path, include_prompt: bool = False, extra: str = "") -> Path:
    """`extra` = more Markdown to add at the end (e.g. the provenance report)."""
    directory.mkdir(parents=True, exist_ok=True)
    r = result.request
    name = f"{r.paper_id or 'all'}_{r.audience}_{r.length}_{r.style}.md"
    path = directory / name
    path.write_text(script_to_markdown(result, include_prompt) + extra, encoding="utf-8")
    return path
