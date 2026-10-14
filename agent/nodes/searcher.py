"""
searcher.py — Node 1: find job listings.

The node is thin on purpose: it reads inputs from state, calls the tool,
and writes the result back. All API details live in tools/serp_tool.py.
"""
from agent.state import AgentState
from agent.tools.serp_tool import search_google_jobs
from config import SERPAPI_API_KEY, SEARCH_COUNTRY


def searcher_node(state: AgentState) -> dict:
    try:
        listings = search_google_jobs(
            query=state["search_query"],
            location=state["location"],
            num_results=state["num_results"],
            api_key=SERPAPI_API_KEY,
            country=SEARCH_COUNTRY,
        )
    except Exception as e:
        # Don't crash the graph: record the error, continue with zero jobs.
        # The ranker then finds an empty shortlist and the graph ends cleanly.
        return {"raw_listings": [], "errors": [f"searcher: {e}"]}

    return {"raw_listings": listings}