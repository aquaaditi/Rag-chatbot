"""
runner.py - Evaluator: generate (or load) each case's script and measure it.

    evaluator = Evaluator(Retriever.load(), runs_dir=config.EVAL_DIR / "runs", bertscore=bertscore_f1)
    rows = evaluator.evaluate(default_cases(["P1", "P2", "P3"]))

Every generated script is CACHED in runs/<case_id>.json (text + the chunk IDs it was
given). Re-running only re-computes the metrics - no LLM calls, same scripts - so a
change to a metric can be compared fairly. Use fresh=True to generate new scripts.
"""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from src import config
from src.chunking import Chunk
from src.conversation.readability import reading_ease
from src.evaluation.cases import EvalCase
from src.evaluation.overlap import rouge
from src.evaluation.references import load_reference
from src.evaluation.row import EvalRow
from src.generation import ScriptGenerator
from src.generation.citations import find_citations, unknown_citations
from src.llm import ask_llm
from src.provenance import check_provenance, extract_claims
from src.provenance.claim import strip_citations
from src.retrieval import Retriever
from src.safety import check_output


class Evaluator:
    def __init__(
        self, retriever: Retriever, runs_dir: Path, llm: Callable[..., str] = ask_llm,
        bertscore: Callable[[list[str], list[str]], list[float]] | None = None,
        references_dir: Path = config.REFERENCES_DIR, fresh: bool = False,
    ):
        self._retriever = retriever
        self._generator = ScriptGenerator(retriever, llm)
        self._chunks = {c.chunk_id: c for c in retriever.chunks}
        self._runs_dir = runs_dir
        self._bertscore = bertscore
        self._references_dir = references_dir
        self._fresh = fresh
        self.n_generated = 0  # how many scripts were NEW (= LLM calls) in this evaluation

    def evaluate(self, cases: list[EvalCase], progress: Callable[[str], None] = lambda _: None) -> list[EvalRow]:
        rows, texts, references = [], [], []
        for i, case in enumerate(cases, start=1):
            progress(f"[{i}/{len(cases)}] {case.case_id}")
            text, sources = self.script_for(case)
            reference = load_reference(case.paper_id, case.length, self._references_dir)
            rows.append(self._measure(case, text, sources, reference))
            texts.append(text)
            references.append(reference)

        if self._bertscore:  # one batch for all scripts that have a reference (loading the model is slow)
            pairs = [(row, t, r) for row, t, r in zip(rows, texts, references) if r]
            for (row, _, _), score in zip(pairs, self._bertscore([t for _, t, _ in pairs], [r for _, _, r in pairs])):
                row.bertscore = score
        return rows

    # ------------------------------------------------------------ generate or load

    def script_for(self, case: EvalCase) -> tuple[str, list[Chunk]]:
        path = self._runs_dir / f"{case.case_id}.json"
        if path.exists() and not self._fresh:
            run = json.loads(path.read_text(encoding="utf-8"))
            return run["text"], [self._chunks[cid] for cid in run["source_ids"]]

        result = self._generator.generate(case.to_request())
        self.n_generated += 1
        path.parent.mkdir(parents=True, exist_ok=True)
        run = {"case_id": case.case_id, "model": config.LLM_MODEL, "generated": f"{datetime.now():%Y-%m-%d %H:%M}",
               "source_ids": result.source_ids, "length_retry": result.length_retry, "text": result.text}
        path.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
        return result.text, result.sources

    # ------------------------------------------------------------ measure

    def _measure(self, case: EvalCase, text: str, sources: list[Chunk], reference: str | None) -> EvalRow:
        request = case.to_request()
        report = check_provenance(extract_claims(text, "script"), sources, self._retriever.embedder)
        safety = check_output([("script", text)], case.audience, " ".join(c.text for c in sources),
                              reading_ease=reading_ease([text]))
        row = EvalRow(
            case.case_id, case.paper_id, case.audience, case.style, case.mode,
            words=len(strip_citations(text).split()), target_words=request.target_words,
            n_claims=report.n_claims, citation_coverage=report.citation_coverage,
            supported_share=report.supported_share,
            grounded_share=(report.count("supported") + report.count("weak")) / max(report.n_claims, 1),
            mean_similarity=report.mean_similarity,
            number_errors=report.number_errors,
            invented_citations=len(unknown_citations(find_citations(text), [c.chunk_id for c in sources])),
            reading_ease=reading_ease([text]), safety_warnings=len(safety.issues),
        )
        if reference:
            row.rouge1, row.rouge2, row.rougeL = rouge(text, reference).values()
        return row
