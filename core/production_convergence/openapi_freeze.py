"""OpenAPI supported-surface freeze helpers (Phase 7)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def extract_route_surface(openapi_spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return sorted [{path, methods}] from an OpenAPI 3 paths object."""
    paths = openapi_spec.get("paths") or {}
    surface: list[dict[str, Any]] = []
    http_methods = ("get", "post", "put", "patch", "delete", "options", "head")
    for path in sorted(paths):
        item = paths[path]
        if not isinstance(item, Mapping):
            continue
        methods = sorted(
            method.upper() for method in http_methods if method in item
        )
        if methods:
            surface.append({"path": path, "methods": methods})
    return surface


def freeze_violations(
    *,
    live_surface: list[dict[str, Any]],
    frozen_surface: list[dict[str, Any]],
) -> list[str]:
    """Return human-readable violations when frozen routes shrink or lose methods."""
    live = {entry["path"]: set(entry["methods"]) for entry in live_surface}
    violations: list[str] = []
    for entry in frozen_surface:
        path = entry["path"]
        required = set(entry["methods"])
        if path not in live:
            violations.append(f"missing_path:{path}")
            continue
        missing = sorted(required - live[path])
        if missing:
            violations.append(f"missing_methods:{path}:{','.join(missing)}")
    return violations
