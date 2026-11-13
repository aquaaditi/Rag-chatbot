"""
generator.py - RAG in one function: retrieve -> build prompt -> ask the LLM -> fix the length -> check citations.

    generator = ScriptGenerator(Retriever.load())
    script = generator.generate(ScriptRequest("the main idea and results", audience="policymakers",
                                              length="90s", style="plain_english", paper_id="P3"))
    print(script.text)

The retriever and the LLM function are passed in (not created inside), so tests
can swap in fakes and run without the network or the embedding model.
"""

from collections.abc import Callable

from src.generation.citations import find_citations, spoken_words, unknown_citations
from src.generation.context import format_sources
from src.generation.options import ScriptRequest
from src.generation.prompts import SYSTEM_PROMPT, build_length_fix_prompt, build_script_prompt, length_range
from src.generation.script_result import GeneratedScript
from src.generation.source_selection import select_sources
from src.llm import ask_llm
from src.retrieval import Retriever


class ScriptGenerator:
    def __init__(self, retriever: Retriever, llm: Callable[..., str] = ask_llm):
        self._retriever = retriever
        self._llm = llm

    def generate(self, request: ScriptRequest) -> GeneratedScript:
        sources = select_sources(self._retriever, request.topic, k=request.n_chunks, paper_id=request.paper_id,
                                 mode=request.retrieval_mode)
        prompt = build_script_prompt(request, format_sources(sources))
        text = self._llm(prompt, system_prompt=SYSTEM_PROMPT).strip()
        text, retried = self._fix_length(text, prompt, request.target_words)

        cited = find_citations(text)
        return GeneratedScript(
            request=request,
            text=text,
            sources=sources,
            prompt=prompt,
            cited_ids=cited,
            unknown_ids=unknown_citations(cited, [c.chunk_id for c in sources]),
            length_retry=retried,
        )

    def _fix_length(self, text: str, prompt: str, target: int) -> tuple[str, bool]:
        """Outside the asked range -> ONE retry with the real word count; keep whichever is closer."""
        low, high = length_range(target)
        n_words = spoken_words(text)
        if low <= n_words <= high:
            return text, False
        retry = self._llm(build_length_fix_prompt(prompt, text, n_words, target), system_prompt=SYSTEM_PROMPT).strip()
        return (retry if abs(spoken_words(retry) - target) < abs(n_words - target) else text), True
