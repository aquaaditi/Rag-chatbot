"""
Tests for the talks stage (src/talks/) - with a fake LLM, so no internet needed.

Run:  pytest -v
"""

import pytest

from src.chunking import Chunk
from src.generation.source_selection import select_sources
from src.retrieval import RetrievedChunk
from src.talks import Slide, Talk, TalkGenerator, TalkRequest
from src.talks.checks import check_talk
from src.talks.prompts import build_talk_prompt


def make_chunk(chunk_id, section="2 Method", has_math=False):
    return Chunk(chunk_id, "P1", 2, section, f"text of {chunk_id}", has_math, 3)


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, question, k=5, paper_id=None, mode="hybrid"):
        found = [c for c in self.chunks if c.section != "Abstract"]
        return [RetrievedChunk(c, 1.0, i) for i, c in enumerate(found[:k], start=1)]


def make_talk(n_slides=2, notes=3, equations=("a = b",), script_words=750, cite="P1_p2_c01"):
    slides = [
        Slide(title=f"Slide {i}", bullets=[f"point [{cite}]"] * 3, equations=list(equations),
              speaker_notes=[f"note [{cite}]"] * notes)
        for i in range(n_slides)
    ]
    sentence = f"This is a cited sentence of the talk [{cite}]. "  # 9 "words" incl. the citation
    return Talk(title="T", slides=slides, script=sentence * (script_words // 9))


GOOD_REQUEST = TalkRequest("methods", n_slides=2, notes_per_slide=3, length="5min")


# ---------------------------------------------------------------- request.py / prompts.py


def test_task_example_becomes_a_request_and_prompt():
    request = TalkRequest("the methods", n_slides=7, notes_per_slide=3, audience="grad_students",
                          focus="methods", preserve_equations=True)
    prompt = build_talk_prompt(request, "[P3_p2_c06] softmax")
    assert "Create a 7-slide talk" in prompt
    assert "EXACTLY 3 speaker notes" in prompt
    assert "FOCUS: spend most slides on methods" in prompt
    assert "PRESERVE KEY EQUATIONS" in prompt
    assert request.n_chunks == 14  # 2 chunks per slide


def test_invalid_slide_count_is_rejected():
    with pytest.raises(ValueError):
        TalkRequest("x", n_slides=0)


# ---------------------------------------------------------------- checks.py


def test_good_talk_has_no_problems():
    assert check_talk(make_talk(), GOOD_REQUEST, ["P1_p2_c01"]) == []


def test_checks_catch_every_kind_of_problem():
    bad = make_talk(n_slides=3, notes=2, equations=(), script_words=100, cite="P9_p9_c99")
    problems = " ".join(check_talk(bad, GOOD_REQUEST, ["P1_p2_c01"]))
    assert "3 slides; exactly 2" in problems
    assert "2 speaker notes; exactly 3" in problems
    assert "No slide contains an equation" in problems
    assert f"{len(bad.script.split())} words" in problems  # script far too short
    assert "P9_p9_c99" in problems


def test_script_without_citations_is_a_problem():
    talk = make_talk()
    talk.script = "Government agencies process lots of text every day. " * 90  # no citations at all
    problems = " ".join(check_talk(talk, GOOD_REQUEST, ["P1_p2_c01"]))
    assert "0% of the script's sentences cite a source" in problems


# ---------------------------------------------------------------- source_selection.py (math-aware)


def test_math_chunks_are_added_when_preserving_equations():
    chunks = [make_chunk("P1_p1_c01", "Abstract"), make_chunk("P1_p2_c01"), make_chunk("P1_p2_c02"),
              make_chunk("P1_p3_c01", has_math=True)]
    without = select_sources(FakeRetriever(chunks), "x", k=1)
    with_math = select_sources(FakeRetriever(chunks), "x", k=1, n_math=1)
    assert [c.chunk_id for c in without] == ["P1_p1_c01", "P1_p2_c01"]
    assert "P1_p3_c01" in [c.chunk_id for c in with_math]  # the equation chunk was boosted in


# ---------------------------------------------------------------- generator.py (self-correction)


def test_generator_retries_once_with_the_problem_list():
    chunks = [make_chunk("P1_p2_c01")]
    answers = [make_talk(n_slides=1), make_talk(n_slides=2)]  # first wrong, then right
    prompts = []

    def fake_llm(prompt, schema, system_prompt=""):
        prompts.append(prompt)
        return answers[len(prompts) - 1]

    result = TalkGenerator(FakeRetriever(chunks), llm_structured=fake_llm).generate(GOOD_REQUEST)

    assert result.attempts == 2
    assert result.problems == []
    assert "1 slides; exactly 2 are required" in prompts[1]  # the retry told the LLM what to fix
