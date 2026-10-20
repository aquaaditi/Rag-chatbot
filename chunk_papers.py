"""
Day 2 checkpoint: turn every paper in data/papers/ into chunks.

Run:  python chunk_papers.py
Output: data/chunks/<paper>.json  (open them in VS Code to inspect!)
"""

import json
from pathlib import Path

from src.chunker import chunk_blocks
from src.ingest import load_paper

PAPERS_DIR = Path("data/papers")
CHUNKS_DIR = Path("data/chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

papers = sorted(PAPERS_DIR.glob("*.pdf")) + sorted(PAPERS_DIR.glob("*.tex"))

for i, path in enumerate(papers, start=1):
    paper_id = f"P{i}"
    blocks = load_paper(path, paper_id)
    chunks = chunk_blocks(blocks)

    out_file = CHUNKS_DIR / f"{path.stem}.json"
    out_file.write_text(
        json.dumps([c.to_dict() for c in chunks], indent=2, ensure_ascii=False), encoding="utf-8"
    )

    sizes = [c.n_words for c in chunks]
    print(f"\n{paper_id} = {path.name}")
    print(f"  {len(blocks)} blocks -> {len(chunks)} chunks "
          f"(words per chunk: min {min(sizes)}, avg {sum(sizes) // len(sizes)}, max {max(sizes)})")
    print(f"  {sum(c.has_math for c in chunks)} chunks contain equations")
    print(f"  sections: {sorted({c.section for c in chunks}, key=lambda s: [c.section for c in chunks].index(s))}")
    print(f"  saved -> {out_file}")

    math_chunk = next((c for c in chunks if c.has_math), None)
    if math_chunk:
        print(f"  example math chunk [{math_chunk.chunk_id}] (page {math_chunk.page}, {math_chunk.section}):")
        print("    " + math_chunk.text[:300] + ("..." if len(math_chunk.text) > 300 else ""))
