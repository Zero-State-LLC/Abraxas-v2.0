"""Deterministic process-local file caches for runtime hot paths."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class _FileSignature:
    size: int
    mtime_ns: int


@dataclass(slots=True)
class _FileCacheEntry:
    signature: _FileSignature
    text: str
    json_value: Any | None = None


_FILE_CACHE: dict[str, _FileCacheEntry] = {}


def _cache_key(path: str | Path) -> str:
    return Path(path).resolve().as_posix()


def _signature(path: Path) -> _FileSignature:
    stat = path.stat()
    return _FileSignature(size=stat.st_size, mtime_ns=stat.st_mtime_ns)


def clear_file_cache() -> None:
    """Clear all process-local cached file contents."""
    _FILE_CACHE.clear()


def prime_text_cache(path: str | Path, text: str) -> None:
    """Store known on-disk text for *path* after a deterministic write."""
    target = Path(path)
    _FILE_CACHE[_cache_key(target)] = _FileCacheEntry(
        signature=_signature(target),
        text=text,
    )


def read_text_cached(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Read text from *path* with deterministic stat-based invalidation."""
    target = Path(path)
    key = _cache_key(target)
    signature = _signature(target)
    cached = _FILE_CACHE.get(key)
    if cached is not None and cached.signature == signature:
        return cached.text
    text = target.read_text(encoding=encoding)
    _FILE_CACHE[key] = _FileCacheEntry(signature=signature, text=text)
    return text


def read_json_cached(path: str | Path) -> Any:
    """Read JSON from *path* with deterministic stat-based invalidation."""
    target = Path(path)
    key = _cache_key(target)
    signature = _signature(target)
    cached = _FILE_CACHE.get(key)
    if cached is not None and cached.signature == signature and cached.json_value is not None:
        return copy.deepcopy(cached.json_value)
    if cached is not None and cached.signature == signature:
        text = cached.text
    else:
        text = target.read_text(encoding="utf-8")
    value = json.loads(text)
    _FILE_CACHE[key] = _FileCacheEntry(
        signature=signature,
        text=text,
        json_value=value,
    )
    return copy.deepcopy(value)
