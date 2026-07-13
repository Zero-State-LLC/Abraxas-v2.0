"""Tests for skills/abx-hermes-skill-evolution/abx_skill_operator_decision_reconciliation.py (GOVERNANCE candidate d39d1e466fdfedee)"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_operator_decision_reconciliation as r

def test_load_json_safe_missing(tmp_path):
    missing = tmp_path / "missing.json"
    assert r.load_json_safe(missing) is None

def test_compute_det_hash():
    h = r.compute_det_hash({"a": 1, "b": 2})
    assert len(h) == 16

def test_main_current_valid(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    op = tmp_path / "out" / "operator_input"
    out.mkdir(parents=True)
    op.mkdir(parents=True)
    review = {"formal_review_id": "r1", "deterministic_hash": "h1"}
    decision = {
        "formal_review_id": "r1",
        "review_packet_hash": "h1",
        "decision_value": "APPROVE_EXTENDED_OBSERVATION",
        "acknowledgements": {k: True for k in r.REQUIRED_ACKS},
        "authority_boundary": {k: False for k in r.REQUIRED_AUTH},
        "operator": {"operator_id": "op1", "operator_display_name": "Test"}
    }
    (out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").write_text(json.dumps(review))
    (op / "abx_hermes_formal_operator_decision_v2_7.input.json").write_text(json.dumps(decision))
    monkeypatch.setattr(r, "OUT", out)
    monkeypatch.setattr(r, "OPERATOR_DIR", op)
    monkeypatch.setattr(r, "REVIEW_PATH", out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json")
    monkeypatch.setattr(r, "DECISION_PATH", op / "abx_hermes_formal_operator_decision_v2_7.input.json")
    monkeypatch.setattr(r, "VALIDATION_PATH", out / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json")
    monkeypatch.setattr(r, "LEDGER_PATH", out / "abx_hermes_formal_operator_decision_ledger_v2_9.latest.json")
    res = r.main()
    assert res is not None
    # Expect classification or emission without crash

def test_main_no_decision(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    op = tmp_path / "out" / "operator_input"
    out.mkdir(parents=True)
    op.mkdir(parents=True)
    (out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").write_text(json.dumps({}))
    monkeypatch.setattr(r, "OUT", out)
    monkeypatch.setattr(r, "OPERATOR_DIR", op)
    monkeypatch.setattr(r, "REVIEW_PATH", out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json")
    monkeypatch.setattr(r, "DECISION_PATH", op / "abx_hermes_formal_operator_decision_v2_7.input.json")
    monkeypatch.setattr(r, "VALIDATION_PATH", out / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json")
    monkeypatch.setattr(r, "LEDGER_PATH", out / "abx_hermes_formal_operator_decision_ledger_v2_9.latest.json")
    res = r.main()
    assert res is not None
