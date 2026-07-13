"""Tests for core/intelligence/brier_scorer.py (HARDENING candidate a1161da52e9125d1)"""

from core.intelligence.brier_scorer import BrierScorer

def test_brier_scorer_basic():
    scorer = BrierScorer()
    b = scorer.update(0.8, 1.0)
    assert b == (0.8 - 1.0) ** 2
    summary = scorer.get_summary()
    assert summary["n_scores"] == 1
    assert "mean_brier" in summary

def test_brier_scorer_multiple():
    scorer = BrierScorer()
    scorer.update(0.5, 1.0)
    scorer.update(0.2, 0.0)
    summary = scorer.get_summary()
    assert summary["n_scores"] == 2
    assert summary["min_brier"] <= summary["max_brier"]

def test_empty_summary():
    scorer = BrierScorer()
    s = scorer.get_summary()
    assert s["status"] == "no_scores_yet"
