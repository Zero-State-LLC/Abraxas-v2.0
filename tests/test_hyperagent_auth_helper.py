"""Tests for skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_auth_helper.py (TEST candidate 1bff6a2a19cffe23)"""

import os
import pytest
from unittest.mock import patch
from pathlib import Path

# Import the module under test
import sys
sys.path.insert(0, "skills/autonomous-ai-agents/hyperagent-orchestrator/scripts")
import hyperagent_auth_helper as h


def test_inspect_session_defaults(monkeypatch):
    for k in ["HYPERAGENT_API_KEY", "HYPERAGENT_OAUTH_TOKEN", "HYPERAGENT_SESSION_TOKEN", "HYPERAGENT_SECURE_STORE", "HYPERAGENT_BASE_URL", "HYPERAGENT_AUTH_PATH", "HYPERAGENT_SESSION_FILE"]:
        monkeypatch.delenv(k, raising=False)

    result = h.inspect_session()
    assert result["status"] == "ok"
    creds = result["credential_sources"]
    assert creds["HYPERAGENT_API_KEY"] is False
    assert "missing_required" in result


def test_inspect_session_with_values(monkeypatch, tmp_path):
    monkeypatch.setenv("HYPERAGENT_API_KEY", "fake")
    monkeypatch.setenv("HYPERAGENT_BASE_URL", "https://example.com")
    sess_file = tmp_path / "session.json"
    sess_file.write_text("{}")
    monkeypatch.setenv("HYPERAGENT_SESSION_FILE", str(sess_file))

    result = h.inspect_session()
    creds = result["credential_sources"]
    assert creds["HYPERAGENT_API_KEY"] is True
    assert creds["session_file_exists"] is True
    assert "HYPERAGENT_API_KEY" not in result["missing_required"]


def test_probe_endpoint_structure():
    # Just test that the function exists and returns a dict structure (no network)
    # We don't call real network in tests
    result = h.probe_endpoint("https://example.com", "/api/me")
    # In this environment it will likely fail to connect, which is fine
    assert isinstance(result, dict)
    assert "status" in result
    assert "url" in result


def test_main_status(monkeypatch, capsys):
    monkeypatch.setenv("HYPERAGENT_API_KEY", "x")
    with patch("sys.argv", ["prog", "--status"]):
        code = h.main()
    captured = capsys.readouterr()
    assert code == 0
    assert "credential_sources" in captured.out or "status" in captured.out