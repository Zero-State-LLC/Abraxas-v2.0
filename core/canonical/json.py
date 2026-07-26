"""Canonical JSON utilities for ABRAXAS v2.0."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import stat
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import (
    ArtifactClass,
    ArtifactClassificationError,
    stamp_classification,
)
from core.file_cache import prime_text_cache, read_text_cached


class CanonicalWriteError(ValueError):
    """Fail-closed canonical write policy violation."""


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


def _resolve_under_root(path: Path, root: Path) -> Path:
    target = path.resolve()
    base = root.resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise CanonicalWriteError(
            f"path traversal denied: {path} is outside allowed root {root}"
        ) from exc
    return target


def prepare_canonical_artifact(
    value: dict[str, Any],
    artifact_class: ArtifactClass | str,
) -> dict[str, Any]:
    """Stamp classification fields and recompute ``canonical_hash`` (pure)."""
    if not isinstance(value, dict):
        raise CanonicalWriteError("classified artifact payload must be a JSON object")
    try:
        stamped = stamp_classification(value, artifact_class)
    except ArtifactClassificationError as exc:
        raise CanonicalWriteError(str(exc)) from exc
    body = {key: item for key, item in stamped.items() if key != "canonical_hash"}
    stamped["canonical_hash"] = canonical_hash(body)
    return stamped


def write_canonical_artifact(
    path: str | Path,
    value: dict[str, Any],
    *,
    artifact_class: ArtifactClass | str,
    out_root: str | Path | None = None,
    append_only: bool = False,
    if_changed: bool = True,
) -> bool:
    """Write a classified artifact through the canonical serializer.

    - Stamps ``artifact_class`` and ``influences_current_state`` per ADR-0018.
    - Optionally confines writes under *out_root* (path traversal protection).
    - ``append_only`` refuses overwrite when the destination already exists.
    - Does not invent timestamps; callers inject deterministic clocks if needed.

    Returns whether a write occurred (False when ``if_changed`` skips).
    """
    stamped = prepare_canonical_artifact(value, artifact_class)
    target = Path(path)
    if out_root is not None:
        target = _resolve_under_root(target, Path(out_root))

    if append_only and target.exists():
        raise CanonicalWriteError(f"append_only collision: {target} already exists")

    if if_changed:
        return write_canonical_json_if_changed(target, stamped)
    write_canonical_json(target, stamped)
    return True


def infer_out_root(path: str | Path, *, fallback: str | Path | None = "out") -> Path | None:
    """Infer the ``out/`` root that contains *path*, else *fallback*."""
    target = Path(path)
    if not target.is_absolute():
        target = Path.cwd() / target
    for parent in (target.parent, *target.parents):
        if parent.name == "out":
            return parent.resolve()
    if fallback is None:
        return None
    return Path(fallback).resolve()


def write_classified_json(
    path: str | Path,
    value: Any,
    *,
    artifact_class: ArtifactClass | str = ArtifactClass.AUDIT_EVIDENCE,
    out_root: str | Path | None = None,
    append_only: bool = False,
    if_changed: bool = True,
) -> bool:
    """Migration helper: classified write for dicts; legacy writer for non-dicts.

    Prefer this (or ``write_canonical_artifact``) over bare ``write_canonical_json``
    for governed ``out/`` publication paths.
    """
    if isinstance(value, dict):
        resolved_root = out_root if out_root is not None else infer_out_root(path)
        return write_canonical_artifact(
            path,
            value,
            artifact_class=artifact_class,
            out_root=resolved_root,
            append_only=append_only,
            if_changed=if_changed,
        )
    if if_changed:
        return write_canonical_json_if_changed(path, value)
    write_canonical_json(path, value)
    return True
