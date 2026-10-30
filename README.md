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
              (blocks)      (chunks)   (top-k chunks)  (Day 4+)
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
│   ├── chunking/              # STAGE 2: Blocks -> Chunks
│   │   ├── chunk.py           #   Chunk data type (ID like P3_p2_c06)
│   │   ├── sentences.py       #   math-safe sentence splitting
│   │   ├── chunker.py         #   size limit, page boundaries, overlap, IDs
│   │   └── storage.py         #   save / load chunks as JSON
│   ├── retrieval/             # STAGE 3: question -> most relevant Chunks
│   │   ├── retrieved_chunk.py #   RetrievedChunk data type (chunk + score + rank)
│   │   ├── embedder.py        #   text -> vectors (sentence-transformers, bge-small-en-v1.5)
│   │   ├── vector_store.py    #   DENSE search (FAISS, cosine similarity)
│   │   ├── bm25_index.py      #   SPARSE keyword search (BM25)
│   │   ├── hybrid.py          #   merge both rankings (Reciprocal Rank Fusion)
│   │   └── retriever.py       #   build / save / load index, retrieve()
│   ├── generation/            # STAGE 4: request + chunks -> script with [chunk ID] citations
│   │   ├── options.py         #   audience / length / style choices, ScriptRequest
│   │   ├── context.py         #   format chunks as the SOURCES block of the prompt
│   │   ├── prompts.py         #   prompt template family + grounding rules (system prompt)
│   │   ├── citations.py       #   find + check the [chunk IDs] in the answer
│   │   ├── script_result.py   #   GeneratedScript data type
│   │   ├── generator.py       #   ScriptGenerator: retrieve -> prompt -> LLM -> check
│   │   ├── source_selection.py #  abstract + top chunks + math-aware equation chunks
│   │   └── export.py          #   save a run as Markdown (examples/)
│   ├── talks/                 # STAGE 4b: structured slide talks (JSON via Pydantic schema)
│   │   ├── schema.py          #   Slide / Talk: the JSON shape Gemini must return
│   │   ├── request.py         #   TalkRequest: slides, notes per slide, focus, equations...
│   │   ├── prompts.py         #   talk template + self-correction retry prompt
│   │   ├── checks.py          #   slide count, notes, equations, length, citations
│   │   ├── result.py          #   GeneratedTalk data type
│   │   ├── generator.py       #   TalkGenerator: sources -> JSON -> check -> retry once
│   │   └── export.py          #   save a talk deck as Markdown
│   ├── provenance/            # STAGE 5: every claim -> the source sentence that supports it
│   │   ├── claim.py           #   split outputs into claims (sentence + cited IDs)
│   │   ├── numbers.py         #   EXACT match: numbers must appear in the cited source
│   │   ├── support.py         #   SEMANTIC match: best source sentence + verdict per claim
│   │   ├── report.py          #   metrics: citation coverage, supported share, number errors
│   │   └── export.py          #   Markdown provenance table + terminal summary
│   └── conversation/          # STAGE 6: chat - create, edit (#2 less technical), undo, with change tracking
│       ├── commands.py        #   understand a message (fast path + Gemini structured output)
│       ├── edit_prompts.py    #   DELTA-ANCHORED edit prompts (only the changed part + its sources)
│       ├── editing.py         #   Editor: edit a slide / the script / the whole talk -> new talk + reason
│       ├── goals.py           #   measurable goal per request (simpler -> readability up, 90s -> 225 words)
│       ├── diff.py            #   the delta: field by field, word by word (~~old~~ **new**)
│       ├── readability.py     #   Flesch reading ease
│       ├── versions.py        #   versions + changes + before/after metrics, undo
│       ├── formatting.py      #   Markdown chat replies
│       ├── log.py             #   logs/session_*.json + .md (evidence of iteration)
│       └── session.py         #   ChatSession.handle(message) -> reply
├── tests/                     # one test file per stage (pytest)
├── data/
│   ├── papers/                # input papers
│   ├── chunks/                # output of chunking (JSON)
│   └── references/            # human-written reference scripts (for evaluation)
├── hello_llm.py               # Day 1 check: can we call the LLM?
├── chunk_papers.py            # Day 2: run ingestion + chunking on all papers
├── build_index.py             # Day 3: embed all chunks, save index/ (git-ignored)
├── search.py                  # Day 3: python search.py "question" [--paper P3] [--compare]
├── generate.py                # Day 4: python generate.py --paper P3 --audience policymakers --length 90s
├── make_talk.py               # Day 5: python make_talk.py --paper P3 --slides 7 --notes 3 --focus methods
├── chat.py                    # Day 7: python chat.py  (or --demo for a scripted conversation)
├── logs/                      # conversation logs
├── examples/                  # saved example runs (input -> script -> sources -> checks)
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
