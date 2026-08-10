"""Fail-closed resolution of RDI artifact references.

This module is deliberately a resolver only.  It does not bind artifacts,
compute outcomes, activate declarations, or grant authority.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.forecasting.forecast_object import forecast_object_hash
from core.settlement.verdict import settlement_verdict_hash

from .contracts import canonical_intervention_json, canonical_transition_json


@dataclass(frozen=True)
class ResolvedArtifactRef:
    """A validated reference and the JSON payload it identifies."""

    kind: str
    object_id: str
    schema_version: str
    canonical_hash: str
    path: str
    payload: dict[str, Any]


class ArtifactResolutionError(ValueError):
    """A stable, fail-closed artifact resolution failure."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def resolve_intervention_ref(
    intervention_ref: Mapping[str, Any] | None, store_root: str | Path
) -> ResolvedArtifactRef | None:
    """Resolve an optional transition intervention reference.

    InstantiationTransition.v1 stores the compact ``object_id`` and
    ``canonical_hash`` form.  The resolver adds the contract identity before
    delegating to the common artifact-store resolver.  ``None`` is the
    explicitly absent optional reference; every present reference is
    fail-closed and advisory-only.
    """
    if intervention_ref is None:
        return None
    if not isinstance(intervention_ref, Mapping):
        raise ArtifactResolutionError(
            "MALFORMED_REF", "intervention_ref must be an object or null"
        )
    ref = {
        "kind": "intervention",
        "schema_version": "InterventionDeclaration.v1",
        "object_id": intervention_ref.get("object_id"),
        "canonical_hash": intervention_ref.get("canonical_hash"),
    }
    return resolve_artifact_refs([ref], store_root)[0]


def resolve_transition_intervention_ref(
    transition: Mapping[str, Any], store_root: str | Path
) -> ResolvedArtifactRef | None:
    """Resolve the intervention linked by an InstantiationTransition.v1.

    This is a read-only SHADOW binding helper.  It does not resolve an
    outcome, settle a verdict, or alter the transition payload.
    """
    if not isinstance(transition, Mapping):
        raise ArtifactResolutionError("MALFORMED_REF", "transition must be an object")
    return resolve_intervention_ref(transition.get("intervention_ref"), store_root)


@dataclass(frozen=True)
class _ArtifactSpec:
    schema_version: str
    directory: str
    hash_field: str


_SPECS: dict[str, _ArtifactSpec] = {
    "forecast": _ArtifactSpec("ForecastObject.v1", "forecast", "forecast_hash"),
    "settlement": _ArtifactSpec(
        "SettlementVerdict.v1", "settlement", "settlement_hash"
    ),
    "transition": _ArtifactSpec(
        "InstantiationTransition.v1", "instantiation", "transition_hash"
    ),
    "intervention": _ArtifactSpec(
        "InterventionDeclaration.v1", "intervention", "intervention_hash"
    ),
}

# Accept schema names as input convenience, while retaining one canonical kind
# and one canonical path for deterministic output.
_KIND_ALIASES = {
    "ForecastObject.v1": "forecast",
    "SettlementVerdict.v1": "settlement",
    "InstantiationTransition.v1": "transition",
    "InterventionDeclaration.v1": "intervention",
    "instantiation_transition": "transition",
    "intervention_declaration": "intervention",
}


def _kind(value: Any) -> str:
    raw = str(value)
    normalized = _KIND_ALIASES.get(raw, raw)
    if normalized not in _SPECS:
        raise ArtifactResolutionError("UNSUPPORTED_KIND", f"unsupported kind {raw!r}")
    return normalized


def _required_text(ref: Mapping[str, Any], name: str) -> str:
    value = ref.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ArtifactResolutionError("MALFORMED_REF", f"{name} must be non-blank")
    return value


def _relative_path(kind: str, object_id: str) -> Path:
    # IDs are path components, never paths.  Reject separators, dot segments,
    # absolute syntax, and platform-specific drive prefixes before joining.
    candidate = Path(object_id)
    if (
        candidate.is_absolute()
        or candidate.drive
        or object_id in {".", ".."}
        or "/" in object_id
        or "\\" in object_id
        or "\x00" in object_id
    ):
        raise ArtifactResolutionError("PATH_ESCAPE", f"unsafe object_id {object_id!r}")
    return Path("out") / _SPECS[kind].directory / f"{object_id}.json"


def _expected_hash(kind: str, payload: dict[str, Any]) -> str:
    if kind == "forecast":
        return forecast_object_hash(payload)
    if kind == "settlement":
        return settlement_verdict_hash(payload)
    if kind == "transition":
        return canonical_hash(json.loads(canonical_transition_json(payload)))
    if kind == "intervention":
        return canonical_hash(json.loads(canonical_intervention_json(payload)))
    raise AssertionError(f"unreachable artifact kind: {kind}")


def resolve_artifact_refs(
    refs: list[Mapping[str, Any]], store_root: str | Path
) -> tuple[ResolvedArtifactRef, ...]:
    """Resolve and validate all refs in deterministic order.

    ``store_root`` is the repository/artifact-store root containing ``out/``.
    Every input is validated before any result is returned; one bad reference
    therefore prevents partial projection.
    """
    normalized: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        kind = _kind(ref.get("kind"))
        object_id = _required_text(ref, "object_id")
        schema_version = _required_text(ref, "schema_version")
        expected_hash = _required_text(ref, "canonical_hash")
        key = (kind, object_id)
        if key in seen:
            raise ArtifactResolutionError(
                "DUPLICATE_REF", f"duplicate reference {kind}/{object_id}"
            )
        seen.add(key)
        _relative_path(kind, object_id)
        normalized.append((kind, object_id, schema_version, expected_hash))

    root = Path(store_root).resolve()
    resolved: list[ResolvedArtifactRef] = []
    for kind, object_id, ref_schema, expected_hash in sorted(
        normalized, key=lambda item: (item[0], item[1])
    ):
        spec = _SPECS[kind]
        relative = _relative_path(kind, object_id)
        target = (root / relative).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ArtifactResolutionError("PATH_ESCAPE", str(relative)) from exc
        if not target.is_file():
            raise ArtifactResolutionError("MISSING_ARTIFACT", str(relative))
        try:
            payload_raw = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ArtifactResolutionError("MALFORMED_JSON", str(relative)) from exc
        if not isinstance(payload_raw, dict):
            raise ArtifactResolutionError("MALFORMED_JSON", str(relative))
        payload = dict(payload_raw)
        if payload.get("schema_version") != spec.schema_version or ref_schema != spec.schema_version:
            raise ArtifactResolutionError("SCHEMA_MISMATCH", str(relative))
        payload_id = payload.get({
            "forecast": "forecast_id",
            "settlement": "settlement_id",
            "transition": "transition_id",
            "intervention": "intervention_id",
        }[kind])
        if payload_id != object_id:
            raise ArtifactResolutionError("SCHEMA_MISMATCH", str(relative))
        actual_hash = _expected_hash(kind, payload)
        if payload.get(spec.hash_field) != actual_hash or expected_hash != actual_hash:
            raise ArtifactResolutionError("HASH_MISMATCH", str(relative))
        resolved.append(
            ResolvedArtifactRef(
                kind=kind,
                object_id=object_id,
                schema_version=spec.schema_version,
                canonical_hash=actual_hash,
                path=relative.as_posix(),
                payload=payload,
            )
        )
    return tuple(resolved)
