"""Tests for core/abraxas_engineering_priority_model.py (HARDENING candidate d4678411ee599ddf)"""

from core.abraxas_engineering_priority_model import compute_scores, rank_candidates

def test_compute_scores_basic():
    cand = {
        "candidate_id": "d4678411ee599ddf",
        "title": "Add tests for core/abraxas_engineering_priority_model.py",
        "estimated_impact": 0.8,
        "estimated_effort": 0.15,
        "estimated_risk": 0.05,
        "confidence": 0.9,
        "affected_paths": ["core/abraxas_engineering_priority_model.py"],
        "candidate_class": "HARDENING"
    }
    pkt = {"affected_paths": ["core/abraxas_engineering_priority_model.py"]}
    scores = compute_scores(cand, pkt)
    assert "final_priority_score" in scores
    assert 0.0 <= scores["final_priority_score"] <= 1.0
    assert scores["governance_boost"] >= 0.0

def test_rank_candidates():
    cands = [
        {"candidate_id": "a", "estimated_impact": 0.9, "estimated_effort": 0.1, "estimated_risk": 0.0, "confidence": 0.95, "affected_paths": ["core/foo.py"], "candidate_class": "HARDENING"},
        {"candidate_id": "b", "estimated_impact": 0.5, "estimated_effort": 0.3, "estimated_risk": 0.2, "confidence": 0.6, "affected_paths": ["scripts/bar.py"], "candidate_class": "TEST"}
    ]
    ranked = rank_candidates(cands)
    assert len(ranked) == 2
    assert ranked[0]["candidate_id"] == "a"
    assert "final_priority_score" in ranked[0]

def test_governance_boost_applied():
    cand = {"candidate_id": "c", "estimated_impact": 0.7, "estimated_effort": 0.2, "estimated_risk": 0.1, "confidence": 0.8, "affected_paths": ["core/baz.py"], "candidate_class": "GOVERNANCE"}
    pkt = {"affected_paths": ["core/baz.py"]}
    scores = compute_scores(cand, pkt)
    assert scores["governance_boost"] > 0.0
