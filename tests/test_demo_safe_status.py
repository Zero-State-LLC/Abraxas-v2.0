from __future__ import annotations

import importlib
import io
from pathlib import Path
from unittest import mock


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "demo_safe_status",
        Path("scripts/demo_safe_status.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _capture_status() -> str:
    mod = _load_module()
    buf = io.StringIO()
    with mock.patch("sys.stdout", buf):
        mod.print_status()
    return buf.getvalue()


def test_print_status_runs_without_error() -> None:
    _capture_status()


def test_output_contains_header() -> None:
    out = _capture_status()
    assert "ABRAXAS v2.0" in out


def test_output_contains_read_only_notice() -> None:
    out = _capture_status()
    assert "READ-ONLY" in out


def test_output_contains_end_marker() -> None:
    out = _capture_status()
    assert "END STATUS" in out


def test_output_contains_doctrine_validator_section() -> None:
    out = _capture_status()
    assert "DOCTRINE VALIDATOR" in out


def test_output_contains_transport_chain_section() -> None:
    out = _capture_status()
    assert "TRANSPORT CHAIN" in out


def test_output_contains_implementation_gate_section() -> None:
    out = _capture_status()
    assert "IMPLEMENTATION GATE" in out


def test_output_contains_authority_posture_section() -> None:
    out = _capture_status()
    assert "AUTHORITY POSTURE" in out


def test_no_files_written(tmp_path) -> None:
    before = set(Path("out").rglob("*.json"))
    _capture_status()
    after = set(Path("out").rglob("*.json"))
    assert before == after, "demo_safe_status wrote unexpected files to out/"


def test_does_not_touch_research_canary() -> None:
    canary_paths = list(Path("out").glob("research_canary*"))
    if not canary_paths:
        canary_paths = list(Path("out").glob("**/research_canary*"))
    before_mtimes = {p: p.stat().st_mtime for p in canary_paths if p.exists()}
    _capture_status()
    for p, mtime in before_mtimes.items():
        assert p.stat().st_mtime == mtime, f"research_canary file modified: {p}"


def test_main_exits_zero() -> None:
    mod = _load_module()
    buf = io.StringIO()
    with mock.patch("sys.stdout", buf):
        with mock.patch("sys.exit") as mock_exit:
            mod.main()
    mock_exit.assert_called_once_with(0)


def test_read_json_missing_returns_none() -> None:
    mod = _load_module()
    result = mod._read_json(Path("/nonexistent/path/file.json"))
    assert result is None


def test_read_json_existing_artifact() -> None:
    mod = _load_module()
    p = Path(
        "out/metric_operator/"
        "transport_fixture_corpus_creation_plan_001.latest.json"
    )
    if not p.exists():
        import pytest
        pytest.skip("artifact not present")
    result = mod._read_json(p)
    assert isinstance(result, dict)
    assert "plan_status" in result


def test_short_hash_truncates() -> None:
    mod = _load_module()
    h = "a" * 64
    result = mod._short_hash(h, length=16)
    assert result.startswith("a" * 16)
    assert result.endswith("...")
    assert len(result) == 19


def test_short_hash_empty_returns_none_label() -> None:
    mod = _load_module()
    result = mod._short_hash("", length=16)
    assert result == "(none)"


def test_no_subprocess_calls() -> None:
    mod = _load_module()
    buf = io.StringIO()
    with mock.patch("subprocess.run") as mock_run:
        with mock.patch("sys.stdout", buf):
            mod.print_status()
    mock_run.assert_not_called()


def test_no_open_for_write() -> None:
    mod = _load_module()
    original_open = open
    opened_for_write = []

    def tracking_open(file, mode="r", *args, **kwargs):
        if "w" in str(mode) or "a" in str(mode):
            opened_for_write.append((file, mode))
        return original_open(file, mode, *args, **kwargs)

    buf = io.StringIO()
    with mock.patch("builtins.open", side_effect=tracking_open):
        with mock.patch("sys.stdout", buf):
            mod.print_status()

    assert opened_for_write == [], (
        f"demo_safe_status opened files for writing: {opened_for_write}"
    )
