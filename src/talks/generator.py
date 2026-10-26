"""
generator.py - build a whole slide talk with RAG and structured output.

    1. select sources   - abstract + top chunks + math chunks (math-aware)
    2. build the prompt - talk template + shared grounding rules
    3. ask the LLM      - JSON that must match the Talk schema
    4. check            - slide count, notes per slide, equations, length, citations
    5. self-correct     - if there are problems, ask ONCE more with the problem list

    generator = TalkGenerator(Retriever.load())
    result = generator.generate(TalkRequest("the methods", n_slides=7, paper_id="P3"))
"""

from collections.abc import Callable

from src.generation.citations import find_citations
from src.generation.context import format_sources
from src.generation.source_selection import select_sources
from src.llm import ask_llm_structured
from src.retrieval import Retriever
from src.talks.checks import all_text, check_talk
from src.talks.prompts import TALK_SYSTEM_PROMPT, build_retry_prompt, build_talk_prompt
from src.talks.request import TalkRequest
from src.talks.result import GeneratedTalk
from src.talks.schema import Talk

MAX_ATTEMPTS = 2  # first try + one self-correction


class TalkGenerator:
    def __init__(self, retriever: Retriever, llm_structured: Callable[..., Talk] = ask_llm_structured):
        self._retriever = retriever
        self._llm = llm_structured

    def generate(self, request: TalkRequest) -> GeneratedTalk:
        sources = select_sources(
            self._retriever, request.topic, k=request.n_chunks,
            paper_id=request.paper_id, n_math=request.n_math_chunks,
        )
        source_ids = [c.chunk_id for c in sources]
        prompt = build_talk_prompt(request, format_sources(sources))

        current_prompt, attempts = prompt, 0
        while True:
            attempts += 1
            talk = self._llm(current_prompt, schema=Talk, system_prompt=TALK_SYSTEM_PROMPT)
            problems = check_talk(talk, request, source_ids)
            if not problems or attempts >= MAX_ATTEMPTS:
                break
            current_prompt = build_retry_prompt(prompt, problems)

        return GeneratedTalk(
            request=request,
            talk=talk,
            sources=sources,
            prompt=prompt,
            problems=problems,
            attempts=attempts,
            cited_ids=find_citations(all_text(talk)),
        )
