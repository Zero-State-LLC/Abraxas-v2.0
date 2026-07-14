from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = (
    ROOT
    / "skills"
    / "abx-hermes-skill-evolution"
    / "abx_skill_formal_operator_decision_builder.py"
)


@pytest.fixture
def builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wp8_hermes_builder", BUILDER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _expected(value: dict[str, Any]) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode()


def _residue(target: Path) -> list[Path]:
    return list(target.parent.glob(f".{target.name}.*.tmp"))


def test_save_json_preserves_exact_hermes_profile_and_default_encoding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder: ModuleType,
) -> None:
    payload = {"z": "lambda: \u03bb", "a": {"value": 1.25, "items": [True, None]}}
    target = tmp_path / "nested" / "hermes.json"
    opened: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    original_open = Path.open

    def recording_open(self: Path, *args: Any, **kwargs: Any) -> Any:
        if self.name.startswith(f".{target.name}."):
            opened.append((args, kwargs))
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", recording_open)
    result = builder.save_json(target, payload)

    expected = _expected(payload)
    assert result is None
    assert target.read_bytes() == expected
    assert hashlib.sha256(expected).hexdigest() == (
        "f5ebb4fc37ea79746c8ad382049f43909c37650245d3f5df994a9b2516eb69dc"
    )
    assert b"\\u03bb" in expected
    assert not expected.endswith(b"\n")
    assert opened == [(('x',), {})]


def test_save_json_creates_parent_before_serialization_failure(
    tmp_path: Path, builder: ModuleType
) -> None:
    class Unsupported:
        pass

    target = tmp_path / "created" / "hermes.json"

    with pytest.raises(TypeError):
        builder.save_json(target, {"unsupported": Unsupported()})

    assert target.parent.is_dir()
    assert not target.exists()
    assert _residue(target) == []


def test_save_json_handles_large_payload_and_rewrites_unchanged_content(
    tmp_path: Path, builder: ModuleType
) -> None:
    payload = {"records": [{"index": index, "body": "x" * 100} for index in range(5000)]}
    target = tmp_path / "large.json"
    builder.save_json(target, payload)
    target.chmod(0o640)
    before = target.stat()
    os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns - 2_000_000_000))
    before = target.stat()

    builder.save_json(target, payload)

    after = target.stat()
    assert target.read_bytes() == _expected(payload)
    assert stat.S_IMODE(after.st_mode) == 0o640
    assert after.st_mtime_ns > before.st_mtime_ns
    assert after.st_ino != before.st_ino
    assert _residue(target) == []


def test_save_json_first_write_permissions_match_path_write_text(
    tmp_path: Path, builder: ModuleType
) -> None:
    reference = tmp_path / "reference.json"
    target = tmp_path / "hermes.json"
    reference.write_text("{}")

    builder.save_json(target, {})

    assert stat.S_IMODE(target.stat().st_mode) == stat.S_IMODE(reference.stat().st_mode)


def test_save_json_rejects_read_only_destination(tmp_path: Path, builder: ModuleType) -> None:
    target = tmp_path / "locked.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)
    target.chmod(0o444)

    try:
        with pytest.raises(PermissionError):
            builder.save_json(target, {"replacement": "value"})
    finally:
        target.chmod(0o644)

    assert target.read_bytes() == prior
    assert _residue(target) == []


def test_save_json_accepts_write_only_destination(tmp_path: Path, builder: ModuleType) -> None:
    target = tmp_path / "write-only.json"
    target.write_text("prior")
    target.chmod(0o200)

    try:
        builder.save_json(target, {"replacement": "value"})
        assert stat.S_IMODE(target.stat().st_mode) == 0o200
        target.chmod(0o600)
        assert target.read_bytes() == _expected({"replacement": "value"})
    finally:
        target.chmod(0o600)

    assert _residue(target) == []


class _FailingHandle:
    def __init__(self, handle: Any, failure_point: str) -> None:
        self.handle = handle
        self.failure_point = failure_point

    def write(self, data: str) -> int:
        if self.failure_point == "write":
            self.handle.write(data[:5])
            self.handle.flush()
            raise OSError("controlled Hermes write failure")
        return self.handle.write(data)

    def flush(self) -> None:
        if self.failure_point == "flush":
            raise OSError("controlled Hermes flush failure")
        self.handle.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.handle, name)


@pytest.mark.parametrize("failure_point", ["write", "flush"])
def test_save_json_stream_failure_preserves_prior_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder: ModuleType,
    failure_point: str,
) -> None:
    target = tmp_path / "preserved.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)
    original_open = Path.open

    def failing_open(self: Path, *args: Any, **kwargs: Any) -> Any:
        handle = original_open(self, *args, **kwargs)
        if args and args[0] == "x":
            return _FailingHandle(handle, failure_point)
        return handle

    monkeypatch.setattr(Path, "open", failing_open)
    with pytest.raises(OSError, match=f"controlled Hermes {failure_point} failure"):
        builder.save_json(target, {"replacement": "value"})

    assert target.read_bytes() == prior
    assert _residue(target) == []


@pytest.mark.parametrize("failure_point", ["fsync", "replace"])
def test_save_json_publication_failure_preserves_prior_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder: ModuleType,
    failure_point: str,
) -> None:
    target = tmp_path / "preserved.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)

    def fail(*_args: Any, **_kwargs: Any) -> None:
        raise OSError(f"controlled Hermes {failure_point} failure")

    monkeypatch.setattr(os, failure_point, fail)
    with pytest.raises(OSError, match=f"controlled Hermes {failure_point} failure"):
        builder.save_json(target, {"replacement": "value"})

    assert target.read_bytes() == prior
    assert _residue(target) == []


def test_save_json_cleanup_failure_preserves_primary_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder: ModuleType,
) -> None:
    target = tmp_path / "cleanup.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)
    original_unlink = Path.unlink

    def fail_fsync(*_args: Any, **_kwargs: Any) -> None:
        raise OSError("controlled Hermes fsync failure")

    def fail_cleanup(self: Path, *args: Any, **kwargs: Any) -> None:
        raise OSError("controlled Hermes cleanup failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)
    monkeypatch.setattr(Path, "unlink", fail_cleanup)
    with pytest.raises(OSError, match="controlled Hermes fsync failure") as exc_info:
        builder.save_json(target, {"replacement": "value"})

    assert target.read_bytes() == prior
    assert any("temporary file removal failed" in note for note in exc_info.value.__notes__)
    residue = _residue(target)
    assert len(residue) == 1
    original_unlink(residue[0])


def test_failed_working_state_publication_preserves_resumable_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder: ModuleType,
) -> None:
    target = tmp_path / ".working" / "decision.working.json"
    prior = {
        "builder_status": "COLLECTING_OPERATOR_INPUT",
        "formal_review_id": "review-1",
        "normalized_fields": {"operator.operator_id": "op-1"},
    }
    monkeypatch.setattr(builder, "WORKING_PATH", target)
    builder.save_json(target, prior)

    def fail_replace(*_args: Any, **_kwargs: Any) -> None:
        raise OSError("controlled Hermes working-state replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="working-state replace failure"):
        builder.save_working({**prior, "builder_status": "OPERATOR_INPUT_CANCELLED"})

    assert json.loads(target.read_text()) == prior
    assert builder.load_working() == prior
    assert _residue(target) == []


def test_concurrent_writers_never_expose_malformed_json(
    tmp_path: Path, builder: ModuleType
) -> None:
    target = tmp_path / "concurrent.json"
    payloads = [{"writer": index, "body": "x" * 1000} for index in range(20)]
    builder.save_json(target, payloads[0])
    stop = threading.Event()
    malformed: list[str] = []

    def read_while_writing() -> None:
        while not stop.is_set():
            try:
                observed = json.loads(target.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                malformed.append(str(exc))
                continue
            if observed not in payloads:
                malformed.append(repr(observed))

    reader = threading.Thread(target=read_while_writing)
    reader.start()
    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(lambda payload: builder.save_json(target, payload), payloads))
    finally:
        stop.set()
        reader.join()

    assert malformed == []
    assert json.loads(target.read_text()) in payloads
    assert _residue(target) == []
