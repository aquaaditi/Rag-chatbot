"""
session.py - ChatSession: one conversation with the chatbot.

    session = ChatSession(Retriever.load())
    session.handle("Make a 7-slide talk on the distillation paper for grad students")
    session.handle("make #2 less technical")    # -> diff + reason + before/after metrics
    session.handle("undo")

For every message:  understand (commands.py) -> act (talks / editing) ->
measure before/after (readability + provenance) -> check the goal, retry once if
missed (goals.py) -> new version -> log the turn.
"""

from collections.abc import Callable

from google.genai.errors import APIError

from src import config
from src.chunking import Chunk
from src.conversation.commands import ParsedMessage, parse_message, to_talk_request
from src.conversation.diff import talk_changes
from src.conversation.editing import Editor
from src.conversation.formatting import render_change, render_history, render_outline, render_slide
from src.conversation.goals import check_goal
from src.conversation.log import ConversationLog
from src.conversation.readability import reading_ease, slide_texts, talk_texts
from src.conversation.versions import Change, Metrics, VersionHistory
from src.generation.citations import find_citations
from src.llm import ask_llm_structured
from src.provenance import Claim, check_provenance, claims_from_slide, extract_claims
from src.provenance.claim import strip_citations
from src.retrieval import Retriever
from src.talks import GeneratedTalk, Talk, TalkGenerator, TalkRequest
from src.talks.checks import all_text
from src.talks.export import save_talk_markdown

MAX_EDIT_ATTEMPTS = 2  # first try + one retry with the measured feedback (goals.py)

HELP = (
    "I turn papers into slide talks and edit them with you. Try:\n"
    "- \"Make a 7-slide talk on the distillation paper for graduate students focusing on methods\"\n"
    "- \"make #2 less technical\", \"dumb down slide 3\", \"shorten the script to 90 seconds\"\n"
    "- \"show #2\", \"history\", \"undo\", \"save\""
)


class ChatSession:
    def __init__(self, retriever: Retriever, llm_structured: Callable = ask_llm_structured,
                 log_dir=config.LOGS_DIR):
        self._retriever = retriever
        self._llm = llm_structured
        self._talks = TalkGenerator(retriever, llm_structured)
        self._editor = Editor(llm_structured)
        self.history = VersionHistory()
        self.request: TalkRequest | None = None
        self.sources: list[Chunk] = []
        self.log = ConversationLog(log_dir)
        self.papers = paper_catalog(retriever.chunks)

    @property
    def talk(self) -> Talk | None:
        return self.history.current.talk if self.history.current else None

    # ------------------------------------------------------------ one turn

    def handle(self, message: str) -> str:
        action = "error"
        try:
            parsed = parse_message(message, self.papers, len(self.talk.slides) if self.talk else None, self._llm)
            action = parsed.action
            reply = self._dispatch(parsed)
        except (ValueError, APIError) as error:  # keep the chat alive; show what went wrong
            reply = f"⚠️ Sorry, that failed: {error}"
        version = self.history.current.number if self.history.current else None
        self.log.add(message, action, reply, version)
        self.log.save()
        return reply

    def _dispatch(self, parsed: ParsedMessage) -> str:
        handlers = {
            "create": self._create, "edit": self._edit, "show": self._show,
            "undo": self._undo, "history": self._history, "save": self._save,
        }
        return handlers.get(parsed.action, lambda _: HELP)(parsed)

    # ------------------------------------------------------------ actions

    def _create(self, parsed: ParsedMessage) -> str:
        if parsed.paper_id not in self.papers:
            options = "; ".join(f"{pid} = {title}" for pid, title in self.papers.items())
            return f"Which paper should the talk be about? {options}"
        request = to_talk_request(parsed)
        result = self._talks.generate(request)
        self.request, self.sources = request, result.sources
        self.history.reset()
        version = self.history.add(result.talk)
        metrics = self._measure(talk_texts(result.talk), self._talk_claims(result.talk))
        return (
            f"✅ Created a {request.n_slides}-slide talk for {request.audience} ({request.style}).\n\n"
            + render_outline(result.talk, version.number)
            + f"\n\n**Measured:** readability {metrics.reading_ease:.0f} · supported claims "
              f"{metrics.supported_share:.0%} · citation coverage {metrics.citation_coverage:.0%}"
        )

    def _edit(self, parsed: ParsedMessage) -> str:
        if not self.talk:
            return "There is no talk yet - ask me to create one first.\n\n" + HELP
        old = self.talk
        instruction = parsed.instruction or "improve it"
        numbers = parsed.slide_numbers
        if (numbers or parsed.target == "slides") and (not numbers or any(not 1 <= n <= len(old.slides) for n in numbers)):
            return f"Please name slides between 1 and {len(old.slides)} (e.g. \"make #2 less technical\")."

        before = self._measure_part(old, parsed.target, numbers)
        feedback, attempts = "", 0
        while True:
            attempts += 1
            new, target, reason = self._apply_edit(old, parsed.target, numbers, instruction, feedback)
            after = self._measure_part(new, parsed.target, numbers)
            feedback = check_goal(instruction, before, after) or ""
            if not feedback or attempts >= MAX_EDIT_ATTEMPTS:
                break  # goal reached, or out of retries (then the reply says so)

        change = Change(instruction, target, reason, talk_changes(old, new), before, after,
                        attempts=attempts, unmet_goal=feedback or None)
        return render_change(self.history.add(new, change))

    def _apply_edit(self, old: Talk, target: str, numbers: list[int], instruction: str,
                    feedback: str) -> tuple[Talk, str, str]:
        """One edit attempt, always starting from the OLD talk. Returns (new talk, target name, reason)."""
        if numbers:
            new, reasons = old, []
            for n in numbers:
                new, reason = self._editor.edit_slide(new, n, instruction, self.request, self.sources, feedback)
                reasons.append(reason if len(numbers) == 1 else f"Slide {n}: {reason}")
            return new, f"slide{'s' if len(numbers) > 1 else ''} {', '.join(map(str, numbers))}", " ".join(reasons)
        if target == "script":
            new, reason = self._editor.edit_script(old, instruction, self.request, self.sources, feedback)
            return new, "script", reason
        new, reason = self._editor.edit_whole_talk(old, instruction, self.request, self.sources, feedback)
        return new, "whole talk", reason

    def _show(self, parsed: ParsedMessage) -> str:
        if not self.talk:
            return "There is no talk yet.\n\n" + HELP
        if parsed.slide_numbers:
            return "\n\n".join(
                render_slide(self.talk.slides[n - 1], n) for n in parsed.slide_numbers if 1 <= n <= len(self.talk.slides)
            ) or f"There are only {len(self.talk.slides)} slides."
        return render_outline(self.talk, self.history.current.number) + f"\n\n**Script:** {self.talk.script}"

    def _undo(self, parsed: ParsedMessage) -> str:
        removed = self.history.undo()
        if removed is None:
            return "Nothing to undo."
        return (f"↩️ Undid v{removed.number} ({removed.change.target}: \"{removed.change.instruction}\"). "
                f"Now back at v{self.history.current.number}.")

    def _history(self, parsed: ParsedMessage) -> str:
        return render_history(self.history.versions) if self.history.versions else "No versions yet."

    def _save(self, parsed: ParsedMessage) -> str:
        if not self.talk:
            return "There is no talk to save yet."
        result = GeneratedTalk(self.request, self.talk, self.sources, prompt="", problems=[],
                               attempts=0, cited_ids=find_citations(all_text(self.talk)))
        path = save_talk_markdown(result, config.EXAMPLES_DIR)
        return f"💾 Saved v{self.history.current.number} to {path.relative_to(config.PROJECT_ROOT)}"

    # ------------------------------------------------------------ measuring

    def _measure_part(self, talk: Talk, target: str, numbers: list[int]) -> Metrics:
        """Measure only the edited part: those slides, the script, or the whole talk."""
        if numbers:
            texts = [t for n in numbers for t in slide_texts(talk.slides[n - 1])]
            claims = [c for n in numbers for c in claims_from_slide(talk.slides[n - 1], n)]
        elif target == "script":
            texts, claims = [talk.script], extract_claims(talk.script, "script")
        else:
            texts, claims = talk_texts(talk), self._talk_claims(talk)
        return self._measure(texts, claims)

    def _measure(self, texts: list[str], claims: list[Claim]) -> Metrics:
        report = check_provenance(claims, self.sources, self._retriever.embedder)
        n_words = len(" ".join(strip_citations(t) for t in texts).split())
        return Metrics(reading_ease(texts), report.supported_share, report.citation_coverage, n_words)

    @staticmethod
    def _talk_claims(talk: Talk) -> list[Claim]:
        claims = [c for n, slide in enumerate(talk.slides, start=1) for c in claims_from_slide(slide, n)]
        return claims + extract_claims(talk.script, "script")


def paper_catalog(chunks: list[Chunk]) -> dict[str, str]:
    """{"P1": "Convolutional Neural Networks for Sentence Classification", ...} from the first chunk of each paper."""
    catalog: dict[str, str] = {}
    for chunk in chunks:
        if chunk.paper_id not in catalog:
            catalog[chunk.paper_id] = " ".join(chunk.text.split()[:9])
    return catalog
