"""Tests for core/intelligence/brier_visualization.py (HARDENING candidate 6d31710875addd15)"""

from core.intelligence.brier_visualization import (
    format_brier_summary,
    format_decomposition,
)

def test_format_brier_summary_no_scores():
    s = format_brier_summary({"status": "no_scores_yet"})
    assert "No Brier scores" in s

def test_format_brier_summary_basic():
    s = format_brier_summary({
        "n_scores": 10,
        "mean_brier": 0.1234,
        "latest_brier": 0.11,
        "min_brier": 0.05,
        "max_brier": 0.3
    })
    assert "Mean Brier" in s
    assert "0.1234" in s

def test_format_decomposition():
    d = {"reliability": 0.1, "resolution": 0.2, "uncertainty": 0.3, "brier_score": 0.6}
    out = format_decomposition(d)
    assert "Reliability" in out
