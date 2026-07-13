"""Tests for skills/abx-hermes-skill-evolution/abx_skill_live_corpus_expander.py (TEST candidate d8169391bc2ca748)"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_live_corpus_expander as e

def test_load_live_traces_missing(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    monkeypatch.setattr(e, "OUT", out)
    traces = e.load_live_traces()
    assert traces == []

def test_load_live_traces_valid(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    p = out / "abx_hermes_live_operation_traces.latest.json"
    p.write_text(json.dumps({"traces": [{"operation_id": "op1"}]}))
    monkeypatch.setattr(e, "OUT", out)
    traces = e.load_live_traces()
    assert len(traces) == 1
    assert traces[0]["operation_id"] == "op1"

def test_trace_to_replay_case():
    trace = {"operation_id": "op1", "task_class": "TEST", "skill_id": "foo"}
    case = e.trace_to_replay_case(trace, 0)
    assert case["case_id"] == "live-op1"
    assert case["task_class"] == "TEST"
    assert "provenance_hash" in case
    assert case["source"] == "live_operation_trace"

def test_main_expands(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    p = out / "abx_hermes_live_operation_traces.latest.json"
    p.write_text(json.dumps({"traces": [{"operation_id": "opX", "task_class": "HARDENING"}]}))
    monkeypatch.setattr(e, "OUT", out)
    expanded = e.main()
    assert expanded is not None
    assert len(expanded["cases"]) == 1
    assert (out / "abx_hermes_live_expanded_corpus_v2_4.latest.json").exists()
