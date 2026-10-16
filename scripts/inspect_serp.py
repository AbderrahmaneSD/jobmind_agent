"""
inspect_serp.py — save one raw SerpAPI response to look at the real data.
Costs 1 SerpAPI search. Usage: python scripts/inspect_serp.py
"""
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import SERPAPI_API_KEY, SEARCH_COUNTRY  # noqa: E402

params = {"engine": "google_jobs", "q": "Machine Learning Engineer Toronto, ON",
          "gl": SEARCH_COUNTRY, "hl": "en", "api_key": SERPAPI_API_KEY}
data = requests.get("https://serpapi.com/search.json", params=params, timeout=30).json()

out = Path("data/serp_raw.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Saved full response to {out}\n")

for job in data.get("jobs_results", []):
    print(f"- {job.get('title')} @ {job.get('company_name')}")
    print(f"    detected_extensions: {job.get('detected_extensions')}")
    print(f"    extensions:          {job.get('extensions')}")
