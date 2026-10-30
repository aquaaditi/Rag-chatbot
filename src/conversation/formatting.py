"""
formatting.py - turn talks, slides and changes into Markdown chat replies.
(Markdown works in the terminal and in the chat UI of Day 8.)
"""

from src.conversation.diff import word_diff
from src.conversation.versions import Change, Metrics, Version
from src.talks import Slide, Talk

GROUNDING_DROP_WARNING = 0.20  # warn when supported claims fall by 20 percentage points or more


def render_slide(slide: Slide, number: int) -> str:
    lines = [f"**Slide {number}: {slide.title}**"]
    lines += [f"- {b}" for b in slide.bullets]
    lines += [f"  - equation: $${e}$$" for e in slide.equations]
    lines += [f"  - note {i}: {n}" for i, n in enumerate(slide.speaker_notes, start=1)]
    return "\n".join(lines)


def render_outline(talk: Talk, version: int) -> str:
    lines = [f"**{talk.title}** (v{version}, {len(talk.slides)} slides)"]
    lines += [f"{i}. {s.title}" + (" ∑" if s.equations else "") for i, s in enumerate(talk.slides, start=1)]
    lines += ["", f"Script: {len(talk.script.split())} words. Try: \"show #2\", \"make #2 less technical\", "
                  "\"shorten the script\", \"undo\", \"history\"."]
    return "\n".join(lines)


def render_change(version: Version) -> str:
    change = version.change
    lines = [
        f"✏️ **v{version.number}: {change.target}**: \"{change.instruction}\"",
        f"**Why it changed:** {change.reason}",
    ]
    if change.before and change.after:
        lines.append(_metrics_line(change.before, change.after))
    if change.before and change.after and \
            change.before.supported_share - change.after.supported_share >= GROUNDING_DROP_WARNING:
        lines.append(
            "⚠️ **Fewer claims closely match the sources now.** Simpler wording drifts from the paper's "
            "wording (and can lose precision) - check the new text against the sources."
        )
    if change.attempts > 1:
        lines.append("🔁 The first attempt missed its measured goal, so it was redone once.")
    if change.unmet_goal:
        lines.append(f"⚠️ **Goal not fully met:** {change.unmet_goal} You can ask again or \"undo\".")
    lines += ["", f"**What changed** ({len(change.field_changes)} fields; ~~removed~~ **added**):"]
    for fc in change.field_changes:
        if not fc.old:
            lines.append(f"- *{fc.where}* (added): **{fc.new}**")
        elif not fc.new:
            lines.append(f"- *{fc.where}* (removed): ~~{fc.old}~~")
        else:
            lines.append(f"- *{fc.where}*: {word_diff(fc.old, fc.new)}")
    return "\n".join(lines)


def render_history(versions: list[Version]) -> str:
    lines = ["**Versions:**"]
    for v in versions:
        if v.change is None:
            lines.append(f"- v{v.number}: created ({len(v.talk.slides)} slides)")
        else:
            lines.append(f"- v{v.number}: {v.change.target}: \"{v.change.instruction}\" "
                         f"({len(v.change.field_changes)} fields changed)")
    return "\n".join(lines)


def _metrics_line(before: Metrics, after: Metrics) -> str:
    return (
        f"**Measured:** readability {before.reading_ease:.0f} → {after.reading_ease:.0f} (higher = easier) · "
        f"supported claims {before.supported_share:.0%} → {after.supported_share:.0%} · "
        f"citation coverage {before.citation_coverage:.0%} → {after.citation_coverage:.0%} · "
        f"words {before.n_words} → {after.n_words}"
    )
