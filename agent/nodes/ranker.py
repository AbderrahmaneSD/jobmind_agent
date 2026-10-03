"""
ranker.py — Node 4: sort jobs and split them into shortlist / skipped.

REAL already: pure Python, no LLM needed. Sorting is not a judgment call.
"""
from agent.state import AgentState
from config import TOP_N

URGENCY_ORDER = {"fresh": 0, "recent": 1, "unknown": 2, "old": 3}


def ranker_node(state: AgentState) -> dict:
    # Highest score first; fresher posting wins a tie.
    ranked = sorted(
        state["analyses"],
        key=lambda a: (-a["total_score"], URGENCY_ORDER[a["urgency"]]),
    )
    worth = [a for a in ranked if a["worth_applying"]]
    return {
        "shortlist": worth[:TOP_N],
        "skipped": [a for a in ranked if a not in worth[:TOP_N]],
    }
