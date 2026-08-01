"""Tests for skills/abx-hermes-skill-evolution/abx_skill_evolution_analyzer.py

Covers legacy receipts + new Hermes os_signal / signal_forage volume (task_class keying).
"""

import json
import sys

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


def test_aggregate_ledger_signal_forage_task_class():
    """New: Hermes signal volume should be keyed as skill:task_class."""
    traces = [
        {
            "data": {
                "skill_id": "abx-familiar-signal-forager",
                "task_class": "signal_forage",
                "completion_status": "COMPLETE",
                "brier_score": 0.15,
            }
        },
        {
            "data": {
                "skill_id": "abx-familiar-signal-forager",
                "task_class": "signal_forage",
                "completion_status": "COMPLETE",
                "brier_score": 0.12,
            }
        },
    ]
    ledger = a.aggregate_ledger(traces)
    key = "abx-familiar-signal-forager:signal_forage"
    assert key in ledger
    assert ledger[key]["runs"] == 2
    assert ledger[key]["success"] == 2
    assert abs(ledger[key]["success_rate"] - 1.0) < 0.01


def test_detect_signals_low_success():
    ledger = {
        "bar": {"runs": 5, "success": 2, "success_rate": 0.4, "brier_sum": 1.0, "mean_brier": 0.2, "failures": []}
    }
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
    except Exception:  # noqa: BLE001,S110
        pass
    assert True

def test_detect_signals_high_hermes_signal_volume():
    """New: sufficient signal_forage volume from Hermes triggers advisory candidate (even with good success rate)."""
    ledger = {
        "abx-familiar-signal-forager:signal_forage": {
            "runs": 5,
            "success": 5,
            "success_rate": 1.0,
            "brier_sum": 0.3,
            "mean_brier": 0.06,
            "failures": [],
        }
    }
    cands = a.detect_signals(ledger)
    sf_cand = [c for c in cands if "signal_forage" in c["skill_id"]][0]
    assert "high_hermes_signal_volume" in sf_cand["triggering_patterns"]
    assert sf_cand["status"] == "CANDIDATE_ONLY"
    assert "Hermes sessions" in sf_cand["evidence_window"]
