"""
scraper.py — Node 2: make sure every listing has full job description text.

Google Jobs (via SerpAPI) usually returns the description already, so we
reuse it. Only listings without one will need real scraping (later step:
tools/scraper_tool.py). For now those get empty text and an error note.
"""
from agent.state import AgentState


def scraper_node(state: AgentState) -> dict:
    jds, errors = [], []

    for job in state["raw_listings"]:
        if job["description"]:
            jds.append({"url": job["url"], "jd_text": job["description"]})
        else:
            # STUB: real scraping comes later
            jds.append({"url": job["url"], "jd_text": ""})
            errors.append(f"scraper: no description for {job['title']} @ {job['company']}")

    return {"scraped_jds": jds, "errors": errors}
