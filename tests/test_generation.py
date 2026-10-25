"""
Tests for the generation stage (src/generation/).

The LLM and the retriever are replaced by small fakes, so these tests run
instantly, need no internet and cost nothing.

Run:  pytest -v
"""

import pytest

from src.chunking import Chunk
from src.generation import ScriptGenerator, ScriptRequest
from src.generation.citations import find_citations, unknown_citations
from src.generation.prompts import build_script_prompt
from src.retrieval import RetrievedChunk


def make_chunk(chunk_id, section="2 Method", paper_id="P1"):
    return Chunk(chunk_id, paper_id, 2, section, f"text of {chunk_id}", False, 3)


class FakeRetriever:
    """Behaves like Retriever, but returns fixed chunks."""

    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, question, k=5, paper_id=None, mode="hybrid"):
        found = [c for c in self.chunks if c.section != "Abstract" and paper_id in (None, c.paper_id)]
        return [RetrievedChunk(c, 1.0, i) for i, c in enumerate(found[:k], start=1)]


# ---------------------------------------------------------------- options.py


def test_length_becomes_a_word_target():
    assert ScriptRequest("x", length="30s").target_words == 75
    assert ScriptRequest("x", length="90s").target_words == 225
    assert ScriptRequest("x", length="5min").target_words == 750


def test_unknown_audience_is_rejected():
    with pytest.raises(ValueError):
        ScriptRequest("x", audience="aliens")


# ---------------------------------------------------------------- prompts.py


def test_prompt_contains_every_parameter():
    request = ScriptRequest("distillation", audience="policymakers", length="30s", style="press_release",
                            change_instruction="make it more visual")
    prompt = build_script_prompt(request, "[P3_p2_c06] some source")
    assert "policymakers" in prompt
    assert "about 75 words" in prompt
    assert "press release" in prompt
    assert "CHANGE REQUEST: make it more visual" in prompt
    assert "[P3_p2_c06] some source" in prompt


def test_first_draft_has_no_change_block():
    prompt = build_script_prompt(ScriptRequest("x"), "sources")
    assert "CHANGE REQUEST" not in prompt


# ---------------------------------------------------------------- citations.py


def test_find_citations_handles_all_formats():
    text = "A [P1_p2_c01]. B [P1_p2_c01][P3_p2_c06]. C [P2_p1_c03, P2_s1_c01]. Not [1] or [Table 2]."
    assert find_citations(text) == ["P1_p2_c01", "P3_p2_c06", "P2_p1_c03", "P2_s1_c01"]


def test_unknown_citations_are_flagged():
    assert unknown_citations(["P1_p2_c01", "P9_p9_c99"], ["P1_p2_c01"]) == ["P9_p9_c99"]


# ---------------------------------------------------------------- generator.py


def test_generator_puts_abstract_first_and_checks_citations():
    chunks = [make_chunk("P1_p1_c02", section="Abstract"), make_chunk("P1_p2_c01"), make_chunk("P2_p2_c01", paper_id="P2")]
    sent = {}

    def fake_llm(prompt, system_prompt=""):
        sent["prompt"] = prompt
        return "The model works [P1_p2_c01]. It is great [P7_p1_c01]."

    result = ScriptGenerator(FakeRetriever(chunks), llm=fake_llm).generate(ScriptRequest("method", paper_id="P1"))

    assert result.source_ids == ["P1_p1_c02", "P1_p2_c01"]  # abstract first, other paper excluded
    assert "[P1_p1_c02]" in sent["prompt"]  # sources really were sent to the LLM
    assert result.cited_ids == ["P1_p2_c01", "P7_p1_c01"]
    assert result.unknown_ids == ["P7_p1_c01"]  # the invented citation is caught
