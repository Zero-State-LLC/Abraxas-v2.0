"""Tests for skills/abx-hermes-skill-evolution/abx_skill_formal_operator_review_packet.py (TEST candidate 737a69826fdbbf40)"""

import sys
import json
sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_formal_operator_review_packet as r

def test_find_signal_source_unresolved(monkeypatch, tmp_path):
    monkeypatch.setattr(r, "OUT", tmp_path)
    res = r.find_signal_source("nonexistent-signal")
    assert res["classification"] == "INFERRED"
    assert res["source_artifact"] == "SOURCE_UNRESOLVED"
    assert res["authority_conferred"] is False

def test_find_signal_source_observed(monkeypatch, tmp_path):
    audit = tmp_path
    (audit / "some_signal_v1.latest.json").write_text(json.dumps({"data": "test"}))
    monkeypatch.setattr(r, "OUT", audit)
    res = r.find_signal_source("some_signal")
    assert res["classification"] == "OBSERVED"
    assert "some_signal_v1.latest.json" in res["source_artifact"]
    assert res["authority_conferred"] is False

def test_main_not_computable_no_review(monkeypatch, tmp_path):
    monkeypatch.setattr(r, "OUT", tmp_path)
    res = r.main()
    assert res.get("packet_status") == "NOT_COMPUTABLE"

def test_packet_structure_with_mocks(monkeypatch, tmp_path):
    audit = tmp_path
    review = {"review_id": "formal-op-review-v2.5-13", "evidence_bundle": {"cross_surface_signals": [], "live_traces": 5}}
    (audit / "abx_hermes_formal_operator_review_v2_5.latest.json").write_text(json.dumps(review))
    monkeypatch.setattr(r, "OUT", audit)
    # minimal run
    formal = r.load_artifact("abx_hermes_formal_operator_review_v2_5.latest.json")
    assert formal is not None
    assert formal["review_id"] == "formal-op-review-v2.5-13"