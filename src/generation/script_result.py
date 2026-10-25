"""
script_result.py - the GeneratedScript data type: the output of the generation stage.
It keeps everything needed to explain and check an answer: the request, the exact
prompt, the chunks that were used and the citations found in the text.
"""

from dataclasses import dataclass

from src.chunking import Chunk
from src.generation.options import ScriptRequest


@dataclass
class GeneratedScript:
    request: ScriptRequest
    text: str
    sources: list[Chunk]  # the chunks that were put in the prompt
    prompt: str  # the exact prompt sent to the LLM (for debugging / the report)
    cited_ids: list[str]  # chunk IDs found in the text
    unknown_ids: list[str]  # cited IDs that were not in the sources (should be empty!)

    @property
    def n_words(self) -> int:
        return len(self.text.split())

    @property
    def source_ids(self) -> list[str]:
        return [c.chunk_id for c in self.sources]
