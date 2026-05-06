"""Canonical JSON utilities for ABRAXAS v2.0."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def normalize_numbers(value: Any) -> Any:
    """Recursively round floats to 6 decimal places."""
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, dict):
        return {k: normalize_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_numbers(item) for item in value]
    return value


def canonical_dumps(value: Any) -> str:
    """Serialize to canonical JSON: sorted keys, minimal separators, unicode."""
    normalized = normalize_numbers(value)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(value: Any) -> str:
    """Return sha256 hex digest of the canonical JSON representation."""
    serialized = canonical_dumps(value)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def write_canonical_json(path: str | Path, value: Any) -> None:
    """Write canonical JSON to *path* with a trailing newline."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(canonical_dumps(value) + "\n", encoding="utf-8")
