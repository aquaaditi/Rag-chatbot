# Learning Journal

Write in your own words — this is your interview prep material.

## Day 1 — Setup & RAG basics

**What I set up:**
-

**What is RAG? (my own words):**
-

**What are embeddings / chunks / cosine similarity?**
-

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
