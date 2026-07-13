"""Tests for core/abraxas_governance_decision_contract.py (GOVERNANCE candidate)"""

from core.abraxas_governance_decision_contract import (
    classify_from_work_packet,
    compute_decision_hash,
)


def test_classify_from_work_packet_basic():
    work_packet = {
        "candidate_id": "test-gov-001",
        "title": "Add tests for governance decision contract",
        "candidate_class": "GOVERNANCE",
        "governance_layer": 0,
        "affected_paths": ["core/abraxas_governance_decision_contract.py"],
    }
    candidate = {"candidate_id": "test-gov-001", "candidate_class": "GOVERNANCE"}
    result = classify_from_work_packet(work_packet, candidate)
    assert isinstance(result, dict)
    assert "layer" in result
    assert result["layer"] == 0
    assert "automatic_under_engineering_approval" in result


def test_compute_decision_hash_stable():
    decision = {"key": "value", "layer": 0}
    h1 = compute_decision_hash(decision)
    h2 = compute_decision_hash(decision)
    assert h1 == h2
    assert isinstance(h1, str)
    assert len(h1) > 0


def test_compute_decision_hash_changes_on_input():
    d1 = {"a": 1}
    d2 = {"a": 2}
    h1 = compute_decision_hash(d1)
    h2 = compute_decision_hash(d2)
    assert h1 != h2
