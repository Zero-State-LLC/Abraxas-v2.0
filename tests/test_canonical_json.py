"""Tests for core/canonical/json.py"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest
from core.canonical.json import (
    canonical_dumps,
    canonical_hash,
    normalize_numbers,
    write_canonical_json,
    write_canonical_json_if_changed,
)


def test_identical_dicts_different_key_order_hash_same():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonical_hash(a) == canonical_hash(b)


def test_floats_rounded_to_6_decimals():
    result = normalize_numbers({"x": 1.123456789})
    assert result == {"x": 1.123457}


def test_nested_float_normalization():
    data = {"a": {"b": [1.9999999, 0.0000001]}}
    result = normalize_numbers(data)
    assert result["a"]["b"][0] == 2.0
    assert result["a"]["b"][1] == 0.0


def test_canonical_dumps_sorted_keys():
    data = {"z": 1, "a": 2}
    dumped = canonical_dumps(data)
    assert dumped.index('"a"') < dumped.index('"z"')


def test_canonical_dumps_minimal_separators():
    data = {"key": "value"}
    dumped = canonical_dumps(data)
    assert " " not in dumped


def test_output_is_deterministic():
    data = {"c": 3, "b": 2, "a": 1}
    assert canonical_dumps(data) == canonical_dumps(data)
    assert canonical_hash(data) == canonical_hash(data)


def test_write_canonical_json(tmp_path: Path):
    out = tmp_path / "test.json"
    data = {"hello": "world"}
    write_canonical_json(out, data)
    content = out.read_text(encoding="utf-8")
    assert content.endswith("\n")
    loaded = json.loads(content)
    assert loaded == data


def test_hash_is_sha256_hex():
    h = canonical_hash({"x": 1})
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_write_canonical_json_if_changed_skips_identical_payload(tmp_path: Path):
    out = tmp_path / "dedupe.json"

    assert write_canonical_json_if_changed(out, {"hello": "world"}) is True
    assert write_canonical_json_if_changed(out, {"hello": "world"}) is False
    assert write_canonical_json_if_changed(out, {"hello": "again"}) is True
    assert json.loads(out.read_text(encoding="utf-8")) == {"hello": "again"}


def test_write_canonical_json_is_byte_stable_and_cleans_temporary_files(tmp_path: Path):
    out = tmp_path / "stable.json"
    expected = canonical_dumps({"z": 1.123456789, "a": "value"}) + "\n"

    write_canonical_json(out, {"z": 1.123456789, "a": "value"})
    first = out.read_bytes()
    write_canonical_json(out, {"a": "value", "z": 1.123456789})

    assert first == expected.encode("utf-8")
    assert out.read_bytes() == first
    assert list(tmp_path.glob(".stable.json.*.tmp")) == []


def test_write_canonical_json_creates_parents_and_preserves_existing_mode(tmp_path: Path):
    out = tmp_path / "nested" / "mode.json"
    write_canonical_json(out, {"version": 1})
    out.chmod(0o640)

    write_canonical_json(out, {"version": 2})

    assert json.loads(out.read_text(encoding="utf-8")) == {"version": 2}
    assert stat.S_IMODE(out.stat().st_mode) == 0o640


@pytest.mark.parametrize("failure_point", ["fsync", "replace"])
def test_write_canonical_json_failure_preserves_prior_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
):
    out = tmp_path / "preserved.json"
    prior = b'{"valid":"prior"}\n'
    out.write_bytes(prior)

    def fail(*_args: object, **_kwargs: object) -> None:
        raise OSError(f"controlled {failure_point} failure")

    monkeypatch.setattr(os, failure_point, fail)
    with pytest.raises(OSError, match=f"controlled {failure_point} failure"):
        write_canonical_json(out, {"replacement": "value"})

    assert out.read_bytes() == prior
    assert list(tmp_path.glob(".preserved.json.*.tmp")) == []
