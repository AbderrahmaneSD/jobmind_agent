"""
searcher.py — Node 1: find job listings.

STUB: returns fake listings so the whole graph can run end to end.
Next step: replace the body with a call to tools/serp_tool.py (SerpAPI).
"""
from agent.state import AgentState, JobListing


def searcher_node(state: AgentState) -> dict:
    # Reads: search_query, location, num_results
    fake: list[JobListing] = [
        {
            "title": "Machine Learning Engineer", "company": "Acme AI",
            "location": "Toronto, ON", "url": "https://example.com/job/1",
            "source": "stub", "posted_date": "2026-10-01",
            "expiry_date": None, "days_since_posted": None,
        },
        {
            "title": "Data Analyst", "company": "Beta Corp",
            "location": "Vancouver, BC", "url": "https://example.com/job/2",
            "source": "stub", "posted_date": "2026-09-10",
            "expiry_date": "2026-09-30", "days_since_posted": None,
        },
    ]
    # Writes: raw_listings
    return {"raw_listings": fake[: state["num_results"]]}
