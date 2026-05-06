"""Tests for core/canonical/json.py"""

from __future__ import annotations

import json
from pathlib import Path


from core.canonical.json import (
    canonical_dumps,
    canonical_hash,
    normalize_numbers,
    write_canonical_json,
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
