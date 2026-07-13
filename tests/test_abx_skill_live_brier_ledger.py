"""Tests for skills/abx-hermes-skill-evolution/abx_skill_live_brier_ledger.py (TEST candidate d6d15258a697a351)"""

import sys
import json

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_live_brier_ledger as b

def test_load_json_missing(tmp_path):
    p = tmp_path / "missing.json"
    assert b.load_json(p) == {}

def test_load_json_valid(tmp_path):
    p = tmp_path / "valid.json"
    p.write_text(json.dumps({"traces": [1,2]}))
    assert b.load_json(p) == {"traces": [1,2]}

def test_main_emits_ledger(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    traces = out / "abx_hermes_live_operation_traces.latest.json"
    traces.write_text(json.dumps({"traces": [{"id":1}]}))
    expander = out / "abx_hermes_live_expanded_corpus_v2_4.latest.json"
    expander.write_text(json.dumps({"cases": [{"source": "arxiv_literature_corpus"}]}))
    readiness = out / "abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json"
    readiness.write_text(json.dumps({"verification_evidence": {"agreement_rate": 0.8}}))
    monkeypatch.setattr(b, "OUT", out)
    ledger = b.main()
    assert "brier_delta" in ledger
    assert ledger["status"] == "SHADOW_ONLY"
    assert (out / "abx_hermes_live_brier_ledger_v2_4.latest.json").exists()
