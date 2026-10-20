# SARAL Chatbot — Audience-Adaptive Script & Bullet Generator

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

```
saral-chatbot/
├── data/papers/        # input papers
├── data/references/    # human-written reference scripts
├── src/                # pipeline modules (ingest, chunk, embed, retrieve, generate, ...)
├── eval/               # evaluation scripts
├── logs/               # conversation logs
├── app.py              # chat UI
└── README.md
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
