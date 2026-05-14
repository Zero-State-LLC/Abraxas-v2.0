"""Tests for PATCH-P1-API-STATE-HARDENING-001: state engine hardening."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

import pytest

import scripts.run_state_engine as rse


# ---------------------------------------------------------------------------
# Phase 5 – _load_optional failure semantics
# ---------------------------------------------------------------------------


def test_load_optional_returns_default_for_missing_file(tmp_path):
    """Missing file returns the supplied default (optional input fallback)."""
    default = {"k": "v"}
    result = rse._load_optional(str(tmp_path / "nonexistent.json"), default)
    assert result == default


def test_load_optional_raises_on_malformed_json(tmp_path):
    """Malformed JSON must not silently fall back to default."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{unclosed", encoding="utf-8")
    with pytest.raises(RuntimeError, match="input_malformed"):
        rse._load_optional(str(bad_file), {"k": "v"})


def test_load_optional_raises_on_corrupt_json(tmp_path):
    """Partial/truncated JSON must not silently fall back to default."""
    bad_file = tmp_path / "corrupt.json"
    bad_file.write_text('{"key": ', encoding="utf-8")
    with pytest.raises(RuntimeError, match="input_malformed"):
        rse._load_optional(str(bad_file), {"k": "v"})


def test_load_optional_loads_valid_json(tmp_path):
    """Valid JSON file is loaded and returned correctly."""
    good_file = tmp_path / "good.json"
    payload = {"pipeline_id": "test", "execution_hash": "abc123"}
    good_file.write_text(json.dumps(payload), encoding="utf-8")
    result = rse._load_optional(str(good_file), {})
    assert result == payload


def test_load_optional_raises_on_unreadable_file(tmp_path):
    """File that exists but cannot be read raises RuntimeError."""
    locked = tmp_path / "locked.json"
    locked.write_text('{"k": "v"}', encoding="utf-8")
    locked.chmod(0o000)
    try:
        with pytest.raises(RuntimeError, match="input_unreadable"):
            rse._load_optional(str(locked), {})
    finally:
        locked.chmod(0o644)


# ---------------------------------------------------------------------------
# Phase 5 – Print path fix
# ---------------------------------------------------------------------------


def test_main_prints_correct_output_path(tmp_path):
    """main() must print the actual output path, not a stale alias."""
    captured = StringIO()
    with (
        patch("scripts.run_state_engine.run_state_engine", return_value={}),
        patch("scripts.run_state_engine.write_canonical_json"),
        patch("sys.stdout", captured),
    ):
        rse.main()
    output = captured.getvalue()
    assert "out/state/runtime.latest.json" in output
    # The old wrong path must not appear
    assert "out/state/latest.json" not in output
