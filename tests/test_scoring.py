"""Unit tests for the deterministic Python logic in the Analyzer."""
from datetime import date
from agent.nodes.analyzer import weighted_total, days_since, urgency_label, is_expired

TODAY = date(2026, 10, 2)


def test_weighted_total():
    # 85*.40 + 70*.25 + 90*.20 + 100*.15 = 84.5 -> 84 (banker's rounding)
    assert weighted_total({"skills": 85, "experience": 70, "domain": 90, "location": 100}) == 84


def test_days_since():
    assert days_since("2026-09-29", TODAY) == 3
    assert days_since(None, TODAY) is None


def test_urgency_label():
    assert urgency_label(1) == "fresh"
    assert urgency_label(7) == "recent"
    assert urgency_label(30) == "old"
    assert urgency_label(None) == "unknown"


def test_is_expired():
    assert is_expired("2026-09-30", TODAY) is True
    assert is_expired("2026-10-30", TODAY) is False
    assert is_expired(None, TODAY) is False
