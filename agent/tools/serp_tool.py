"""
serp_tool.py — Tool: search Google Jobs through SerpAPI.

A TOOL does one concrete job (call an API) and knows nothing about the graph.
The searcher NODE decides when to call it and writes the result into state.

Docs: https://serpapi.com/google-jobs-api
"""
import re
from datetime import date, timedelta

import requests

from agent.state import JobListing

SERPAPI_URL = "https://serpapi.com/search.json"

# Approximate length of each unit, in days, for "posted X <unit> ago".
_UNIT_DAYS = {"minute": 0, "hour": 0, "day": 1, "week": 7, "month": 30}


# ── Pure helpers (no network → easy to unit-test) ────────────────────────────
def parse_posted_at(text: str | None, today: date) -> str | None:
    """
    Convert Google's relative date ("3 days ago", "17 hours ago", "30+ days ago")
    into an absolute ISO date ("2026-10-01"). Returns None if unrecognised.
    Months are approximated as 30 days.
    """
    if not text:
        return None
    t = text.lower().strip()
    if t in ("today", "just posted", "just now"):
        return today.isoformat()

    match = re.search(r"(\d+|an?)\+?\s*(minute|hour|day|week|month)", t)
    if not match:
        return None

    amount_txt, unit = match.groups()
    amount = 1 if amount_txt in ("a", "an") else int(amount_txt)
    return (today - timedelta(days=amount * _UNIT_DAYS[unit])).isoformat()


def extract_posted_date(raw: dict, today: date) -> str | None:
    """
    Google puts the posting age in different places depending on the result:
    1. detected_extensions.posted_at  (structured, when Google parsed it)
    2. extensions                     (raw labels, e.g. ["3 days ago", "Full-time"])
    Try both; return the first one that parses as a date.
    """
    candidates = [(raw.get("detected_extensions") or {}).get("posted_at")]
    candidates += raw.get("extensions") or []
    for text in candidates:
        if isinstance(text, str):
            parsed = parse_posted_at(text, today)
            if parsed:
                return parsed
    return None


def to_listing(raw: dict, today: date) -> JobListing:
    """Map one raw SerpAPI job dict to our JobListing schema."""
    apply_options = raw.get("apply_options") or []
    url = apply_options[0]["link"] if apply_options else raw.get("share_link", "")
    via = raw.get("via", "google_jobs").removeprefix("via ").strip()

    return {
        "title": raw.get("title", ""),
        "company": raw.get("company_name", ""),
        "location": raw.get("location", ""),
        "url": url,
        "source": via,
        "description": raw.get("description", ""),
        "posted_date": extract_posted_date(raw, today),
        "expiry_date": None,        # Google Jobs does not expose an expiry date
        "days_since_posted": None,  # computed later by the Analyzer
    }


# ── Network call ─────────────────────────────────────────────────────────────
def search_google_jobs(
    query: str,
    location: str,
    num_results: int,
    api_key: str,
    country: str = "ca",
    today: date | None = None,
) -> list[JobListing]:
    """
    Return up to `num_results` job listings. Each page holds up to 10 jobs and
    costs ONE SerpAPI search, so 25 results = 3 searches from your quota.
    Raises RuntimeError on API errors (the node decides what to do with it).
    """
    if not api_key:
        raise RuntimeError("SERPAPI_API_KEY is not set (add it to your .env file)")

    today = today or date.today()
    listings: list[JobListing] = []
    params = {
        "engine": "google_jobs",
        "q": f"{query} {location}".strip(),  # location in the query is the most robust
        "gl": country,
        "hl": "en",
        "api_key": api_key,
    }

    seen: set = set()
    max_pages = num_results // 10 + 2   # safety cap so we never loop forever

    for _ in range(max_pages):
        if len(listings) >= num_results:
            break
        response = requests.get(SERPAPI_URL, params=params, timeout=30)
        data = response.json()
        if response.status_code != 200 or "error" in data:
            raise RuntimeError(f"SerpAPI error: {data.get('error', response.status_code)}")

        jobs = data.get("jobs_results", [])
        for job in jobs:
            # Google can repeat a job across pages: skip ones already seen
            key = job.get("job_id") or (job.get("title"), job.get("company_name"))
            if key not in seen:
                seen.add(key)
                listings.append(to_listing(job, today))

        token = (data.get("serpapi_pagination") or {}).get("next_page_token")
        if not jobs or not token:
            break                       # no more pages
        params["next_page_token"] = token

    return listings[:num_results]