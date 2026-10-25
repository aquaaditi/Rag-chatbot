Here's everything from today in one place, in simple language, grouped by topic. The four questions you asked are in **Part 2**.

             **  # DAY -  1**
I'd suggest saving it as `INTERVIEW_QA.md` in your project and adding to it every day. By the end, it becomes your full revision sheet.

---

# Part 1: Project setup and Git

**Q1. What is a virtual environment (venv), and why use one?**
A private folder of Python libraries just for this project. Different projects can need different versions of the same library; a venv keeps them from clashing.

**Q2. What is `.gitignore`?**
A list of files Git should pretend don't exist, so they never get committed or uploaded to GitHub.

**Q3. Why do we ignore `venv/`, `.env` and `__pycache__/`?**
- `.env` holds secrets such as your API key.
- `venv/` is huge and only works on your computer.
- `__pycache__/` is junk Python creates automatically.

**Q4. What's the difference between `.env` and `.env.example`?**
`.env` has your **real** secrets and is never uploaded. `.env.example` has **fake placeholders** and *is* uploaded, so others know which settings they need to fill in.

**Q5. How do you prove `.env` is really ignored?**
Run `git check-ignore -v .env`. If it prints the `.gitignore` line that matches, it's ignored. If it prints nothing, it isn't. Also check that `.env` doesn't appear in `git status`.

**Q6. If you accidentally commit your API key, why isn't deleting the file enough?**
Git keeps every old snapshot forever, so the key is still in the history. You must **cancel the key and create a new one**.

**Q7. Why commit `requirements.txt` but not `venv/`?**
`requirements.txt` is the **recipe** (a small list of libraries). `venv/` is the **cooked meal** (big, and built for your machine only). Anyone can rebuild it with `pip install -r requirements.txt`.

**Q8. What's the difference between `git add` and `git commit`?**
`git add` **packs the box** by choosing which changes to save. `git commit` **seals the box with a label**, creating a permanent snapshot you can return to.

**Q9. What does "U" (untracked) mean in VS Code?**
Git can see the file, but it has never been saved in a commit.

**Q10. Why don't empty folders show up in `git status`?**
Git tracks files, not folders. An empty folder has nothing to track.

**Q11. What does the "LF will be replaced by CRLF" warning mean?**
Windows and Linux end lines of text differently. Git converts them automatically. It's harmless.

**Q12. Do you have to pay for a Gemini API key?**
No. There's a free tier, which is enough for this project. One catch: on the free tier, Google may use your inputs to improve its models, so don't send private data.

---

# Part 2: Python basics (Day 1 lesson)

**Q13. How does Pydantic validation differ from plain type hints?**
Type hints are **labels**. They help you and your editor, but Python **doesn't check them while the program runs**. Pydantic is a **guard**: it checks the data when an object is created and raises a clear error if something is wrong.
*Example:* `seconds: int` won't stop someone passing `"90"`, but a Pydantic model will reject it, or convert it safely if it can.

**Q14. Why is it better for the app to crash at startup over a bad setting than to keep running?**
**Fail fast, fail clearly.** If the API key is missing, it's better to stop in the first second with "GEMINI_API_KEY is missing" than to fail 10 minutes later, halfway through processing a PDF, with a confusing error. The problem is found early, the message points straight at the cause, and no half-finished work is left behind.

**Q15. Why use `logging` instead of `print` in a server?**
Logging adds a **timestamp**, a **level** (DEBUG, INFO, WARNING, ERROR), and **which file** the message came from. You can turn detail up or down without deleting code, and send logs to files. A server runs all day; when something breaks at 3 a.m., `print` gives you none of that.

**Q16. Why catch `ValidationError` specifically instead of using a bare `except:`?**
A bare `except:` catches **everything**, including real bugs you didn't expect, like a typo in your code. Those bugs then hide silently. Catching `ValidationError` handles only the problem you **expected and know how to deal with**; anything else still crashes loudly so you can find it.

**Q17. What is `BaseSettings`, and how does it read `.env`?**
It's like a Pydantic model that **fills itself from environment variables and the `.env` file**. A field named `gemini_api_key` automatically reads `GEMINI_API_KEY`. It also validates the values.

**Q18. What do `Literal[...]` and `Field(gt=0, le=50)` do?**
`Literal["INFO", "ERROR"]` means only these exact values are allowed. `Field(gt=0, le=50)` means greater than 0 and at most 50.

**Q19. Why should you never log the full API key?**
Log files get shared, copied and uploaded. A key in a log is a leaked key. Show only the last 4 characters, e.g. `****abcd`.

**Q20. What does exit code 1 mean?**
Exit code `0` means success; any other number means failure. Other programs, like scripts or Docker, use it to know whether your program worked.

---

# Part 3: RAG concepts

**Q21. What problem does RAG solve?**
LLMs only know their training data, can make things up, and can't show sources. RAG **looks up relevant text first** and makes the model answer from it, so answers are more factual and traceable.

**Q22. What are the two parts of RAG?**
1. **Retriever**: finds the most relevant pieces of text.
2. **Generator**: the LLM that writes the answer using those pieces.
In SARAL: the retriever searches the uploaded paper's chunks; the generator is Gemini.

**Q23. What are parametric and non-parametric memory?**
- **Parametric**: knowledge stored *inside* the model's weights. You can't easily update or inspect it.
- **Non-parametric**: knowledge stored *outside* the model in a searchable index. Easy to update and to cite.

**Q24. Why can RAG show sources when a normal LLM can't?**
In a normal LLM, knowledge is mixed into millions of numbers, with no record of where it came from. In RAG, the retriever returns **specific chunks**, and if each chunk has an ID and a page or slide number, every claim can link to it.

**Q25. Does a citation prove the answer is correct?**
**No.** A citation shows *where the model looked*, not that it understood correctly. The model can still twist the evidence. That's why SARAL uses a separate **Checker** to verify each claim against its cited chunk.

**Q26. How is RAG different from fine-tuning?**
Fine-tuning **changes the model's weights** by training it on new data: slow, costly, and still no citations. RAG **changes what you give the model** at question time: works instantly on a new document, and it can cite sources.

**Q27. What is a chunk?**
A small piece of a document, like a paragraph, bullet, equation or slide note, stored with its location (page or slide).

**Q28. Why split a paper into chunks instead of sending the whole thing?**
- LLMs have a limit on how much text they can read at once.
- Sending only relevant parts is cheaper and faster.
- Citations need small pieces with exact locations; "the whole paper" isn't a useful citation.
(If a paper is short enough to fit, sending it whole can be fine. You'll learn this trade-off later.)

**Q29. What is an embedding?**
A list of numbers (a vector) representing a text's **meaning**. Texts with similar meanings get similar vectors, even if they use different words.

**Q30. What is cosine similarity?**
A way to measure how similar two vectors are, using the angle between them. Close to **1** means very similar meaning; close to **0** means unrelated.

**Q31. Two chunks use completely different words but have high cosine similarity. What does that tell you?**
They **mean** similar things, e.g. "car crash" and "vehicle accident." This is the strength of embeddings: they find matches by meaning, not just by matching words.

**Q32. How does search with embeddings work?**
Turn the question into an embedding, compare it with every chunk's embedding using cosine similarity, and return the chunks with the highest scores.

---

# Part 4: About the assignment

**Q33. What's the difference between the RAG paper and the 3 test papers?**
You **study** the RAG paper to learn the idea, and for Part B's video. Your chatbot **processes** the 3 test papers as input documents in Part A.

**Q34. How should you choose the 3 test papers?**
Short conference papers, to keep costs low, that you can understand. They should cover different challenges: one with many equations (tests LaTeX handling), one with results tables (tests number accuracy). You'll also write a human reference script for each one for evaluation.

---

### How to use this
- Don't memorise the words. Read a question, **cover the answer**, and say it aloud.
- Mark any question you can't answer with ❌ and revise it tomorrow.
- Pick any 5 questions and send me your spoken answers. I'll ask follow-ups like an interviewer would.

       # DAY - 2 

# Part 1: Chunking basics

**Q1. What is a chunk?**
A small piece of a document that can be searched and cited on its own. Each chunk carries its text plus where it came from (paper, page, section).

**Q2. Why do we chunk at all? Why not send the whole paper to the LLM?**
- Models can only read a limited amount of text at once (the embedding model reads about 512 tokens).
- Sending only the relevant parts is cheaper and faster.
- Citations need small pieces with exact locations; "the whole paper" isn't a useful citation.
(For a short paper that fits, sending it whole can work. You'll compare both approaches later.)

**Q3. Why about 250 words per chunk?**
It's a balance:
- **Too small:** loses context ("it improved by 4%": what is "it"?).
- **Too big:** mixes topics, so search is less precise and citations are vague.
- 250 words ≈ 330 tokens, which fits the embedding model's ~512-token limit.

**Q4. What happens if a chunk is longer than the embedding model's limit?**
The extra text is **silently cut off**. That part never gets an embedding, so search can't find it. No error appears, which makes it a dangerous bug.

**Q5. What's the difference between a "block" and a "chunk" in your code?**
- A **block** is a natural unit from the PDF: one paragraph or one equation.
- A **chunk** is what gets searched and cited: one or more blocks grouped together, up to about 250 words.
Blocks come from `ingest.py`; chunks come from `chunker.py`.

**Q6. Why split ingestion and chunking into two files?**
Each file has **one job**. `ingest.py` deals with messy PDFs; `chunker.py` deals with grouping text. If you later add PowerPoint or LaTeX input, you only write a new ingester; the chunker stays the same. It's also easier to test each part separately.

---

# Part 2: Messy PDF text

**Q7. Why is text extracted from a PDF messy?**
A PDF stores **where to draw characters on a page**, not sentences and paragraphs. Extraction has to guess the reading order, which is hard with columns, equations, headers and tables.

**Q8. What is a ligature, and why is it a problem?**
Printers join some letter pairs into one symbol, like **ﬁ**. The PDF stores it as a single special character, so "classiﬁcation" doesn't match a search for "classification."

**Q9. How did you fix ligatures?**
With **Unicode NFKC normalisation**, which converts "compatibility" characters into their standard form; `ﬁ` becomes `f` + `i`.
*Bonus point:* NFKC can also change things you might want to keep. For example, a superscript `²` becomes a plain `2`, which could change the meaning of maths. Worth mentioning as a known trade-off.

**Q10. How did you fix hyphenated line breaks?**
When a line ends with `-` followed by a new line, join the two parts: `classi-\nfier` → `classifier`.
*Trade-off:* some words really are hyphenated, like "pre-trained." If one falls at a line break, it becomes "pretrained." A small error, but you should know it exists.

**Q11. What noise did you remove, and why?**
Page numbers, the arXiv stamp in the margin, and the reference list. They add no meaning, waste space in chunks, and can pollute search results.

**Q12. Is removing the reference list always a good idea?**
Not always. You lose the ability to answer "Which papers does this work build on?" For SARAL, scripts and bullets rarely need references, so removing them reduces noise. That's a reasonable choice, but a choice, not a rule.

**Q13. Why did the summation sign Σ come out as the letter "P"?**
In LaTeX's math font, the large Σ symbol is stored in the **same slot as the letter "P"**, and the PDF doesn't record that it's really Σ. The extractor reads the slot and returns "P." This shows that **a PDF can't reliably give back maths**.

---

# Part 3: Keeping maths intact

**Q14. Why must an equation never be split?**
Half an equation is meaningless or misleading. Splitting breaks search, makes Gemini write wrong maths, and makes citations unverifiable. The assignment also explicitly requires preserving equations.

**Q15. How does your code detect an equation in a PDF?**
In a PDF, equations break into **many tiny fragments** sitting next to each other. The code groups neighbouring small fragments, and if the group contains maths symbols, it's labelled `math`.

**Q16. Why does a math block stay with the sentence before it?**
Because the sentence **introduces** it, e.g. "The softmax with temperature is computed as:". The equation alone doesn't say what it is; the sentence alone doesn't say how. Together they're one idea.

**Q17. How does math protection work for LaTeX files?**
1. `protect_math` replaces each equation with a placeholder like `⟦MATH_3⟧`.
2. The splitter cuts the text; placeholders are treated as single words, so they can't be cut.
3. `restore_math` swaps the real equations back in.
It's like covering something fragile before moving furniture.

**Q18. PDF or LaTeX source: which is better for maths, and why?**
**LaTeX source.** It contains the exact equations (`\frac{...}{...}`), while a PDF only has drawn shapes that extract as jumbled characters. Papers on arXiv usually provide the `.tex` source. PDF support is still needed, because users will often upload only a PDF.

**Q19. What's the limitation of your math detection on PDFs?**
It **guesses** using fragment size and symbols, so it can miss an equation or wrongly label something (e.g. a table with numbers) as maths. Even when detected correctly, the extracted text isn't real LaTeX.

---

# Part 4: Chunk design rules

**Q20. Why does a chunk never cross a page boundary?**
So each chunk has **exactly one page to cite**. A citation like "page 3–4" is less precise and harder to show to the user.

**Q21. What's the downside of page-bounded chunks?**
A paragraph that continues onto the next page gets **split in two**, and both halves lose some context. You also get some very small chunks at the end of pages.

**Q22. Why does a chunk never cross a section boundary?**
Sections are about different topics (Method vs Results). Mixing them makes a chunk less focused, so search matches it less precisely. The section name also becomes useful metadata for citations.

**Q23. What is overlap, and why use it?**
The last sentence of one chunk is repeated at the start of the next. If an important idea sits right at a boundary, at least one chunk contains it with its context.

**Q24. What are the costs of overlap?**
- Duplicate text, so more storage and more embeddings to compute.
- Search can return **two chunks with the same sentence**, wasting space in the prompt.
- As you found, overlap can create bugs, like duplicating a whole table.

**Q25. Why skip overlap when the sentence is over 40 words?**
A very long "sentence" is often a table or messy text without full stops. Copying it would make the next chunk too large, which is exactly the 447-word bug you fixed.

**Q26. How do you split a paragraph that's too long?**
At **sentence endings**, so no sentence is cut in half. If there are no sentence endings (like a table), it's cut into **word windows**: fixed groups of words.

---

# Part 5: Chunk IDs and provenance

**Q27. What does `P3_p2_c06` mean?**
Paper 3, page 2, chunk 6. In your code, the chunk number **restarts on each page**.

**Q28. What is provenance?**
Being able to say **exactly where** a piece of information came from. In SARAL, every generated claim must link to the chunk(s) it's based on. The assignment requires this.

**Q29. Why must chunk IDs be stable?**
Saved drafts store citations as IDs. If re-running the chunker gave different IDs, old citations would point to the **wrong text**, which is worse than no citation.

**Q30. Why restart chunk numbers on each page instead of counting across the whole paper?**
Two reasons:
- The ID is **readable**: you can see the page immediately.
- **Changes stay local**: if the chunking on page 2 changes, IDs on page 5 don't shift.

**Q31. When could your IDs still change, and how would you protect against it?**
If you **change the chunking rules** (size, overlap, cleaning), the same page may split differently. Protections:
- store the chunk **text** together with each saved citation, so old drafts still show the right evidence;
- record a **version** of the ingestion settings with each document;
- or build IDs from a **hash of the chunk's content**, so the same text always gets the same ID.

**Q32. Why use zero padding (`c06`, not `c6`)?**
So IDs **sort correctly** as text: `c06` before `c10`. Without padding, `c10` would sort before `c6`.

---

# Part 6: Debugging and testing

**Q33. Tell me about a bug you found on real data.** *(very common interview question)*
Use the STAR shape: **situation, problem, how you found it, fix, lesson**.
*Example:* "A chunk came out at 447 words, far above my 250 limit. I opened the JSON and saw a table duplicated, because the overlap step copied a very long 'sentence' (the table had no full stops). I capped overlap at 40 words and added word-window splitting for text without sentence endings. The lesson was to inspect the actual output, not just check that the code runs."

**Q34. Tell me about the heading bug.**
The heading "4.1 … vs. …" wasn't recognised, because the code assumed headings don't contain full stops, and "vs." has one. The fix was to allow full stops inside headings. Real data always breaks assumptions.

**Q35. Why write automated tests for chunking?**
Tests check the **main promises automatically** every time you change the code: equations are never cut, IDs are unique, text is clean, references are removed. Without them, a fix for one bug can silently break something else.

**Q36. Your tests pass. Does that mean chunking is correct?**
No. Tests only check what you **thought** to test. Both of your bugs were found by **looking at real output**, not by tests. The right habit is: find a bug by inspection, fix it, then **add a test** so it can't come back.

**Q37. How would you test "equations are never split"?**
For each math block in the input, check that its **full text appears inside a single chunk**. If any chunk contains only part of it, the test fails.

---

# Part 7: Follow-up questions interviewers might ask

**Q38. Why not just use a ready-made splitter, like LangChain's text splitter?**
Generic splitters cut by character or token count and don't know about **equations, pages or sections**. SARAL needs math-safe, page-located chunks for citations, so custom rules are justified. A ready-made splitter could still be used inside, for splitting plain paragraphs.

**Q39. How would you handle a scanned PDF?**
A scanned PDF is just images, so text extraction returns almost nothing. You'd detect that (very few characters per page) and either run **OCR** (optical character recognition) or reject the file with a clear message.

**Q40. How would chunking work for a PowerPoint deck?**
Use the slide structure: each bullet, each speaker-notes section, or each slide becomes a piece, with the **slide number** as the location. Slides are already small, so you rarely need word-count splitting.

**Q41. How would you handle a 300-page paper?**
Chunking works the same, just with many more chunks. The bigger changes are elsewhere: ingest in a **background job** so the upload doesn't time out, embed chunks in **batches**, and rely on **retrieval** because the whole paper won't fit in the prompt.

**Q42. What would you improve in your chunker next?**
Honest options:
- use the `.tex` source when available, for exact maths;
- handle tables as their own block type;
- allow paragraphs to continue across a page break;
- tune chunk size using retrieval evaluation (recall@k) instead of guessing 250.

**Q43. How would you know 250 words is actually the right size?**
You **don't** yet. You'd measure it: build a small set of questions with known answer chunks, try different sizes (150, 250, 400), and compare **recall@k**. That's part of the retrieval evaluation coming up.

---

### How to practise
- Cover the answers and say them aloud. **Q33, Q36 and Q43** are the ones interviewers love most, because they test real experience and honesty.
- Mark anything you can't explain with ❌. Tell me which ones, and I'll explain them differently, with an example from your own chunks.     

# Day 3 — Lessons from my own retrieval results
**Q. Is hybrid search always better than dense or BM25 alone?**
No. For "making a big model smaller", dense search found the right Introduction
chunks by meaning. BM25 matched the word "big" and found a less relevant chunk
("ensembles ... on very big datasets"), and hybrid ranked that noisy chunk #1.
RRF can mix one method's noise into the final ranking. That's why I don't assume
hybrid wins; I measure each mode.

**Q. Tell me about a retrieval failure you found.**
For "SST-2 accuracy", the right answer is in paper 1 (Kim's sentiment
benchmarks), but BM25 and hybrid returned mostly paper 3 chunks. I expected BM25
to win on an exact dataset name, so the result surprised me. I checked the cause
instead of guessing: (fill in after your checks, e.g. "BM25 split 'SST-2' into
'sst' and '2', and '2' appears everywhere").

**Q. Why can names like "SST-2" be hard for BM25?**
BM25 depends on how text is split into words. If "SST-2" is split into "sst" and
"2", the "2" matches page numbers, section numbers and tables everywhere, adding
noise. A fix is to keep hyphenated names together as one token, and split the
question and the chunks the same way.

**Q. How do tables affect retrieval?**
Tables come out of PDFs as jumbled words and numbers, so a results table may not
read clearly as "SST-2 accuracy 87%". Both BM25 and embeddings struggle with that
text. Better table extraction, or adding a short description of each table, would
help.

**Q. Your hybrid scores were 0.030–0.033. What does that tell you?**
The top results are almost tied, so the ranking is fragile: a small change could
reorder them. That's another reason to judge retrieval over many questions, not
one.

**Q. How do you know your retrieval is good?**
Not by looking at a few examples. One of my test queries worked well, one failed,
and hybrid wasn't always best. The right way is a small labelled set (about 20
questions, each with its correct chunk ID) and recall@5 for each mode. That turns
"it looks good" into a number.

**Q. What did you learn from comparing the modes?** (short version)
My assumptions were wrong twice: BM25 didn't win on "SST-2", and hybrid didn't win on "making a big model smaller". So I test with real queries and measure, instead of trusting what should happen in theory.

       #DAY - 4 generation (the first complete RAG answer)

# Day 4 — Generation (the first complete RAG answer)

## The pipeline

**Q1. Walk me through what happens when a user asks for a script.**
"The request comes with an audience, length and style. I retrieve relevant
chunks, always putting the abstract first, then format each chunk with its ID
and location. I fill the prompt template with the parameters and the chunks, and
send it to Gemini with a system prompt of grounding rules. Gemini returns a script
with chunk IDs in brackets, and my code checks that every cited ID really exists."
One line: retrieve → format → prompt → Gemini → check citations.

**Q2. What is the 'G' in RAG doing in your system?**
"Gemini writes the script, but only from the retrieved chunks. Retrieval decides
what evidence it sees; generation decides how to explain it for the audience."
One line: retrieval finds the evidence; generation explains it.

## Prompts

**Q3. Why use a prompt template instead of writing a new prompt each time?**
"The pipeline stays the same and only the parameters change. That makes outputs
consistent, easy to test and easy to compare across audiences."
One line: one template, many requests, consistent results.

**Q4. What are your four template parameters?**
"{audience}: policymakers, grad students or press. {length}: 30s, 90s or 5 min,
turned into a word target at 150 words per minute. {style}: technical, plain
English or press release. {change_instruction}: an edit request for iterative
changes, empty for a first draft."
One line: who, how long, what tone, and what to change.

**Q5. Why separate the system prompt from the user prompt?**
"The system prompt holds fixed rules for every request: use only the sources,
cite every fact, keep numbers exact, use LaTeX for maths, use safe and accessible
language. The user prompt holds what changes: the task and the chunks. Keeping
them apart stops the rules getting lost in the content, and models give system
instructions higher priority."
One line: fixed rules in the system prompt; the changing task in the user prompt.

**Q6. Which rule fights hallucination most?**
"'Use ONLY the provided sources', combined with 'cite every sentence'. The first
limits what the model can say; the second makes every claim checkable."
One line: only-the-sources plus cite-everything.

**Q7. Does grounding eliminate hallucination?**
"No, it reduces it. In my own output, one sentence cited a valid chunk but
misstated what N meant. Grounding limits the evidence; it doesn't guarantee the
model reads it correctly. That's why I need claim-level checking."
One line: grounding reduces hallucination but doesn't remove it.

## Context and citations

**Q8. How do you format chunks for the LLM, and why?**
"Each chunk is shown as [P3_p2_c06] with its paper, page and section, then its
text. The model sees exactly which ID to cite, and the location helps it
understand where the text came from."
One line: every chunk carries its ID so the model can cite it.

**Q9. Why does the abstract always come first?**
"The abstract is the authors' own reliable summary, so it gives the model the big
picture before the details. It also guarantees the main claims are always
available, even if retrieval misses something."
One line: the abstract gives a reliable overview every time.

**Q10. Why do longer scripts get more chunks?**
"A 30-second script needs a few facts; a 5-minute script needs many. So I use 4,
6 or 10 chunks. More chunks give more coverage but cost more tokens and can add
less relevant text."
One line: more length needs more evidence, at the cost of tokens and noise.

**Q11. What does your citation check do, and what can't it do?**
"It finds every cited ID and flags any that don't exist among the provided
chunks, so it catches invented citations. It can't tell whether the sentence is
actually supported by the chunk; my N-meaning error had a valid citation."
One line: it checks citations exist, not that they're correct.

**Q12. What's an invented citation, and why does it matter?**
"An ID the model made up, like P3_p9_c04 when that chunk doesn't exist. It looks
trustworthy but points nowhere, which is worse than no citation."
One line: a fake citation creates false trust.

## Length, audience, style

**Q13. How do you control length?**
"I convert time into a word target at about 150 spoken words per minute, so 90
seconds is about 225 words, and put it in the prompt. My scripts came out at 199
and 219, close but not exact, because LLMs don't count words precisely. So I
measure the length after generation."
One line: a word target in the prompt, then measure.

**Q14. How does the output change for different audiences?**
"For policymakers: plain words, impact and why it matters, few technical terms.
For grad students: methods, equations in LaTeX, precise terms. For press: a news
style with a strong opening."
One line: same evidence, different emphasis and vocabulary.

## Design and testing

**Q15. Why does the generator take `llm` and `retriever` as parameters?**
"Dependency injection. Tests pass in a fake LLM and a fake retriever, so they run
fast, offline, free and give the same result every time. It also lets me swap in
a different model or retrieval mode without changing the generator."
One line: inject dependencies so they can be faked or swapped.

**Q16. What can tests with a fake LLM NOT tell you?**
"Whether the real model follows the prompt well. Fakes test my code: parsing,
citation checking, saving. Output quality needs real runs checked against the
paper, and later an evaluation set."
One line: fakes test the code, not the model's quality.

**Q17. Why save every run with its prompt, sources and output?**
"It's evidence. I can reproduce and debug any output, compare prompt versions,
and the assignment asks for example runs and conversation logs."
One line: saved runs make outputs reproducible and checkable.

## Your error stories (most important)

**Q18. Tell me about an error you found in the generated output.**
"The fastText loss lost its 1/N, because the PDF extracted the equation as
'−1 N N X n=1'. I added a prompt rule explaining scrambled PDF equations, and it
then wrote −\frac{1}{N}\sum_{n=1}^{N} correctly. Prompt engineering can fix a
systematic error, but I still check the result."
One line: a prompt rule fixed a scrambled equation.

**Q19. Is it risky to ask the model to rebuild equations?**
"Yes. Rebuilding means the model fills in structure the PDF lost, and it could
build a wrong equation that looks right. So rebuilt maths must be checked
against the paper, and the LaTeX source is better when available."
One line: rebuilding maths helps but can invent errors.

**Q20. Why doesn't a valid citation guarantee a true sentence?**
"I had a sentence saying 'a document with N n-gram features', citing the right
chunk, but in the paper N is the number of documents. The citation proves where
the model looked, not that it understood correctly. That's why SARAL needs a
separate Checker that verifies each claim against its cited chunk."
One line: a citation shows where the model looked, not that it's right.

**Q21. What did the uncited conclusion teach you?**
"The policymaker script added its own conclusion without a citation. Models
like to add a nice ending. I need to measure citation coverage, the share of
sentences with a source, and flag uncited ones."
One line: models add uncited conclusions, so measure coverage.