"""
scraper.py — Node 2: fetch the full job description text for each listing.

STUB: returns placeholder text.
Next step: call tools/scraper_tool.py (requests + BeautifulSoup) per URL.
"""
from agent.state import AgentState


def scraper_node(state: AgentState) -> dict:
    # Reads: raw_listings
    jds = [
        {"url": job["url"], "jd_text": f"Placeholder JD for {job['title']} at {job['company']}."}
        for job in state["raw_listings"]
    ]
    # Writes: scraped_jds (appended thanks to operator.add)
    return {"scraped_jds": jds}
