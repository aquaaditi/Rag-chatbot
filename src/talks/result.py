"""
result.py - the GeneratedTalk data type: the output of the talks stage.
"""

from dataclasses import dataclass

from src.chunking import Chunk
from src.talks.request import TalkRequest
from src.talks.schema import Talk


@dataclass
class GeneratedTalk:
    request: TalkRequest
    talk: Talk
    sources: list[Chunk]
    prompt: str  # the first prompt sent to the LLM
    problems: list[str]  # problems still left after the retry (empty = all checks passed)
    attempts: int  # 1 = right first time, 2 = needed the self-correction retry
    cited_ids: list[str]

    @property
    def source_ids(self) -> list[str]:
        return [c.chunk_id for c in self.sources]
