"""Tests for skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_builder.py (GOVERNANCE candidate 3d9b03f89de9428b)"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_formal_operator_decision_builder as d

def test_load_json_safe_missing(tmp_path):
    missing = tmp_path / "missing.json"
    assert d.load_json_safe(missing) is None

def test_load_json_safe_valid(tmp_path):
    f = tmp_path / "v.json"
    f.write_text(json.dumps({"formal_review_id": "r1"}))
    assert d.load_json_safe(f)["formal_review_id"] == "r1"

def test_save_json(tmp_path):
    f = tmp_path / "out" / "test.json"
    data = {"a": 1}
    d.save_json(f, data)
    assert f.exists()
    assert json.loads(f.read_text()) == data

def test_allowed_decisions():
    assert "APPROVE_EXTENDED_OBSERVATION" in d.ALLOWED_DECISIONS
    assert "REJECT_CANDIDATE" in d.ALLOWED_DECISIONS

def test_load_review_packet_fallback(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    pkt = {"formal_review_id": "fb1"}
    f = out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
    f.write_text(json.dumps(pkt))
    monkeypatch.setattr(d, "OUT", out)
    loaded = d.load_review_packet()
    assert loaded is not None
    assert loaded.get("formal_review_id") == "fb1"
