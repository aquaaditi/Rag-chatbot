"""
Conversation stage:  chat messages  ->  a talk that is created, edited and undone
step by step, with every change tracked (old vs new + why) and logged

    commands.py      understand a message (fast path + Gemini structured output)
    edit_prompts.py  DELTA-ANCHORED edit prompts (only the changed part + its sources)
    editing.py       Editor: edit one slide / the script / the whole talk -> new talk + reason
    diff.py          the delta: field-by-field and word-by-word (~~old~~ **new**)
    readability.py   Flesch reading ease (measures "less technical")
    versions.py      Version / Change / Metrics + VersionHistory (undo)
    formatting.py    Markdown replies
    log.py           ConversationLog -> logs/session_*.json + .md
    session.py       ChatSession.handle(message) -> reply

Other parts (the CLI, the Day 8 chat UI) only need `ChatSession`.
"""

from src.conversation.session import ChatSession

__all__ = ["ChatSession"]
