"""Tests for state engine _load failure semantics."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.run_state_engine import _load


def test_missing_file_uses_default(tmp_path: Path) -> None:
    """A missing file (FileNotFoundError) returns the provided default."""
    default = {"pipeline_id": "shadow", "execution_hash": "exec:latest"}
    result = _load(str(tmp_path / "nonexistent.json"), default)
    assert result == default


def test_malformed_json_raises(tmp_path: Path) -> None:
    """Malformed/corrupt JSON must not silently default — raises RuntimeError."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json{{{{", encoding="utf-8")
    with pytest.raises(RuntimeError, match="input_malformed"):
        _load(str(bad_file), {"fallback": True})


def test_malformed_json_does_not_return_default(tmp_path: Path) -> None:
    """Malformed JSON must never silently return a default value."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("null\x00\xff", encoding="latin-1")
    with pytest.raises(Exception):
        _load(str(bad_file), {"should_not_appear": True})


def test_valid_json_is_returned(tmp_path: Path) -> None:
    """A valid JSON file is loaded and returned correctly."""
    data = {"replay_hash": "replay:abc123"}
    f = tmp_path / "valid.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    result = _load(str(f), {"fallback": True})
    assert result == data


def test_unreadable_file_raises(tmp_path: Path) -> None:
    """An unreadable file (OSError, not FileNotFoundError) raises RuntimeError."""
    target = str(tmp_path / "locked.json")
    with patch("scripts.run_state_engine.Path") as mock_path_cls:
        mock_instance = mock_path_cls.return_value
        mock_instance.read_text.side_effect = OSError("permission denied")
        # FileNotFoundError is a subclass of OSError; use plain OSError here
        # by making isinstance check work:
        with pytest.raises(RuntimeError, match="input_unreadable"):
            _load(target, {"fallback": True})


def test_print_path_matches_written_path(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """The printed completion path must match the actual written output path."""
    from unittest.mock import patch as _patch

    fake_result = {"snapshot": {}, "transition": {}}

    with (
        _patch("scripts.run_state_engine._load", return_value={}),
        _patch("scripts.run_state_engine.run_state_engine", return_value=fake_result),
        _patch("scripts.run_state_engine.write_canonical_json") as mock_write,
    ):
        from scripts.run_state_engine import main
        main()

    captured = capsys.readouterr()
    assert "out/state/runtime.latest.json" in captured.out
    assert "out/state/latest.json" not in captured.out

    # Verify written path also matches
    call_args = mock_write.call_args
    written_path = str(call_args[0][0])
    assert written_path == "out/state/runtime.latest.json"
