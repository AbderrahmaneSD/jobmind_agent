"""
state.py — the schema (blueprint) of the agent's memory.

This file stores no data. It defines the SHAPE of the dict that LangGraph
creates at runtime and passes from node to node.
"""
from typing import TypedDict, Annotated, Optional
import operator


class JobListing(TypedDict):
    """Raw job found by the Searcher — no AI judgment yet."""
    title: str
    company: str
    location: str
    url: str
    source: str                         # "google_jobs" | "company_page" | ...
    posted_date: Optional[str]          # ISO "2026-09-28", None if unknown
    expiry_date: Optional[str]          # ISO "2026-10-28", None if unknown
    days_since_posted: Optional[int]    # computed in Python from posted_date


class JobAnalysis(TypedDict):
    """The same job after the Analyzer compared it to the resume."""
    listing: JobListing
    jd_text: str
    required_skills: list[str]
    nice_to_have: list[str]
    experience_level: str               # "junior" | "mid" | "senior"
    # LLM judgments (0-100)
    skills_score: int
    experience_score: int
    domain_score: int
    location_score: int
    # Python calculations
    total_score: int                    # weighted average of the 4 scores
    worth_applying: bool                # total_score >= APPLY_THRESHOLD
    is_expired: bool                    # expiry_date is in the past
    urgency: str                        # "fresh" | "recent" | "old" | "unknown"
    score_reasoning: str


class TailoredApplication(TypedDict):
    """Final output for one shortlisted job."""
    job: JobAnalysis
    tailored_resume: str
    cover_letter: str
    key_changes: list[str]


class AgentState(TypedDict):
    # --- Input (set by app.py) ---
    search_query: str
    location: str
    resume_text: str
    num_results: int

    # --- Searcher ---
    raw_listings: list[JobListing]

    # --- Scraper (list of {"url": ..., "jd_text": ...}) ---
    scraped_jds: Annotated[list[dict], operator.add]

    # --- Analyzer ---
    analyses: Annotated[list[JobAnalysis], operator.add]

    # --- Ranker ---
    shortlist: list[JobAnalysis]
    skipped: list[JobAnalysis]

    # --- Tailor ---
    applications: Annotated[list[TailoredApplication], operator.add]

    # --- Meta ---
    errors: Annotated[list[str], operator.add]