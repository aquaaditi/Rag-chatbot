## 1. RAG and LLM basics

| Word | Simple meaning |
|---|---|
| **LLM** (Large Language Model) | An AI model trained on huge amounts of text that can read and write language. Gemini is an LLM. |
| **Prompt** | The text you send to an LLM: your instructions plus any evidence. |
| **Token** | A small piece of text the model reads, often part of a word. Roughly, 100 words ≈ 130 tokens. |
| **Context window** | The maximum number of tokens a model can read at once. |
| **Hallucination** | When an LLM states something false or made up as if it were true. |
| **RAG** (Retrieval-Augmented Generation) | First **find** relevant text from documents, then let the LLM **write** the answer using that text. |
| **Retrieval** | Searching a collection of documents for the most relevant pieces. |
| **Retriever** | The part of the system that does retrieval. |
| **Generation** | The LLM writing the output (answer, script, bullets). |
| **Generator** | The model that does generation (Gemini in SARAL). |
| **Grounded** | An answer based only on the given evidence, not on the model's memory. |
| **Parametric memory** | Knowledge stored inside the model's weights. Hard to update or cite. |
| **Non-parametric memory** | Knowledge stored outside the model, in a searchable index. Easy to update and cite. |
| **Weights / parameters** | The millions of numbers inside a model that store what it learned. |
| **Fine-tuning** | Training an existing model further on new data to change its weights. |

## 2. Citations and trust

| Word | Simple meaning |
|---|---|
| **Citation** | A reference showing where a claim came from, e.g. "Paper 3, page 2." |
| **Provenance** | The ability to trace every piece of output back to its exact source. |
| **Claim** | One statement in the generated output that could be true or false. |
| **Evidence** | The source text used to support a claim. |
| **Checker** | A separate step that verifies whether each claim is really supported by its cited evidence. |
| **Factuality** | Whether the output is factually correct according to the source. |

## 3. Ingestion and chunking (Day 2)

| Word | Simple meaning |
|---|---|
| **Ingestion** | Taking an uploaded file and turning it into clean, searchable pieces. |
| **Parsing** | Reading a file's format (PDF, PPTX, LaTeX) to get its text and structure. |
| **Text extraction** | Pulling the text out of a file such as a PDF. |
| **Block** | A natural unit from the document: one paragraph or one equation. |
| **Chunk** | A searchable, citable piece of a document (up to about 250 words in your project). |
| **Chunking** | Splitting a document into chunks. |
| **Chunk ID** | A unique label for a chunk, e.g. `P3_p2_c06` = paper 3, page 2, chunk 6. |
| **Stable ID** | An ID that stays the same every time you process the same file. |
| **Overlap** | Repeating a bit of text (one sentence) at the start of the next chunk so ideas on boundaries aren't lost. |
| **Word window** | Splitting text into fixed groups of words, used when there are no sentence endings (like tables). |
| **Page-bounded** | A chunk never goes across two pages. |
| **Metadata** | Extra information stored with data, e.g. a chunk's page, section and type. |
| **Noise** | Useless text that hurts search, e.g. page numbers or the arXiv stamp. |
| **Edge case** | An unusual input that can break your code, like a table or an odd heading. |
| **Heuristic** | A rule of thumb that works most of the time but isn't guaranteed, e.g. "small fragments with maths symbols are an equation." |

## 4. PDF and text cleaning

| Word | Simple meaning |
|---|---|
| **PDF** | A file format that stores **where to draw** text on a page, not sentences and paragraphs. |
| **Scanned PDF** | A PDF that is just a picture of a page. It has no real text to extract. |
| **OCR** (Optical Character Recognition) | Software that reads text from images, used for scanned PDFs. |
| **Ligature** | Two letters printed as one symbol, like **ﬁ**. |
| **Unicode** | The standard numbering system for every character in every language. |
| **NFKC normalisation** | A Unicode rule that converts special characters into standard ones, e.g. `ﬁ` → `f` + `i`. |
| **Hyphenation** | A word split across two lines with a hyphen, like `classi-` / `fier`. |
| **LaTeX** | A language researchers use to write papers, especially for maths, e.g. `\frac{a}{b}`. |
| **`.tex` file** | The LaTeX source file of a paper, with exact text and equations. |
| **Placeholder** | A temporary label (like `⟦MATH_3⟧`) that stands in for something to protect it. |

## 5. Search (coming in the retrieval days)

| Word | Simple meaning |
|---|---|
| **Index** | A data structure that makes search fast, like the index at the back of a book. |
| **Keyword search** | Finding text that contains the same words as the query. |
| **BM25** | A popular keyword-search scoring method. Rare words that match count more. |
| **Embedding** | A list of numbers representing a text's **meaning**. |
| **Vector** | A list of numbers. An embedding is a vector. |
| **Cosine similarity** | A score for how similar two vectors are: close to 1 = similar meaning, 0 = unrelated. |
| **Semantic search** | Searching by meaning using embeddings, so different words with the same meaning still match. |
| **Hybrid search** | Combining keyword search (BM25) and semantic search to get the strengths of both. |
| **RRF** (Reciprocal Rank Fusion) | A simple way to merge two ranked result lists into one, using rank positions instead of scores. |
| **pgvector** | An add-on for PostgreSQL that stores and searches vectors. |
| **Top-k** | The best *k* results, e.g. top 5. |

## 6. Evaluation

| Word | Simple meaning |
|---|---|
| **Evaluation** | Measuring how well the system works, with numbers. |
| **Recall@k** | Out of all the correct chunks, how many appeared in the top *k* results. |
| **Precision@k** | Out of the top *k* results, how many were actually correct. |
| **Reference script** | Your human-written script that the chatbot's output is compared against. |
| **ROUGE** | A score that measures word overlap between generated text and a reference. |
| **BERTScore** | A score that measures meaning similarity between generated text and a reference, using embeddings. |
| **Citation coverage** | What percentage of generated content has a source citation. |
| **Human evaluation** | People rating outputs, e.g. for audience fit, factuality and helpfulness. |

## 7. Python and coding

| Word | Simple meaning |
|---|---|
| **Type hint** | A label saying what type a value should be, e.g. `seconds: int`. Python doesn't enforce it. |
| **Pydantic** | A library that checks data matches the expected types and rules, and gives clear errors. |
| **Validation** | Checking that data is correct before using it. |
| **`BaseSettings`** | A Pydantic class that loads and validates settings from environment variables and `.env`. |
| **Exception** | An error that stops normal execution, e.g. `ValueError`. |
| **`try` / `except`** | Code that attempts something and handles a specific error if it happens. |
| **Logging** | Recording messages with time, level and source, instead of `print`. |
| **Log level** | How serious a message is: DEBUG < INFO < WARNING < ERROR. |
| **Exit code** | A number a program returns when it ends: 0 = success, anything else = failure. |
| **CLI** (Command-Line Interface) | A program you run by typing a command in the terminal. |
| **Deterministic** | Gives exactly the same output every time for the same input. |
| **JSON** | A common text format for storing structured data, like `{"id": "P3_p2_c06"}`. |
| **Library / package** | Ready-made code you install and use, e.g. `pymupdf`. |

## 8. Testing

| Word | Simple meaning |
|---|---|
| **Automated test** | Code that checks your code works, run with one command. |
| **Unit test** | A test for one small piece of code, such as one function. |
| **pytest** | The Python tool you use to write and run tests. |
| **Regression** | When a change breaks something that used to work. Tests catch these. |
| **Mock** | A fake version of something (like an LLM call) used in tests so they're fast and predictable. |

## 9. Project setup and tools

| Word | Simple meaning |
|---|---|
| **Virtual environment (venv)** | A private folder of libraries for one project. |
| **pip** | The tool that installs Python libraries. |
| **`requirements.txt`** | The list of libraries your project needs (the "recipe"). |
| **Git** | A tool that saves the history of your project as snapshots. |
| **Commit** | One saved snapshot in Git. |
| **`git add`** | Choosing which changes go into the next commit. |
| **Push** | Uploading your commits to GitHub. |
| **`.gitignore`** | A list of files Git should ignore. |
| **Environment variable** | A setting stored outside the code, e.g. `GEMINI_API_KEY`. |
| **`.env`** | A file holding your real environment variables and secrets. Never uploaded. |
| **`.env.example`** | A template with fake placeholder values. Safe to upload. |
| **API** | A way for one program to talk to another, e.g. your code asking Gemini for text. |
| **API key** | A secret password that lets your code use an API. |
| **Free tier** | Free usage of a service, with limits. |

## 10. Coming up later in your plan

| Word | Simple meaning |
|---|---|
| **FastAPI** | A Python framework for building web APIs. |
| **Endpoint** | One URL your API responds to, e.g. `/upload` or `/search`. |
| **SSE** (Server-Sent Events) | A way for the server to stream text to the browser piece by piece, like typing. |
| **PostgreSQL** | A database for storing documents, chunks, drafts and citations. |
| **Transaction** | A group of database changes that either all succeed or all fail. |
| **Idempotency** | Doing the same operation twice gives the same result, with no double saves. |
| **Agent** | An LLM that can decide to call tools (like search) before answering. |
| **Tool calling** | The LLM asking your code to run a function, e.g. `find_in_deck`. |
| **Structured output** | Making the LLM return data in a fixed format (like JSON) instead of free text. |
| **Prompt injection** | Hidden instructions inside a document that try to trick the LLM. |

---

## Day 4 — Generation

| Word | Simple meaning |
|---|---|
| **Generation** | The LLM writing the output (script, bullets) from the retrieved chunks. The "G" in RAG. |
| **Prompt template** | A fixed prompt with blanks ({audience}, {length}...) filled in for each request. |
| **Template parameter** | One blank in the template, e.g. {style}. |
| **Instantiated example** | A template with its blanks filled in with real values. Part B asks for two. |
| **System prompt** | Fixed rules sent with every request (use only the sources, cite everything). |
| **User prompt** | The part that changes each time: the task plus the chunks. |
| **Grounding** | Making the model answer only from the given evidence. |
| **Grounding rules** | The instructions that enforce grounding, e.g. "use ONLY the sources". |
| **Context** | The chunks given to the LLM inside the prompt. |
| **Context formatting** | How chunks are shown to the LLM, e.g. `[P3_p2_c06] (paper, page, section)` + text. |
| **Context selection** | Choosing which chunks go in the prompt (abstract first, top-k by length). |
| **Word target** | The length goal in words, from time at 150 words per minute (90s ≈ 225 words). |
| **Citation check** | Code that finds cited IDs and checks they exist. |
| **Invented citation** | A chunk ID the model made up that doesn't exist. |
| **Citation coverage** | The share of sentences that have a citation. |
| **Uncited claim** | A sentence with no source, often the model's own conclusion. |
| **Faithfulness** | Whether each claim is actually supported by its cited evidence. |
| **Dependency injection** | Passing what a function needs (like `llm`) as a parameter instead of creating it inside. |
| **Fake / stub** | A simple pretend version of something (like an LLM) used in tests. |
| **Systematic error** | An error that happens the same way every time, e.g. dropping 1/N from scrambled equations. Often fixable with a prompt rule. |
| **Scrambled equation** | An equation that comes out of a PDF as jumbled symbols, e.g. "−1 N N X n=1". |
| **Export / run log** | A saved record of one run: input, prompt, sources and output. |
| **Token budget** | How many tokens you can spend on the prompt and output; more chunks use more of it. |