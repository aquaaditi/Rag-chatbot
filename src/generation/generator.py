"""
generator.py - RAG in one function: retrieve -> build prompt -> ask the LLM -> check citations.

    generator = ScriptGenerator(Retriever.load())
    script = generator.generate(ScriptRequest("the main idea and results", audience="policymakers",
                                              length="90s", style="plain_english", paper_id="P3"))
    print(script.text)

The retriever and the LLM function are passed in (not created inside), so tests
can swap in fakes and run without the network or the embedding model.
"""

from collections.abc import Callable

from src.chunking import Chunk
from src.generation.citations import find_citations, unknown_citations
from src.generation.context import format_sources
from src.generation.options import ScriptRequest
from src.generation.prompts import SYSTEM_PROMPT, build_script_prompt
from src.generation.script_result import GeneratedScript
from src.llm import ask_llm
from src.retrieval import Retriever


class ScriptGenerator:
    def __init__(self, retriever: Retriever, llm: Callable[..., str] = ask_llm):
        self._retriever = retriever
        self._llm = llm

    def generate(self, request: ScriptRequest) -> GeneratedScript:
        sources = self.select_sources(request)
        prompt = build_script_prompt(request, format_sources(sources))
        text = self._llm(prompt, system_prompt=SYSTEM_PROMPT).strip()

        cited = find_citations(text)
        return GeneratedScript(
            request=request,
            text=text,
            sources=sources,
            prompt=prompt,
            cited_ids=cited,
            unknown_ids=unknown_citations(cited, [c.chunk_id for c in sources]),
        )

    def select_sources(self, request: ScriptRequest) -> list[Chunk]:
        """The paper's abstract first (a reliable summary of the whole paper),
        then the chunks that best match the topic - without duplicates."""
        abstract = [
            c for c in self._retriever.chunks
            if c.section == "Abstract" and (request.paper_id is None or c.paper_id == request.paper_id)
        ]
        retrieved = [
            r.chunk for r in self._retriever.retrieve(request.topic, k=request.n_chunks, paper_id=request.paper_id)
        ]
        selected: list[Chunk] = []
        for chunk in abstract + retrieved:
            if chunk not in selected:
                selected.append(chunk)
        return selected
