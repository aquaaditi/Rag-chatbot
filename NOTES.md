# Learning Journal

Write in your own words — this is your interview prep material.

## Day 1 — Setup & RAG basics

**What I set up:**
- Python virtual environment (venv) so this project's libraries stay separate from other projects
- Git repo, with .gitignore excluding venv/, .env and __pycache__/
- .env for secrets (API key) and .env.example as a placeholder others can copy
- Checked with `git check-ignore -v .env` that .env is really ignored
- First commit: 452fa97 "Day 1: project setup"

**What is RAG? (my own words):**
- RAG (Retrieval-Augmented Generation) is an Artificial Intelligence technique that helps Large Language Models (LLMs) generate more accurate and relevant answers by retrieving information from external sources, such as PDFs, documents, websites, or databases.

RAG works in three main steps: Retrieval, Augmentation, and Generation.

First, Retrieval finds relevant information from a knowledge source based on the user's question. Second, Augmentation combines the retrieved information with the question to provide context to the AI model. Finally, Generation uses the LLM to generate an answer based on the provided information.

In a RAG system, documents are often divided into smaller sections called chunks. These chunks are converted into embeddings, which represent their meaning numerically, and stored in a vector database such as FAISS or Chroma. When a user asks a question, the system retrieves the most relevant chunks and passes them to the LLM.

For example, a college chatbot can use RAG to answer questions from university documents.

In simple words, RAG connects AI models with external knowledge to provide more relevant, reliable, and context-specific answers.

**What are embeddings / chunks / cosine similarity?**
- Chunk: a small piece of a document (a paragraph, a bullet, an equation, a slide's
  notes). LLMs can't take unlimited text, and citations need small pieces with a
  location (page/slide), so we split documents into chunks.
- Embedding: a list of numbers (a vector) that represents a chunk's meaning.
  Texts with similar meaning get similar vectors, even with different words.
  e.g. "car crash" and "vehicle accident" end up close together.
- Cosine similarity: measures how similar two vectors are by the ANGLE between
  them. 1 = same direction (very similar meaning), 0 = unrelated.
  To search: embed the question, compare it with every chunk's vector, and return
  the chunks with the highest cosine similarity.

**Papers I chose (and why):**
1. Kim (2014), "Convolutional Neural Networks for Sentence Classification" — 6 pages
2. Joulin et al. (2016), "Bag of Tricks for Efficient Text Classification" (fastText) — 5 pages
3. Hinton et al. (2015), "Distilling the Knowledge in a Neural Network" — 9 pages
   Why: short, well-known, text-based PDFs (not scanned), and each has equations
   to test math preservation. Papers 1 & 2 are related (both text classification).

**What broke & how I fixed it:**
-
1. Wrong Gemini model name
   - Error message: 404 NOT_FOUND — "This model models/gemini-2.5-flash is no
     longer available to new users"
   - Cause: the model name in my code didn't exist / was outdated.
     (A 404 meant the key itself was fine — Google accepted the request.)
   - Fix: replaced it with a current model name from Google AI Studio's model list.
   - Lesson: model names change; keep the name in .env / config, not hard-coded,
     so I can change it in one place.

2. GitHub account problem
   - Error message: 403 — "Permission to aquaaditi/Rag-chatbot.git denied to Aditisailax"
   - Cause: Windows Credential Manager had my work GitHub account (Aditisailax)
     saved, so git used it automatically.
   - Fix: put my username in the remote URL so git asks for that account:
     git remote set-url origin https://aquaaditi@github.com/aquaaditi/Rag-chatbot.git
     Also set this repo's commit email to my personal one (git config user.email).
   - Lesson: 403 = logged in but not allowed; check WHICH account is being used.

3. `cp .env.example .env` overwrote my existing .env
   - Lesson: read the output of a check (`ls -a`) before acting on it.

4. "LF will be replaced by CRLF" warning
   - Harmless: Windows vs Linux line endings.

5. PDF text has ligatures ("Classiﬁcation" with one "ﬁ" character)
   - Found when checking the papers extract correctly (PyMuPDF).
   - Will need to normalise text on Day 2, otherwise searching for
     "classification" won't match.

### ✅ Day 1 checklist — COMPLETE
- [x] Python venv, VS Code, Git set up
- [x] Gemini API key in .env (git-ignored); `python hello_llm.py` prints two answers
- [x] Code on GitHub: https://github.com/aquaaditi/Rag-chatbot
- [x] Read RAG paper (abstract, intro, Figure 1); wrote "What is RAG?" in my own words
- [x] 3 papers in data/papers/ (text extracts correctly with PyMuPDF)
- [x] Study notes for all 3 papers (data/references/*_notes.md)
- [x] 3 human-written 90-second reference scripts (data/references/*_90s.txt)

## Day 2 — Ingestion & chunking

**What is a chunk, and why ~250 words? (my own words):**
-A chunk is a small piece of a paper that the system can search for and cite on its own, saved with its location (paper and page).

About 250 words is a balance:

Too small (one sentence): the chunk loses context. “It improved accuracy by 4%” means nothing if you don’t know what “it” is.
Too big (a whole page): the chunk mixes many topics, so search becomes less precise, citations become vague (“somewhere on page 3”), and fewer chunks fit into Gemini’s prompt.
There’s also a technical limit: the embedding model you’ll use (bge-base-en-v1.5) only reads about 512 tokens. 250 words is roughly 330 tokens, which fits comfortably. Text beyond the limit is cut off and ignored.

One-line version: a chunk is a citable piece of a document; ~250 words is big enough to hold a complete idea and small enough for precise search, clear citations, and the embedding model’s limit.

**Why must an equation never be split?**
-Half an equation is meaningless, or worse, misleading. If the softmax-with-temperature formula from paper3 is cut in the middle, one chunk has the top part of the fraction and the next has the bottom.

That breaks things in several ways:

Search: a question about “temperature in softmax” won’t match either half properly.
Generation: Gemini may receive half an equation and write wrong math in the speaker notes.
Citations and checking: the citation points to a broken formula, so neither a human nor your Checker can verify the claim.
The assignment explicitly requires it: speaker notes must preserve math in LaTeX, and Part B asks for a chunking strategy that keeps LaTeX math blocks intact.

**What surprised me about PDF text?** (looked at data/chunks/*.json)
- Ligatures: "ﬁ" is stored as one special character, so "classification" didn't match until we cleaned it.
- Words split across lines with a hyphen: "vec-" + "tors" in paper 1.
- In two-column papers, some lines have only one word.
- Equations come out as a jumble: in paper 3, Σ became the letter "P" and the fraction line disappeared
  (qi = exp(zi/T ) P j exp(zj/T ) (1)). The chunker keeps the pieces together, but can't rebuild LaTeX.
- The equation (page 2) and its explanation "where T is a temperature" (page 3) ended up in different
  chunks, because chunks never cross pages.
- Page numbers, the vertical arXiv stamp (e.g. "arXiv:1408.5882" in paper 1) and the reference list
  were mixed into the text, so the code removes them.

**What do the chunk IDs mean? (e.g. P3_p2_c06)**
- P3_p2_c06 = paper 3, page 2, chunk 6 on that page.
- The chunk number restarts on every page: P3_p2_c06 is followed by P3_p3_c01
  (the counter is kept per page in src/chunker.py, `count_per_loc`).

Why IDs matter:
- Citations: when Gemini writes a claim, it cites P3_p2_c06, and the code can turn that into
  "Paper 3, page 2" and show the exact text.
- Checking: the evaluation can look up the chunk by its ID to verify a claim.
- Stability: the same file always produces the same IDs, so old citations keep pointing to the right text.
- Zero padding (c06, not c6) makes IDs sort correctly: c06 comes before c10.

One-line version: the ID says which paper, page and chunk a piece of text came from; stable IDs let
every claim be traced, displayed and verified.

## Day 3 — Embeddings & retrieval

**What is an embedding, and what does cosine similarity measure? (my own words):**
-

**Dense vs BM25 — what does each one find that the other misses?** (try: python search.py "..." --compare)
-

**How does Reciprocal Rank Fusion combine them, and why not just add the scores?**
-

**Why did "softmax with temperature" NOT return the Equation 1 chunk?**
-

**What broke & how I fixed it:**
- Search took ~1 minute to start: the venv (1.24 GB, 44k files) was inside OneDrive, so every import
  was slowed by sync/scanning. Fix: moved the venv to C:\Users\aditi\venvs\rag-chatbot.
