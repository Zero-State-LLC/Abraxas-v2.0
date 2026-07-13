"""Tests for skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_export_import_bridge.py (TEST candidate 4540648b5b8727bf)"""

import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, "skills/autonomous-ai-agents/hyperagent-orchestrator/scripts")
import hyperagent_export_import_bridge as b

def test_abraxas_to_hyperagent_basic():
    payload = {
        "name": "test-role",
        "version": "0.2.0",
        "summary": "Test mission",
        "tools": ["web_search", "code"],
        "budget": {"max_cost_usd": 2.0, "max_steps": 10},
        "observed": {"fact": 1},
        "provenance": {"src": "abx"},
        "canonical_hash": "abc123"
    }
    mapped = b.abraxas_to_hyperagent(payload)
    assert mapped["name"] == "test-role"
    assert mapped["mission"] == "Test mission"
    assert mapped["tools"] == ["web_search", "code"]
    assert mapped["observed"] == {"fact": 1}
    assert mapped["canonical_hash"] == "abc123"

def test_hyperagent_to_abraxas_basic():
    payload = {
        "name": "ha-role",
        "version": "1.0",
        "tools": ["search"],
        "canonical_hash": "def456"
    }
    mapped = b.hyperagent_to_abraxas(payload)
    assert mapped["observed"] == payload
    assert mapped["inferred"]["role"] == "ha-role"
    assert mapped["inferred"]["tool_count"] == 1
    assert mapped["speculative"]["next_step"] == "Review role policy and deploy only after validation"

def test_stable_dump_roundtrip():
    obj = {"b": 2, "a": 1}
    dumped = b.stable_dump(obj)
    loaded = json.loads(dumped)
    assert loaded == {"a": 1, "b": 2}  # sorted

def test_cli_export(tmp_path):
    inp = tmp_path / "in.json"
    outp = tmp_path / "out.json"
    inp.write_text(json.dumps({"name": "cli-role", "summary": "cli mission"}))
    # simulate main via direct call
    payload = b.load_json(str(inp))
    mapped = b.abraxas_to_hyperagent(payload)
    text = b.stable_dump(mapped)
    outp.write_text(text + "\n")
    assert "cli-role" in outp.read_text()
    assert "cli mission" in outp.read_text()