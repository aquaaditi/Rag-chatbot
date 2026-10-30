"""
Tests for the conversation stage (src/conversation/) - fake LLM + fake embedder,
so a whole conversation runs in a second, offline.

Run:  pytest -v
"""

import json
from dataclasses import replace

import numpy as np

from src.chunking import Chunk
from src.conversation import ChatSession
from src.conversation.commands import ParsedMessage, match_meta_command, to_talk_request
from src.conversation.diff import slide_changes, word_diff
from src.conversation.editing import ScriptEdit, SlideEdit, TalkEdit
from src.conversation.goals import check_goal, target_words
from src.conversation.versions import Metrics, VersionHistory
from src.retrieval import RetrievedChunk
from src.talks import Slide, Talk

CHUNKS = [
    Chunk("P3_p1_c01", "P3", 1, "Front matter", "Distilling the Knowledge in a Neural Network", False, 7),
    Chunk("P3_p2_c06", "P3", 2, "2 Distillation", "Softmax with a temperature produces soft targets.", True, 7),
]


class FakeEmbedder:
    def embed_passages(self, texts):
        rng = np.random.default_rng(0)
        v = rng.random((len(texts), 4)).astype(np.float32)
        return v / np.linalg.norm(v, axis=1, keepdims=True)


class FakeRetriever:
    chunks = CHUNKS
    embedder = FakeEmbedder()

    def retrieve(self, question, k=5, paper_id=None, mode="hybrid"):
        return [RetrievedChunk(c, 1.0, i) for i, c in enumerate(CHUNKS, start=1)]


def make_slide(title, words="uses the cross-entropy gradient"):
    return Slide(title=title, bullets=[f"The model {words} [P3_p2_c06]."] * 3, equations=[],
                 speaker_notes=[f"This note {words} [P3_p2_c06]."] * 3)


def make_talk():
    return Talk(title="Distillation", slides=[make_slide(f"Slide {i}") for i in range(1, 4)],
                script="Distillation uses soft targets [P3_p2_c06]. " * 30)


def parsed(action, numbers=(), target="whole_talk", instruction="", **create):
    fields = dict(paper_id=None, n_slides=None, notes_per_slide=None, audience=None, style=None,
                  length=None, focus=None, preserve_equations=None)
    fields.update(create)
    return ParsedMessage(action=action, slide_numbers=list(numbers), target=target, instruction=instruction, **fields)


class FakeLLM:
    """Answers each schema the way Gemini would, and remembers the prompts."""

    def __init__(self):
        self.prompts = []
        self.script_answers = []  # optional queue of ScriptEdit answers (used by the retry test)

    def __call__(self, prompt, schema, system_prompt=""):
        self.prompts.append(prompt)
        if schema is ParsedMessage:
            message = prompt.split("MESSAGE:")[-1]  # the prompt's examples also mention these phrases
            if "make #2 less technical" in message:
                return parsed("edit", [2], "slides", "make it less technical")
            if "shorten the script" in message:
                return parsed("edit", [], "script", "shorten the script")
            return parsed("create", paper_id="P3", n_slides=3, audience="grad_students")
        if schema is Talk:
            return make_talk()
        if schema is SlideEdit:
            return SlideEdit(slide=make_slide("Slide 2", "learns from the big model's guesses"),
                             reason="Replaced jargon with everyday words.")
        if schema is ScriptEdit:
            if self.script_answers:
                return self.script_answers.pop(0)
            return ScriptEdit(script="Distillation uses soft targets [P3_p2_c06].", reason="Shortened it.")
        if schema is TalkEdit:
            return TalkEdit(talk=make_talk(), reason="No change.")
        raise AssertionError(f"unexpected schema {schema}")


# ---------------------------------------------------------------- diff.py


def test_word_diff_marks_removed_and_added_words():
    assert word_diff("uses the cross-entropy gradient", "uses a simple signal") == \
        "uses ~~the cross-entropy gradient~~ **a simple signal**"


def test_slide_changes_finds_changed_and_added_fields():
    old = make_slide("Method")
    new = make_slide("Method", "learns from guesses")
    new.speaker_notes.append("An extra note.")
    changes = {c.where: c for c in slide_changes(old, new, 2)}
    assert "slide 2 · title" not in changes  # unchanged
    assert "slide 2 · bullet 1" in changes
    assert changes["slide 2 · note 4"].old == ""  # added


# ---------------------------------------------------------------- commands.py / versions.py


def test_meta_commands_need_no_llm():
    assert match_meta_command("show #2").slide_numbers == [2]
    assert match_meta_command("Undo").action == "undo"
    assert match_meta_command("make #2 less technical") is None


def test_create_message_gets_sensible_defaults():
    request = to_talk_request(parsed("create", paper_id="P3", audience="policymakers"))
    assert (request.n_slides, request.style, request.preserve_equations) == (7, "plain_english", False)


def test_undo_never_removes_the_first_version():
    history = VersionHistory()
    history.add(make_talk())
    assert history.undo() is None
    history.add(make_talk())
    assert history.undo().number == 2 and len(history.versions) == 1


# ---------------------------------------------------------------- session.py (whole conversation)


def test_full_conversation_create_edit_undo_and_log(tmp_path):
    llm = FakeLLM()
    session = ChatSession(FakeRetriever(), llm_structured=llm, log_dir=tmp_path)

    assert "Created a 3-slide talk" in session.handle("Make a 3-slide talk on the distillation paper")
    reply = session.handle("make #2 less technical")

    assert "v2: slide 2" in reply
    assert "Replaced jargon with everyday words." in reply  # the WHY
    assert "\n\n**Why it changed:**" in reply  # own paragraph (Markdown ignores a single line break)
    # the DELTA - word level, so the unchanged "the" stays plain
    assert "~~uses~~ **learns from** the ~~cross-entropy gradient~~ **big model's guesses**" in reply
    assert "readability" in reply  # before -> after metrics
    assert "CURRENT SLIDE 2" in llm.prompts[-1]  # delta-anchored: only slide 2 was sent
    assert session.talk.slides[0].title == "Slide 1"  # other slides untouched

    assert "v3: script" in session.handle("shorten the script")
    assert "Now back at v2" in session.handle("undo")
    assert "v2: slide 2" in session.handle("history")

    log = json.loads(session.log.json_path.read_text(encoding="utf-8"))
    assert [t["action"] for t in log["turns"]] == ["create", "edit", "edit", "undo", "history"]
    assert session.log.md_path.exists()


def test_failed_goal_is_retried_with_measured_feedback(tmp_path):
    llm = FakeLLM()
    session = ChatSession(FakeRetriever(), llm_structured=llm, log_dir=tmp_path)
    session.handle("Make a 3-slide talk on the distillation paper")

    llm.script_answers = [
        ScriptEdit(script=session.talk.script, reason="I shortened it."),  # 1st try: claims it, but unchanged
        ScriptEdit(script="Distillation uses soft targets [P3_p2_c06].", reason="Cut to one sentence."),
    ]
    reply = session.handle("shorten the script")

    assert "redone once" in reply
    assert "It was not shortened" in llm.prompts[-1]  # the retry prompt carried the measured feedback
    assert "Cut to one sentence." in reply


def test_goals_turn_requests_into_measurements():
    before = Metrics(reading_ease=40, supported_share=1, citation_coverage=1, n_words=500)
    assert target_words("shorten the script to 90 seconds") == 225
    assert target_words("make it 2 minutes long") == 300
    assert check_goal("make #2 less technical", before, replace(before, reading_ease=38)) is not None
    assert check_goal("make #2 less technical", before, replace(before, reading_ease=60)) is None
    assert "225 words" in check_goal("shorten to 90 seconds", before, before)
    assert check_goal("shorten to 90 seconds", before, replace(before, n_words=230)) is None
    assert check_goal("add an example", before, before) is None  # no measurable goal -> accepted


def test_editing_before_creating_gives_help(tmp_path):
    session = ChatSession(FakeRetriever(), llm_structured=FakeLLM(), log_dir=tmp_path)
    assert "no talk yet" in session.handle("make #2 less technical")
