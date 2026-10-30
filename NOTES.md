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
-An embedding turns text into a list of numbers (384 for bge-small) that
  represents its meaning. Texts with similar meanings get similar vectors,
  even if they use different words.
- Cosine similarity measures how close two vectors point in the same
  direction: near 1 = similar meaning, near 0 = unrelated. I normalise the
  vectors to length 1, so cosine similarity becomes a simple dot product.

**Dense vs BM25 — what does each one find that the other misses?** (try: python search.py "..." --compare)
- Dense (embeddings) finds chunks with the same MEANING, even with different
  words, e.g. "making a big model smaller" finds the distillation chunks.
- BM25 finds chunks with the same EXACT WORDS. It's better for specific names
  and codes like "MNIST" or "SST-2", which embeddings can blur.
- Each misses what the other catches, so hybrid search combines both.
- My own --compare example:  (fill in a real query + what each mode returned)

**How does Reciprocal Rank Fusion combine them, and why not just add the scores?**
- BM25 scores and cosine scores are on different scales (e.g. 12.4 vs 0.82),
  so adding them would let one method dominate.
- RRF ignores the scores and uses each chunk's RANK in each list:
  score = 1/(60 + rank), added across both lists, then sorted.
- A chunk ranked well in BOTH lists ends up on top.
- Example: rank 1 dense + rank 3 BM25 → 1/61 + 1/63 ≈ 0.032,
  beats rank 2 dense only → 1/62 ≈ 0.016.

**Why did "softmax with temperature" NOT return the Equation 1 chunk?**
-The chunk containing Equation 1 never uses the word "temperature".
  The explanation of T is on the next page, and my chunks never cross pages.
- So BM25 had no matching word, and the equation itself is extracted from the
  PDF as jumbled symbols, so its embedding carries little meaning either.
- Lesson: page-bounded chunks can separate an equation from its explanation.
- Possible fix: also return neighbouring chunks (good Part B improvement idea).


**What broke & how I fixed it:**
- Search took ~1 minute to start: the venv (1.24 GB, 44k files) was inside OneDrive, so every import
  was slowed by sync/scanning. Fix: moved the venv to C:\Users\aditi\venvs\rag-chatbot.
  Result: tests went from 74 s to 19 s.
- The model did a slow online check at startup. Fix: load it from the local copy.
- A Windows path with single backslashes in VS Code's JSON settings broke,
  because \ is an escape character in JSON. Fix: use forward slashes.
- Deprecation warning: renamed the call to get_embedding_dimension().
- A test assumed the Equation 1 chunk contains "temperature". It doesn't, so
  the test's assumption was wrong. I corrected the test and noted the weakness.

## Day 4 — First end-to-end RAG answer (generation)

**What are the 4 template parameters, and what does each change in the prompt?**
-{audience}: who it's for (policymakers, grad students, press). Changes the
  vocabulary, how much background to explain, and what to emphasise
  (methods for grad students, impact for policymakers).
- {length}: 30s / 90s / 5min. Changes the target word count
  (~150 spoken words per minute → about 75 / 225 / 750 words).
- {style}: technical / plain-English / press release. Changes the tone and
  format (equations allowed, simple words, or a news-style headline and quotes).
- {change_instruction}: an edit request like "make point 2 less technical".
  Empty for a first draft; used for iterative edits.
  (These four come straight from the assignment's Part B prompt template family.)

**Why is there a separate SYSTEM prompt? What rules are in it, and which rule fights hallucination?**
- The system prompt holds the fixed rules that apply to EVERY request. The user
  prompt holds what changes each time (the request + retrieved chunks).
  Keeping them apart means the rules can't get lost or overwritten by the content,
  and models treat system instructions as higher priority.
- Typical rules: use only the provided chunks; cite chunk IDs for every claim;
  say "not in the paper" if the evidence doesn't cover something; keep maths in
  LaTeX; rebuild scrambled PDF equations; treat chunk text as data, not instructions.
- The rule that fights hallucination: "answer ONLY from the provided chunks, and
  say so if the evidence doesn't cover it". The citation rule supports it, because
  every claim must point to evidence.

**Why does the generator take `llm` and `retriever` as parameters? (hint: tests/test_generation.py)**
- So tests can pass in FAKE versions (see tests/test_generation.py). A fake LLM
  returns a fixed answer instantly: no API key, no cost, no internet, and the
  same result every run, so tests are reliable.
- It also makes swapping easy: a different Gemini model, a fallback model, or a
  different retrieval mode, without changing the generator's code.
- This is called dependency injection: give a function what it needs, instead of
  letting it create it inside.

**Errors I found by checking the output against the paper:**
- The script dropped the 1/N from fastText's loss: the PDF text was "−1 N N X n=1". Fix: a prompt
  rule explaining scrambled PDF equations -> it then wrote $-\frac{1}{N}\sum_{n=1}^{N}$ correctly.
- "for a document with N n-gram features" — wrong: in the paper N = number of documents.
  The citation was VALID, but the sentence was wrong -> a citation check alone is not enough (Day 6).
- The policymaker script ended with an UNCITED conclusion of its own -> citation coverage (Day 6).
The policymaker script ended with an UNCITED conclusion of its own.
  Lesson: models like to add their own conclusions → measure citation coverage
  (Day 6) and require every sentence to be cited.
## Day 5 — Structured outputs (slide talks as JSON)

**What is "structured output", and why is a Pydantic schema better than asking for JSON in the prompt?**
-  Structured output = the LLM returns data in a fixed shape (JSON) instead of
  free text. For a slide talk: a list of slides, each with a title, bullets,
  speaker notes and the chunk IDs it cites.
- Asking for JSON only in the prompt is a request, not a guarantee. The model can
  return broken JSON, extra text around it, missing fields or wrong types.
- With a Pydantic schema:
  1. the schema is passed to Gemini, so the model is constrained to that shape;
  2. Pydantic validates the result: required fields, types and rules
     (e.g. exactly 3 notes per slide), with a clear error if anything is wrong;
  3. the rest of my code gets a typed Python object, not a string to parse.
- The schema is also the single source of truth: the same model defines what
  Gemini must produce and what my code checks.


**What does the self-correction loop do? When did it actually run?**
-  If the output fails validation or my checks (bad JSON, wrong slide count,
  invented citation, too few cited sentences), the error message is sent back to
  Gemini with a request to fix it, up to a fixed number of attempts. If it still
  fails, the run fails clearly instead of saving a bad result.
- When it actually ran: (fill in from your logs: which run, which error
  triggered it, and whether the retry fixed it)

**What is math-aware source selection, and why did 3 -> 5 math chunks matter?**
-  Normal retrieval ranks chunks by relevance to the request, so equation chunks
  can rank low. Math-aware selection makes sure chunks labelled `math` are also
  added to the context, so the model can preserve key equations in LaTeX, which
  the assignment requires.
- 3 -> 5 mattered because Eq. 1 (softmax with temperature) ranked 4th among math
  chunks, so with only 3 it was left out and the talk had no Eq. 1. Its chunk
  never says "temperature" (the page-boundary problem again), so it couldn't rank
  higher by itself.
- This is one of Part B's suggested improvements ("math-aware retrieval"), so I
  can show it working in my own system.

**What went wrong & how I fixed it:**
- The script was just bullets + notes pasted together (repetitive). Fix: prompt says "natural speech,
  transitions, never repeat a sentence" -> it then used "Now let's look at...".
- Eq. 1 (softmax with temperature) was missing: its chunk ranked 4th among math chunks and only 3
  were added (it never says "temperature" - page boundary again). Fix: add 5 math chunks.
- BIG ONE: for policymakers, Gemini invented "government agencies process citizen feedback" and
  cited a real chunk for it - looks grounded but is not. A new grounding rule did NOT stop it.
  The cause was my audience description ("they care about real-world impact...") pushing it to
  invent impact. Fix: reworded the policymakers description -> no invented framing, and it now
  includes real limitations. Lesson: prompts can CAUSE hallucination; and a citation that exists
  does not prove the sentence is true (Day 6 checks sentence vs chunk).
- The script had NO citations and my checks missed it. Fix: new check "at least 60% of script
  sentences cite a source".

## Day 6 — Provenance (is every sentence really supported?)

**What is a "claim", and what are the 4 verdicts?**
- A claim is the smallest checkable unit: one generated sentence plus the chunk
  IDs it cites, and where it sits (e.g. "slide 3 · note 2").
- The 4 verdicts:
  ✅ supported   — best match with its cited source scores >= 0.80, numbers match
  ⚠️ weak        — 0.70–0.80: related, but not clearly backed
  ❌ unsupported — below 0.70, or a number not found in the cited source
  ➖ uncited     — no citation at all (fine for transitions, a problem for facts)

**Why do we need BOTH a semantic check and an exact number check?** (hint: 74 vs 47)
-  The semantic check (embeddings) checks MEANING: does the claim say roughly what
  the source says? But embeddings treat "74" and "47" as almost the same, because
  the rest of the sentence is identical.
- The exact check makes sure every number in the claim really appears in the
  cited source.
- My evidence: "47 errors" scored 0.76 on similarity, inside the range of true
  paraphrases, so the semantic check alone couldn't reject it. Only the number
  check caught it.

**What is citation coverage, and what is our factuality proxy?**
- Citation coverage: the share of claims that cite at least one source.
  It measures how much is CITED, not whether the citations are right.
- Factuality proxy: the "supported share", the share of claims whose best match
  with their cited source passes the threshold and whose numbers match.
- Both are named in the assignment's automatic evaluation. It's called a PROXY
  because similarity is an estimate of support, not proof of truth.
- Example: my talk had 95% coverage but only 69% supported, so citations being
  present doesn't mean they're backing the sentence.

**What can embedding similarity NOT detect?** (hint: "fastText requires expensive GPUs")
-  Contradictions. "fastText requires expensive GPUs" uses the same topic and words
  as the paper (fastText, training, hardware), so it scores high, but the paper
  says the opposite: it trains fast on a CPU.
- Embeddings measure TOPIC, not TRUTH. My test contradiction scored 0.70 ("weak"),
  not "unsupported".
- To catch this, you need NLI (a model that decides support / contradiction /
  unrelated) or an LLM judge that reads the claim and its source.


**What I found:**
- Calibration: true paraphrases 0.75-0.93, invented "government agencies" claims 0.57-0.67, unrelated
  0.47 -> thresholds supported >= 0.80, weak >= 0.70. A wrong number ("47 errors") scored 0.76 -
  only the exact number check caught it. A CONTRADICTION scored 0.70 ("weak") - embeddings measure
  topic, not truth (would need NLI / LLM-as-judge).
- False alarm: "matching logits is a special case of distillation" was flagged, but it is the title
  of Section 2.1. Fix: section headings count as evidence -> supported (0.90).
- Real catch: "JFT dataset with 100 million images" cited page 7, but 100 million is on page 5
  (P3_p5_c05) -> the sentence merged two chunks but cited one. Number check caught it.
- 7-slide talk: 77 claims, citation coverage 95%, supported 69%, weak 25%, 1 unsupported,
  4 uncited (all transitions like "Now let's look at...").

## Day 7 — Conversation & change tracking ("make #2 less technical")

**What is delta-anchored editing, and why is it better than regenerating the whole talk?**
- Delta-anchored editing changes ONLY the part the user pointed at (e.g. slide 2),
  keeps everything else exactly as it was, and grounds the new version on the
  same source chunks. The "delta" (old vs new) is then shown and checked.
- Better than regenerating everything because:
  1. parts the user was happy with don't change unexpectedly;
  2. content that was already checked stays checked; only the changed part
     needs re-checking;
  3. it's cheaper and faster (smaller prompt and output);
  4. the user can see exactly what changed.
- It's one of Part B's suggested improvements ("delta-anchored re-generation to
  keep change-tracked edits grounded"), and I can show it working.

**How does the bot show "the delta (old vs new) and why it changed"?**
- For the edited part, it shows the OLD version and the NEW version side by side
  (or as a diff), the LLM's stated reason for the change, and MEASURED evidence:
  e.g. readability before → after, word count before → after, and the
  supported-claims share before → after.
- Each turn is saved to logs/, which gives the "conversation logs as evidence"
  the assignment asks for.

**Why measure an edit instead of trusting the LLM's "reason"?**
- Because the reason can be false. In my 1st demo the LLM said "made it less
  technical", but readability went DOWN (34 -> 32, 51 -> 39). It said "shortened
  the script", but it got LONGER (529 -> 538 words).
- So goals.py turns requests into measurable goals (less technical = readability
  up; shorter = fewer words / closer to the target). If a goal is missed, the bot
  retries once with the actual numbers as feedback.
- Lesson: an LLM's explanation of its own change is a claim, and claims must be
  checked, just like facts in the script.

**What is the trade-off between simplicity and faithfulness? (look at "supported claims" in the demo)**
- Simpler language moves away from the paper's wording, and some precise details
  get dropped. In my demo, supported claims fell 43% -> 29% and 71% -> 17%, and the
  gradient formula left the speaker notes.
- Part of the drop is REAL (lost precision, a dropped formula). Part may be my
  CHECKER's limitation: plain-English paraphrases score lower on embedding
  similarity even when true (see Day 6).
- So I don't block simplified edits; the reply WARNS when grounding drops by
  20 points or more, so the user can decide.
- One-line: simpler for the audience usually means less precise and harder to
  verify, so make the cost visible.

**What went wrong & how I fixed it:**
- 1st demo (logs/demo_1_before_fixes_*): the LLM said "made it less technical" but readability went
  DOWN (34 -> 32, 51 -> 39), and said "shortened the script" but it got LONGER (529 -> 538 words).
  Fix: goals.py turns requests into measurable goals; if missed, retry once with the numbers as
  feedback. 2nd demo: readability 29 -> 49 and 42 -> 52, script 467 -> 257 words (target 225).
- LaTeX broke: "\frac" became "<form feed>rac". In JSON, \f \t \b \r are VALID escape codes, so
  unescaped LaTeX is silently corrupted (\e would fail loudly). Fix: repair in llm.py + test.
- Simplifying dropped "supported claims" (43% -> 29%, 71% -> 17%): simpler words drift from the
  paper's wording, and some precision is lost (the gradient formula left the notes). Fix: the reply
  now WARNS when grounding drops by >= 20 points.
- Test bug: my fake LLM matched "make #2 less technical" in the parser's own EXAMPLES, not the message.

## Day 8 — Safety + the chat UI (Streamlit)

**What are the 4 safety layers, and what does each one catch that the others miss?**
- 

**Why is a word list not enough for "no offensive content"? (look at "Wang" and "Dong")**
- 

**What is prompt injection, and where can it come from in THIS project? (2 places)**
- 

**Which safety problems BLOCK an answer, and which only WARN? Why the difference?**
- 

**Frontend vs backend: what does app.py / src/ui do, and what does it NOT do?**
- 

**Why does the retriever live in st.cache_resource but the ChatSession in st.session_state?**
- 

**What went wrong & how I fixed it:**
- The profanity word list flagged the author surnames "Wang" and "Dong" (from the references) and
  normal research words ("kill the process", "sexual harassment detection"). Blocking them would block
  the paper itself and people's names - which is the discriminatory part. Fix: research words are
  always allowed, and words that appear in the SOURCES are allowed (the model is quoting the paper).
  Found by running the checker on my own papers and outputs BEFORE trusting it.
- On real saved talks, the accessibility checks found real problems: "CNN" never spelled out in the
  press talk, "CPU" for policymakers, 37-48 word sentences. In the UI demo
  (logs/demo_3_ui_safety_*), asking "make the whole talk simpler ... spell out every acronym" removed
  the acronym warnings and raised readability 39 -> 46 (floor for the press is 50, so 1 warning left).
- Gemini's safety filter is OFF by default for newer models (per Google's docs), and a blocked answer used to look like
  "invalid JSON". Fix: set safety_settings explicitly + blocked_reason() gives a clear message.
- Streamlit sends usage statistics by default -> turned off in .streamlit/config.toml.
- Uploaded papers can hide instructions (white text in a PDF). Fix: upload.py drops chunks that look
  like prompt injection, and grounding rule 6 says the SOURCES are data, not orders.
- In the browser, "v2 ... Why it changed ... Measured" ran together into one paragraph and the
  safety heading stuck to the last bullet. Markdown ignores a single line break (the terminal does
  not), so my terminal tests never showed it. Fix: blank lines between paragraphs + a test.
  Lesson: test in the real UI, not only in the terminal.
