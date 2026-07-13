"""Tests for skills/abx-hermes-skill-evolution/abx_skill_v25_governance_enhancer.py (GOVERNANCE candidate abc6759bd44d427e)"""

import sys
import json

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_v25_governance_enhancer as g

def test_main_emits_review(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    traces = {"count": 5}
    (out / "abx_hermes_live_operation_traces.latest.json").write_text(json.dumps(traces))
    monkeypatch.setattr(g, "OUT", out)
    res = g.main()
    assert res is not None
    assert "review_id" in res
    assert res["recommendation"] == "CONTINUE_SHADOW_COLLECTION"
    formal_path = out / "abx_hermes_formal_operator_review_v2_5.latest.json"
    assert formal_path.exists()

def test_main_handles_missing(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    monkeypatch.setattr(g, "OUT", out)
    res = g.main()
    assert res is not None
    assert "review_id" in res
