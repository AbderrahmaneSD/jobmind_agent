"""
tailor.py — Node 5: rewrite the resume + cover letter for each shortlisted job.

STUB: returns the resume unchanged.
Next step: prompt Groq with the JD + resume; never invent skills.
"""
from agent.state import AgentState, TailoredApplication


def tailor_node(state: AgentState) -> dict:
    apps: list[TailoredApplication] = [
        {
            "job": job,
            "tailored_resume": state["resume_text"],
            "cover_letter": f"Stub cover letter for {job['listing']['company']}.",
            "key_changes": [],
        }
        for job in state["shortlist"]
    ]
    return {"applications": apps}
