"""Shared Alembic helpers — deterministic IDs and serialization."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash


def det_timestamp(seed: str) -> str:
    digest = canonical_hash({"seed": seed})
    return f"deterministic:{digest[:16]}"


def make_id(prefix: str, *parts: Any) -> str:
    digest = canonical_hash({"prefix": prefix, "parts": list(parts)})
    return f"{prefix}:{digest[:16]}"


def to_canonical_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        payload = model.model_dump(mode="python")
    elif isinstance(model, dict):
        payload = model
    else:
        raise TypeError(f"unsupported model type: {type(model)!r}")
    # Round-trip through canonical JSON for stable shapes.
    import json

    return json.loads(canonical_dumps(payload))


def hash_model(model: Any) -> str:
    return canonical_hash(to_canonical_dict(model))
