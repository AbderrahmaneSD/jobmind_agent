"""
config.py — single source of truth for settings.

Every other file imports its settings from here. Nothing is hardcoded elsewhere,
so changing a model name or a threshold means editing exactly one line.
"""
import os
from dotenv import load_dotenv

# Read key=value pairs from the .env file into environment variables.
# In CI (GitHub Actions) there is no .env file; real env vars are used instead.
load_dotenv()

# ── API keys (secrets: always from the environment, never in code) ───────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

# ── Models ───────────────────────────────────────────────────────────────────
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
EMBED_MODEL = "all-MiniLM-L6-v2"   # same embedding model as ml-research-assistant

# ── Search ───────────────────────────────────────────────────────────────────
DEFAULT_NUM_RESULTS = 10           # how many job listings to search for

# ── Scoring ──────────────────────────────────────────────────────────────────
# Weights of the 4 fit dimensions. They must sum to 1.0.
SCORE_WEIGHTS = {
    "skills": 0.40,
    "experience": 0.25,
    "domain": 0.20,
    "location": 0.15,
}
APPLY_THRESHOLD = 70               # total_score >= this → worth applying
TOP_N = 3                          # how many shortlisted jobs get a tailored resume

# ── Freshness (days since posted) ────────────────────────────────────────────
FRESH_DAYS = 3                     # < 3 days  → "fresh"
RECENT_DAYS = 14                   # < 14 days → "recent", otherwise "old"

# ── Paths ────────────────────────────────────────────────────────────────────
RESUME_INDEX_PATH = os.getenv("RESUME_INDEX_PATH", "data/resume_index")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
