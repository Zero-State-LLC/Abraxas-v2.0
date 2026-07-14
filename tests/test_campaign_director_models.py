from __future__ import annotations

import json
import os
import stat
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import pytest

from core.campaign_director.models import save_json


def _expected(value: Any, *, indent: int = 2) -> bytes:
    return json.dumps(value, indent=indent, sort_keys=True, default=str).encode("utf-8")


@pytest.mark.parametrize("indent", [0, 1, 2, 4])
def test_save_json_preserves_campaign_serialization_profile(
    tmp_path: Path, indent: int
) -> None:
    class CampaignPhase(Enum):
        READY = "ready"

    class CampaignValue:
        def __str__(self) -> str:
            return "campaign-value"

    payload = {
        "empty": {},
        "nested": {"items": [True, False, None, 1.23456789]},
        "unicode": "lambda: \u03bb; kanji: \u6f22\u5b57",
        "datetime": datetime(2026, 7, 14, tzinfo=timezone.utc),
        "path": Path("campaign/state.json"),
        "enum": CampaignPhase.READY,
        "custom": CampaignValue(),
    }
    target = tmp_path / f"indent-{indent}.json"

    result = save_json(target, payload, indent=indent)

    assert result is None
    assert target.read_bytes() == _expected(payload, indent=indent)
    assert not target.read_bytes().endswith(b"\n")


def test_save_json_handles_large_payload_and_creates_parents(tmp_path: Path) -> None:
    payload = {"campaign": [{"cycle": i, "value": "x" * 100} for i in range(5000)]}
    target = tmp_path / "nested" / "large.json"

    save_json(target, payload)

    assert target.read_bytes() == _expected(payload)
    assert list(target.parent.glob(".large.json.*.tmp")) == []


def test_save_json_first_write_permissions_match_direct_open(tmp_path: Path) -> None:
    reference = tmp_path / "reference.json"
    target = tmp_path / "campaign.json"
    with reference.open("w", encoding="utf-8") as handle:
        handle.write("{}")

    save_json(target, {})

    assert stat.S_IMODE(target.stat().st_mode) == stat.S_IMODE(reference.stat().st_mode)


def test_save_json_rewrites_unchanged_content_and_preserves_mode(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    payload = {"campaign": "unchanged"}
    save_json(target, payload)
    target.chmod(0o640)
    before = target.stat()
    os.utime(
        target,
        ns=(before.st_atime_ns, before.st_mtime_ns - 2_000_000_000),
    )
    before = target.stat()

    save_json(target, payload)

    after = target.stat()
    assert target.read_bytes() == _expected(payload)
    assert stat.S_IMODE(after.st_mode) == 0o640
    assert after.st_mtime_ns > before.st_mtime_ns
    assert after.st_ino != before.st_ino


class _FailingHandle:
    def __init__(self, handle: Any, failure_point: str) -> None:
        self.handle = handle
        self.failure_point = failure_point

    def write(self, data: str) -> int:
        if self.failure_point == "write":
            self.handle.write(data[:5])
            self.handle.flush()
            raise OSError("controlled campaign write failure")
        return self.handle.write(data)

    def flush(self) -> None:
        if self.failure_point == "flush":
            raise OSError("controlled campaign flush failure")
        self.handle.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.handle, name)


@pytest.mark.parametrize("failure_point", ["write", "flush"])
def test_save_json_stream_failure_preserves_prior_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
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
    with pytest.raises(OSError, match=f"controlled campaign {failure_point} failure"):
        save_json(target, {"replacement": "value"})

    assert target.read_bytes() == prior
    assert list(tmp_path.glob(".preserved.json.*.tmp")) == []


@pytest.mark.parametrize("failure_point", ["fsync", "replace"])
def test_save_json_publication_failure_preserves_prior_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
) -> None:
    target = tmp_path / "preserved.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)

    def fail(*_args: Any, **_kwargs: Any) -> None:
        raise OSError(f"controlled campaign {failure_point} failure")

    monkeypatch.setattr(os, failure_point, fail)
    with pytest.raises(OSError, match=f"controlled campaign {failure_point} failure"):
        save_json(target, {"replacement": "value"})

    assert target.read_bytes() == prior
    assert list(tmp_path.glob(".preserved.json.*.tmp")) == []


def test_save_json_cleanup_failure_preserves_primary_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "cleanup.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)
    original_unlink = Path.unlink

    def fail_fsync(*_args: Any, **_kwargs: Any) -> None:
        raise OSError("controlled campaign fsync failure")

    def fail_cleanup(self: Path, *args: Any, **kwargs: Any) -> None:
        raise OSError("controlled campaign cleanup failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)
    monkeypatch.setattr(Path, "unlink", fail_cleanup)
    with pytest.raises(OSError, match="controlled campaign fsync failure") as exc_info:
        save_json(target, {"replacement": "value"})

    assert target.read_bytes() == prior
    assert any("temporary file removal failed" in note for note in exc_info.value.__notes__)
    residue = list(tmp_path.glob(".cleanup.json.*.tmp"))
    assert len(residue) == 1
    original_unlink(residue[0])


def test_save_json_serialization_failure_does_not_touch_destination(tmp_path: Path) -> None:
    class BrokenValue:
        def __str__(self) -> str:
            raise ValueError("controlled campaign serialization failure")

    target = tmp_path / "serialization.json"
    prior = b'{"valid":"prior"}'
    target.write_bytes(prior)

    with pytest.raises(ValueError, match="controlled campaign serialization failure"):
        save_json(target, {"broken": BrokenValue()})

    assert target.read_bytes() == prior
    assert list(tmp_path.glob(".serialization.json.*.tmp")) == []


def test_save_json_concurrent_writers_never_expose_malformed_json(tmp_path: Path) -> None:
    target = tmp_path / "concurrent.json"
    payloads = [{"writer": index, "body": "x" * 1000} for index in range(20)]
    save_json(target, payloads[0])
    stop = threading.Event()
    malformed: list[str] = []

    def read_while_writing() -> None:
        while not stop.is_set():
            try:
                observed = json.loads(target.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                malformed.append(str(exc))
                continue
            if observed not in payloads:
                malformed.append(repr(observed))

    reader = threading.Thread(target=read_while_writing)
    reader.start()

    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(lambda payload: save_json(target, payload), payloads))
    finally:
        stop.set()
        reader.join()

    assert malformed == []
    assert json.loads(target.read_text(encoding="utf-8")) in payloads
    assert list(tmp_path.glob(".concurrent.json.*.tmp")) == []
