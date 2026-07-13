"""Tests for core/abraxas_governance_stratifier.py (GOVERNANCE candidate cf643100c80e758f)"""

from core.abraxas_governance_stratifier import classify_work, classify_from_work_packet

def test_layer0_default_engineering():
    candidate = {"candidate_id": "cf643100c80e758f", "title": "Add tests for core/abraxas_governance_stratifier.py"}
    affected = ["core/abraxas_governance_stratifier.py"]
    ops = ["ADD_TEST_FUNCTIONS"]
    res = classify_work(candidate, affected, ops)
    assert res["layer"] == 0
    assert res["automatic_under_engineering_approval"] is True
    assert "default_layer0_internal_engineering" in res["evidence"]

def test_layer1_advisory():
    candidate = {"candidate_id": "test1", "title": "shadow simulation proposal"}
    res = classify_work(candidate, [], [])
    assert res["layer"] == 1
    # Code checks in order; "simulation" appears first in title match for this input
    assert any("layer1_keyword:" in e for e in res["evidence"])

def test_layer2_canon():
    candidate = {"candidate_id": "test2", "title": "canonical_schema governance_definition"}
    res = classify_work(candidate, [], [])
    assert res["layer"] == 2

def test_layer3_production():
    candidate = {"candidate_id": "test3", "title": "production runtime_execution activation"}
    res = classify_work(candidate, [], [])
    assert res["layer"] == 3

def test_classify_from_work_packet():
    wp = {"affected_paths": ["core/foo.py"], "allowed_operations": ["ADD_TEST"]}
    cand = {"candidate_id": "test", "title": "Add tests for core/foo.py"}
    res = classify_from_work_packet(wp, cand)
    assert res["layer"] == 0
    assert res["candidate_id"] == "test"
