"""
analyzer.py — Node 3: score every job against the resume.

Two parts, kept separate on purpose:
  1. LLM judgment  -> the 4 dimension scores (STUB for now: fixed numbers)
  2. Python math   -> total score, dates, urgency (REAL already)
The LLM judges; Python does arithmetic and rules.
"""
from datetime import date
from agent.state import AgentState, JobAnalysis, JobListing
from config import SCORE_WEIGHTS, APPLY_THRESHOLD, FRESH_DAYS, RECENT_DAYS


# ── Python helpers (deterministic, unit-testable) ────────────────────────────
def weighted_total(scores: dict) -> int:
    """scores = {"skills": 85, "experience": 70, ...} -> weighted int 0-100."""
    return round(sum(scores[k] * w for k, w in SCORE_WEIGHTS.items()))


def days_since(posted_date: str | None, today: date) -> int | None:
    if not posted_date:
        return None
    return (today - date.fromisoformat(posted_date)).days


def urgency_label(days: int | None) -> str:
    if days is None:
        return "unknown"
    if days < FRESH_DAYS:
        return "fresh"
    if days < RECENT_DAYS:
        return "recent"
    return "old"


def is_expired(expiry_date: str | None, today: date) -> bool:
    return bool(expiry_date) and date.fromisoformat(expiry_date) < today


# ── LLM part (STUB) ──────────────────────────────────────────────────────────
def llm_score(jd_text: str, resume_text: str, listing: JobListing) -> dict:
    """STUB. Next step: prompt Groq and parse JSON output."""
    in_toronto = "toronto" in listing["location"].lower()
    return {
        "scores": {"skills": 80, "experience": 70, "domain": 85,
                   "location": 100 if in_toronto else 40},
        "required_skills": ["Python"], "nice_to_have": [],
        "experience_level": "junior",
        "reasoning": "Stub reasoning.",
    }


# ── The node ─────────────────────────────────────────────────────────────────
def analyzer_node(state: AgentState) -> dict:
    today = date.today()
    jd_by_url = {jd["url"]: jd["jd_text"] for jd in state["scraped_jds"]}
    analyses: list[JobAnalysis] = []

    for listing in state["raw_listings"]:
        jd_text = jd_by_url.get(listing["url"], "")
        listing = {**listing, "days_since_posted": days_since(listing["posted_date"], today)}

        judged = llm_score(jd_text, state["resume_text"], listing)
        s = judged["scores"]
        total = weighted_total(s)
        expired = is_expired(listing["expiry_date"], today)

        analyses.append({
            "listing": listing, "jd_text": jd_text,
            "required_skills": judged["required_skills"],
            "nice_to_have": judged["nice_to_have"],
            "experience_level": judged["experience_level"],
            "skills_score": s["skills"], "experience_score": s["experience"],
            "domain_score": s["domain"], "location_score": s["location"],
            "total_score": total,
            "worth_applying": total >= APPLY_THRESHOLD and not expired,
            "is_expired": expired,
            "urgency": urgency_label(listing["days_since_posted"]),
            "score_reasoning": judged["reasoning"],
        })

    return {"analyses": analyses}
