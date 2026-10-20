# "RAG Chatbot: Research Paper to Slides, Scripts & Summaries" 

A RAG (Retrieval-Augmented Generation) chatbot that takes a research paper (PDF/LaTeX) and generates
audience-adaptive slide bullets, speaker scripts, speaker notes, and tweet-sized abstracts — with
source citations and conversational editing.

> Status: 🚧 Work in progress

## Features (planned)

- **Ingest papers** — PDF/LaTeX parsing with page numbers; chunking that keeps LaTeX math blocks intact
- **Retrieval** — sentence-BERT embeddings + vector store (FAISS/Chroma)
- **Generation** — slide bullets, full speaker scripts, speaker notes, tweets
- **Audience / length / style control** — policymakers, grad students, press · 30s / 90s / 5min · technical, plain-English, press release
- **Provenance** — every generated sentence links back to its source chunk and page number
- **Change tracking** — edits like "make #2 less technical" show old vs. new and why it changed
- **Safety** — no offensive content, accessible language
- **Evaluation** — factuality proxy, citation coverage, ROUGE / BERTScore, human ratings

## Project Structure

The code is organised as a pipeline. Each folder in `src/` is one stage, and each file in a stage
has one job:

```
paper.pdf ──► ingestion ──► chunking ──► retrieval ──► generation ──► answer + citations
              (blocks)      (chunks)     (Day 3)       (Day 4+)
```

```
Rag-chatbot/
├── src/
│   ├── config.py              # ALL settings: paths, model, chunk size...
│   ├── llm.py                 # the only file that calls the LLM (Gemini)
│   ├── ingestion/             # STAGE 1: paper file -> Blocks
│   │   ├── block.py           #   Block data type (prose / math + page + section)
│   │   ├── text_cleaning.py   #   fix ligatures, broken words, whitespace
│   │   ├── block_rules.py     #   is it noise / a heading / references / math?
│   │   ├── latex_math.py      #   protect LaTeX math from being split
│   │   ├── pdf_loader.py      #   PDF  -> Blocks
│   │   └── tex_loader.py      #   .tex -> Blocks
│   └── chunking/              # STAGE 2: Blocks -> Chunks
│       ├── chunk.py           #   Chunk data type (ID like P3_p2_c06)
│       ├── sentences.py       #   math-safe sentence splitting
│       ├── chunker.py         #   size limit, page boundaries, overlap, IDs
│       └── storage.py         #   save / load chunks as JSON
├── tests/                     # one test file per stage (pytest)
├── data/
│   ├── papers/                # input papers
│   ├── chunks/                # output of chunking (JSON)
│   └── references/            # human-written reference scripts (for evaluation)
├── hello_llm.py               # Day 1 check: can we call the LLM?
├── chunk_papers.py            # Day 2: run ingestion + chunking on all papers
└── NOTES.md                   # learning journal
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Add your LLM API key to a `.env` file:

```
GEMINI_API_KEY=your_key_here
```

## Usage

```bash
streamlit run app.py
```

Upload a paper, then chat, e.g.:

- "Make a 90-second script for policymakers"
- "Make a 7-slide talk for graduate students focusing on methods; include 3 speaker notes per slide"
- "Make #2 less technical"

## Evaluation

_Results will be added here._

## References

- Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS 2020. https://arxiv.org/abs/2005.11401
- _Add every library, model, and paper used._
