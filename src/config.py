"""
config.py - every setting of the project in ONE place.

Other modules import their numbers and paths from here, so to change e.g. the
chunk size or the LLM model you only edit this file (or .env for secrets).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # read GEMINI_API_KEY and LLM_MODEL from .env

# ---------------------------------------------------------------- paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
INDEX_DIR = PROJECT_ROOT / "index"  # built by build_index.py (git-ignored, can be rebuilt)

# ---------------------------------------------------------------- LLM (src/llm.py)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-flash-lite-latest")
LLM_TIMEOUT_MS = 120_000  # give up on one request after 2 minutes
LLM_RETRY_ATTEMPTS = 4  # retry when Google is overloaded
LLM_RETRY_STATUS_CODES = [429, 500, 503, 504]

# ---------------------------------------------------------------- ingestion (src/ingestion/)
PROSE_MIN_WORDS = 12  # a PDF block with fewer words is a "fragment" (equation piece, label...)
MIN_FRAGMENT_WORDS = 4  # non-math fragment groups shorter than this are dropped as noise

# ---------------------------------------------------------------- chunking (src/chunking/)
MAX_CHUNK_WORDS = 250  # about 330 tokens
OVERLAP_SENTENCES = 1  # sentences repeated at the start of the next chunk
MAX_OVERLAP_WORDS = 40  # a "sentence" longer than this (e.g. a table) is not repeated

# ---------------------------------------------------------------- retrieval (src/retrieval/)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # free, runs on CPU, reads up to 512 tokens
# bge models work best when a search QUESTION starts with this instruction (passages don't need it)
EMBEDDING_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
TOP_K = 5  # how many chunks to return per search
RRF_K = 60  # constant in Reciprocal Rank Fusion (standard value from the RRF paper)

# ---------------------------------------------------------------- generation (src/generation/)
SPEAKING_WORDS_PER_MINUTE = 150  # average talk speed; turns "90s" into a word target
EXAMPLES_DIR = PROJECT_ROOT / "examples"  # saved example runs (inputs -> outputs)

# ---------------------------------------------------------------- provenance (src/provenance/)
# Cosine similarity between a claim and its best-matching source sentence.
# Calibrated on real outputs - see NOTES.md Day 6.
SUPPORTED_THRESHOLD = 0.80  # at or above: the source clearly says this
WEAK_THRESHOLD = 0.70  # between the two: partly supported / paraphrased loosely
