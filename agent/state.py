# agent/state.py
from typing import TypedDict, Annotated
import operator


class JobListing(TypedDict):
    """One raw job found by the Searcher node."""
    title: str        # e.g. "ML Engineer"
    company: str      # e.g. "Shopify"
    location: str     # e.g. "Toronto, ON (Remote)"
    url: str          # link to the full posting
    source: str       # "google_jobs" | "indeed" | "company_page"


class JobAnalysis(TypedDict):
    """One job fully analyzed by the Analyzer node."""
    listing: JobListing      # the original listing
    jd_text: str             # full cleaned job description text
    required_skills: list[str]   # skills the JD explicitly asks for
    nice_to_have: list[str]      # preferred but not required
    experience_level: str        # "junior" | "mid" | "senior"
    # Fit scores (0–100 each, weighted into total_score)
    skills_score: int
    experience_score: int
    domain_score: int
    location_score: int
    total_score: int         # weighted average
    score_reasoning: str     # one paragraph explaining the score
    worth_applying: bool     # total_score >= APPLY_THRESHOLD (config)


class TailoredApplication(TypedDict):
    """Final output for one job — everything ready to send."""
    job: JobAnalysis
    tailored_resume: str     # full resume text rewritten for this job
    cover_letter: str        # custom cover letter
    key_changes: list[str]   # bullet list of what was changed and why


class AgentState(TypedDict):
    # --- Input (set by app.py before graph runs) ---
    search_query: str            # e.g. "ML Engineer Toronto"
    location: str                # e.g. "Toronto, ON"
    resume_text: str             # raw text extracted from your PDF
    num_results: int             # how many jobs to search (default 10)

    # --- Searcher output ---
    raw_listings: list[JobListing]   # all jobs found, before scraping

    # --- Scraper output ---
    # Annotated + operator.add so scraped JDs accumulate across retries
    scraped_jds: Annotated[list[dict], operator.add]

    # --- Analyzer output ---
    analyses: Annotated[list[JobAnalysis], operator.add]

    # --- Ranker output ---
    shortlist: list[JobAnalysis]     # top N jobs worth applying to
    skipped: list[JobAnalysis]       # jobs below threshold, with reasons

    # --- Tailor output ---
    applications: Annotated[list[TailoredApplication], operator.add]

    # --- Meta ---
    errors: Annotated[list[str], operator.add]   # non-fatal errors logged
    total_found: int             # total jobs found by Searcher
    total_analyzed: int          # how many were fully analyzed