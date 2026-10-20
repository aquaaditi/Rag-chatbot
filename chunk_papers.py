"""
Day 2 checkpoint: turn every paper in data/papers/ into chunks.

Run:  python chunk_papers.py
Output: data/chunks/<paper>.json  (open them in VS Code to inspect!)

This script only wires the stages together - the real work is in
src/ingestion/ (file -> blocks) and src/chunking/ (blocks -> chunks).
"""

from src import config
from src.chunking import Chunk, chunk_blocks, save_chunks
from src.ingestion import load_paper


def main():
    config.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    papers = sorted(config.PAPERS_DIR.glob("*.pdf")) + sorted(config.PAPERS_DIR.glob("*.tex"))

    for number, path in enumerate(papers, start=1):
        paper_id = f"P{number}"
        blocks = load_paper(path, paper_id)
        chunks = chunk_blocks(blocks)

        out_file = config.CHUNKS_DIR / f"{path.stem}.json"
        save_chunks(chunks, out_file)
        print_summary(paper_id, path.name, len(blocks), chunks, out_file)


def print_summary(paper_id: str, file_name: str, n_blocks: int, chunks: list[Chunk], out_file):
    sizes = [c.n_words for c in chunks]
    sections = list(dict.fromkeys(c.section for c in chunks))  # unique, in order

    print(f"\n{paper_id} = {file_name}")
    print(f"  {n_blocks} blocks -> {len(chunks)} chunks "
          f"(words per chunk: min {min(sizes)}, avg {sum(sizes) // len(sizes)}, max {max(sizes)})")
    print(f"  {sum(c.has_math for c in chunks)} chunks contain equations")
    print(f"  sections: {sections}")
    print(f"  saved -> {out_file.relative_to(config.PROJECT_ROOT)}")

    math_chunk = next((c for c in chunks if c.has_math), None)
    if math_chunk:
        print(f"  example math chunk [{math_chunk.chunk_id}] (page {math_chunk.page}, {math_chunk.section}):")
        print("    " + math_chunk.text[:300] + ("..." if len(math_chunk.text) > 300 else ""))


if __name__ == "__main__":
    main()
