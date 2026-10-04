"""
run_skeleton.py — run the full graph once with fake data.
Proves every node is wired correctly before any real API is added.
Usage: python run_skeleton.py
"""
from agent.graph import jobmind_graph

initial_state = {
    "search_query": "Machine Learning Engineer",
    "location": "Toronto, ON",
    "resume_text": "Abderrahmane — ML Engineer. Python, PyTorch, LangChain, FAISS.",
    "num_results": 10,
    "raw_listings": [], "scraped_jds": [], "analyses": [],
    "shortlist": [], "skipped": [], "applications": [], "errors": [],
}

final = jobmind_graph.invoke(initial_state)

print(f"Found {len(final['raw_listings'])} jobs, analyzed {len(final['analyses'])}\n")
for a in final["analyses"]:
    l = a["listing"]
    print(f"{a['total_score']:>3}/100  {l['title']} @ {l['company']}  "
          f"[{a['urgency']}, posted {l['days_since_posted']}d ago, expired={a['is_expired']}]  "
          f"apply={a['worth_applying']}")
print(f"\nShortlisted: {len(final['shortlist'])}   Applications: {len(final['applications'])}")
