"""Tests for skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_deploy_role.py (TEST candidate ecc82064e32b995c)"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "skills/autonomous-ai-agents/hyperagent-orchestrator/scripts")
import hyperagent_deploy_role as h

def test_load_json(tmp_path):
    p = tmp_path / "tmpl.json"
    p.write_text(json.dumps({"role": "test"}))
    data = h.load_json(str(p))
    assert data["role"] == "test"

def test_build_payload_basic():
    template = {"role": "base"}
    payload = h.build_payload(template, "myrole", "mission text", dry_run=True)
    assert payload["name"] == "myrole"
    assert payload["mission"] == "mission text"
    assert payload["deployment_mode"] == "dry_run"
    assert "version" in payload

def test_build_payload_dry_run_false():
    template = {}
    payload = h.build_payload(template, None, None, dry_run=False)
    assert payload["deployment_mode"] == "deploy"

def test_main_dry_run(tmp_path, monkeypatch, capsys):
    tmpl = tmp_path / "t.json"
    tmpl.write_text(json.dumps({"role": "x"}))
    with patch("sys.argv", ["prog", "--template", str(tmpl), "--dry-run"]):
        h.main()
    out = capsys.readouterr().out
    assert "dry_run" in out or "deployment_mode" in out
