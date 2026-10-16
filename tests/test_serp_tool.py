"""
Tests for tools/serp_tool.py.

No real network calls: requests.get is replaced (mocked) with a fake that
returns a canned SerpAPI response. Tests stay fast, free and deterministic.
"""
from datetime import date

import pytest

from agent.tools import serp_tool
from agent.tools.serp_tool import (
    parse_posted_at, extract_posted_date, to_listing, search_google_jobs,
)

TODAY = date(2026, 10, 4)

RAW_JOB = {
    "title": "Machine Learning Engineer",
    "company_name": "Acme AI",
    "location": "Toronto, ON",
    "via": "via LinkedIn",
    "description": "We need Python, PyTorch and LLM experience.",
    "share_link": "https://google.com/share/1",
    "apply_options": [{"title": "LinkedIn", "link": "https://linkedin.com/jobs/1"}],
    "detected_extensions": {"posted_at": "3 days ago"},
}


# ── parse_posted_at: one test function, many inputs ──────────────────────────
@pytest.mark.parametrize("text, expected", [
    ("3 days ago", "2026-10-01"),
    ("17 hours ago", "2026-10-04"),
    ("a day ago", "2026-10-03"),
    ("2 weeks ago", "2026-09-20"),
    ("30+ days ago", "2026-09-04"),
    ("1 month ago", "2026-09-04"),
    ("Just posted", "2026-10-04"),
    ("Full-time", None),     # not a date → None, never a guess
    (None, None),
])
def test_parse_posted_at(text, expected):
    assert parse_posted_at(text, TODAY) == expected


# ── to_listing: raw API dict → our schema ────────────────────────────────────
def test_to_listing_maps_fields():
    listing = to_listing(RAW_JOB, TODAY)
    assert listing["company"] == "Acme AI"
    assert listing["source"] == "LinkedIn"                     # "via " stripped
    assert listing["url"] == "https://linkedin.com/jobs/1"     # apply link preferred
    assert listing["posted_date"] == "2026-10-01"
    assert listing["expiry_date"] is None


def test_posted_date_found_in_extensions():
    # No detected_extensions.posted_at, but the date sits in the extensions list
    raw = {**RAW_JOB, "detected_extensions": {}, "extensions": ["Full-time", "5 days ago"]}
    assert extract_posted_date(raw, TODAY) == "2026-09-29"


def test_posted_date_missing_everywhere():
    raw = {**RAW_JOB, "detected_extensions": {}, "extensions": ["Full-time"]}
    assert extract_posted_date(raw, TODAY) is None


def test_to_listing_falls_back_to_share_link():
    raw = {**RAW_JOB, "apply_options": []}
    assert to_listing(raw, TODAY)["url"] == "https://google.com/share/1"


# ── search_google_jobs: mock the HTTP call ───────────────────────────────────
class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status

    def json(self):
        return self._payload


def make_jobs(start, count):
    """Distinct fake jobs, each with its own job_id."""
    return [{**RAW_JOB, "job_id": f"id{i}", "title": f"Job {i}"} for i in range(start, start + count)]


def test_search_follows_pagination(monkeypatch):
    pages = iter([
        FakeResponse({"jobs_results": make_jobs(0, 10),
                      "serpapi_pagination": {"next_page_token": "page2"}}),
        FakeResponse({"jobs_results": make_jobs(10, 10)}),   # no token → last page
    ])
    calls = []

    def fake_get(url, params, timeout):
        calls.append(dict(params))
        return next(pages)

    monkeypatch.setattr(serp_tool.requests, "get", fake_get)

    results = search_google_jobs("ML Engineer", "Toronto", 15, api_key="fake", today=TODAY)

    assert len(results) == 15                          # trimmed to num_results
    assert len(calls) == 2                             # 2 pages = 2 searches
    assert calls[1]["next_page_token"] == "page2"      # token passed to page 2


def test_search_removes_duplicates(monkeypatch):
    # Page 2 repeats job id3 from page 1 → it must appear only once
    pages = iter([
        FakeResponse({"jobs_results": make_jobs(0, 5),
                      "serpapi_pagination": {"next_page_token": "page2"}}),
        FakeResponse({"jobs_results": make_jobs(3, 1) + make_jobs(5, 3)}),
    ])
    monkeypatch.setattr(serp_tool.requests, "get", lambda url, params, timeout: next(pages))

    results = search_google_jobs("ML Engineer", "Toronto", 10, api_key="fake", today=TODAY)

    titles = [r["title"] for r in results]
    assert len(titles) == len(set(titles)) == 8


def test_search_raises_on_api_error(monkeypatch):
    monkeypatch.setattr(serp_tool.requests, "get",
                        lambda url, params, timeout: FakeResponse({"error": "Invalid API key"}))
    with pytest.raises(RuntimeError, match="Invalid API key"):
        search_google_jobs("ML Engineer", "Toronto", 10, api_key="bad", today=TODAY)


def test_search_requires_api_key():
    with pytest.raises(RuntimeError, match="SERPAPI_API_KEY"):
        search_google_jobs("ML Engineer", "Toronto", 10, api_key="")
        