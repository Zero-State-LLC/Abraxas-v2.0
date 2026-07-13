"""Tests for skills/abx-hermes-skill-evolution/abx_skill_operator_decision_history_ledger.py (GOVERNANCE candidate 4a8172b37057efd9)"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_operator_decision_history_ledger as l

def test_load_json_safe_missing(tmp_path):
    missing = tmp_path / "missing.json"
    assert l.load_json_safe(missing) is None

def test_load_json_safe_valid(tmp_path):
    f = tmp_path / "v.json"
    f.write_text(json.dumps({"formal_review_id": "r1"}))
    assert l.load_json_safe(f)["formal_review_id"] == "r1"

def test_compute_event_hash():
    event = {"event_sequence": 1, "event_class": "TEST", "candidate_id": "c1"}
    h = l.compute_event_hash(event)
    assert len(h) == 16
    assert isinstance(h, str)

def test_append_event():
    history = []
    event = l.append_event(history, "TEST", "rev1", "cand1", "src.json", "hash1")
    assert len(history) == 1
    assert event["event_sequence"] == 1
    assert "event_hash" in event
    assert event["previous_event_hash"] == "GENESIS"

def test_main_runs(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    op = tmp_path / "out" / "operator_input"
    out.mkdir(parents=True)
    op.mkdir(parents=True)
    # minimal artifacts
    (out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").write_text(json.dumps({"formal_review_id": "r1", "candidate_id": "c1", "deterministic_hash": "h1"}))
    (op / "abx_hermes_formal_operator_decision_v2_7.input.json").write_text(json.dumps({"decision_value": "APPROVE"}))
    monkeypatch.setattr(l, "OUT", out)
    monkeypatch.setattr(l, "OPERATOR_DIR", op)
    # should not crash
    l.main()
    assert True
