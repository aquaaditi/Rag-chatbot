"""
log.py - record every turn of the conversation and save it to logs/.

Two files per session (both rewritten after every turn, so nothing is lost):
    logs/session_<date>_<time>.json  - machine-readable (for evaluation later)
    logs/session_<date>_<time>.md    - human-readable (the evidence for the task)
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Turn:
    time: str
    user: str
    action: str  # what the parser understood: create / edit / show / undo / ...
    reply: str  # the bot's Markdown reply
    version: int | None  # talk version after this turn


class ConversationLog:
    def __init__(self, directory: Path):
        self.turns: list[Turn] = []
        started = datetime.now()
        self.started = started.strftime("%Y-%m-%d %H:%M")
        name = f"session_{started:%Y%m%d_%H%M%S}"
        self.json_path = directory / f"{name}.json"
        self.md_path = directory / f"{name}.md"

    def add(self, user: str, action: str, reply: str, version: int | None) -> None:
        self.turns.append(Turn(datetime.now().strftime("%H:%M:%S"), user, action, reply, version))

    def save(self) -> None:
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"started": self.started, "turns": [asdict(t) for t in self.turns]}
        self.json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self.md_path.write_text(self.to_markdown(), encoding="utf-8")

    def to_markdown(self) -> str:
        lines = [f"# Conversation log ({self.started})", ""]
        for i, turn in enumerate(self.turns, start=1):
            version = f", talk v{turn.version}" if turn.version else ""
            lines += [
                f"## Turn {i} ({turn.time}, action: {turn.action}{version})",
                "",
                f"**User:** {turn.user}",
                "",
                "**Bot:**",
                "",
                turn.reply,
                "",
                "---",
                "",
            ]
        return "\n".join(lines)
