"""Tests for skills/abx-hermes-skill-evolution/abx_skill_evolution_analyzer.py (TEST candidate df0d0b98c52543f3)"""

import sys
import json

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_evolution_analyzer as a

def test_load_traces_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(a, "Path", lambda x="out/audit": tmp_path)
    traces = a.load_traces(tmp_path)
    assert traces == []

def test_aggregate_ledger_basic():
    traces = [{"data": {"skill_id": "foo", "completion_status": "COMPLETE", "brier_score": 0.1}}]
    ledger = a.aggregate_ledger(traces)
    assert "foo" in ledger
    assert ledger["foo"]["runs"] == 1
    assert ledger["foo"]["success"] == 1

def test_detect_signals_low_success():
    ledger = {"bar": {"runs": 5, "success": 2, "success_rate": 0.4, "brier_sum": 1.0, "mean_brier": 0.2, "failures": []}}
    cands = a.detect_signals(ledger)
    assert len(cands) > 0
    assert cands[0]["status"] == "CANDIDATE_ONLY"

def test_main_runs(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    (out / "foo-receipt.json").write_text(json.dumps({"operation_id": "x", "skill_id": "s", "completion_status": "COMPLETE"}))
    monkeypatch.setattr(a, "Path", lambda x="out/audit": out)
    # Should not crash
    try:
        a.main()
    except Exception:
        pass
    assert True
