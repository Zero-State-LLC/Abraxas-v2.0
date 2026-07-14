"""Canonical JSON utilities for ABRAXAS v2.0."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import stat
from pathlib import Path
from typing import Any

from core.file_cache import prime_text_cache, read_text_cached


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


def _write_text_atomically(target: Path, serialized: str) -> None:
    """Publish *serialized* without exposing a partial destination file."""
    try:
        destination_mode = stat.S_IMODE(target.stat().st_mode)
    except FileNotFoundError:
        destination_mode = None

    temporary: Path | None = None
    handle = None
    try:
        for _ in range(100):
            candidate = target.with_name(f".{target.name}.{secrets.token_hex(8)}.tmp")
            try:
                handle = candidate.open("x", encoding="utf-8", newline="")
            except FileExistsError:
                continue
            temporary = candidate
            break
        else:
            raise FileExistsError(f"unable to allocate temporary file for {target}")

        if destination_mode is not None:
            os.chmod(temporary, destination_mode)
        handle.write(serialized)
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        handle = None
        os.replace(temporary, target)
        temporary = None
    except BaseException as primary_error:
        if handle is not None:
            try:
                handle.close()
            except BaseException as cleanup_error:
                primary_error.add_note(f"temporary file close failed: {cleanup_error}")
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except BaseException as cleanup_error:
                primary_error.add_note(f"temporary file removal failed: {cleanup_error}")
        raise


def write_canonical_json_if_changed(path: str | Path, value: Any) -> bool:
    """Write canonical JSON only when the on-disk payload differs.

    Returns True when the file is written and False when an identical payload is
    already present on disk.
    """
    target = Path(path)
    serialized = canonical_dumps(value) + "\n"
    try:
        if read_text_cached(target) == serialized:
            return False
    except FileNotFoundError:
        pass
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_text_atomically(target, serialized)
    prime_text_cache(target, serialized)
    return True


def write_canonical_json(path: str | Path, value: Any) -> None:
    """Write canonical JSON to *path* with a trailing newline."""
    write_canonical_json_if_changed(path, value)
