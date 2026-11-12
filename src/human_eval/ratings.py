"""
ratings.py - one rater's answers, saved in eval/human/ratings_<rater>.json after EVERY item,
so quitting halfway loses nothing and the next run continues where it stopped.

    {"rater": "aditi",
     "scripts": {"P3_press_..._90s": {"factuality": 4, "audience_fit": 5, "helpfulness": 4, "comment": ""}},
     "claims":  {"P3_press_..._90s#4": {"label": "hype", "comment": ""}}}
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RaterFile:
    rater: str
    path: Path
    scripts: dict[str, dict] = field(default_factory=dict)
    claims: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def open(cls, rater: str, directory: Path) -> "RaterFile":
        if not re.fullmatch(r"[a-z0-9_-]+", rater):
            raise ValueError("rater name: lowercase letters, digits, - and _ only (e.g. 'aditi')")
        path = directory / f"ratings_{rater}.json"
        if not path.exists():
            return cls(rater, path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(rater, path, data["scripts"], data["claims"])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"rater": self.rater, "scripts": self.scripts, "claims": self.claims}
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_all(directory: Path) -> list[RaterFile]:
    return [RaterFile.open(p.stem.removeprefix("ratings_"), directory) for p in sorted(directory.glob("ratings_*.json"))]
