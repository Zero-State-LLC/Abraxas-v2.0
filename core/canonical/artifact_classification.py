"""Artifact classification and current-state influence policy (ADR-0018)."""

from __future__ import annotations

from enum import Enum
from typing import Any


class ArtifactClass(str, Enum):
    CANONICAL_DOMAIN_ARTIFACT = "CANONICAL_DOMAIN_ARTIFACT"
    GOVERNANCE_DECISION = "GOVERNANCE_DECISION"
    AUDIT_EVIDENCE = "AUDIT_EVIDENCE"
    BUILD_EVIDENCE = "BUILD_EVIDENCE"
    RUNTIME_EVENT = "RUNTIME_EVENT"
    GENERATED_PLAN = "GENERATED_PLAN"
    HISTORICAL_RECEIPT = "HISTORICAL_RECEIPT"


# Only these classes may influence current canonical state.
STATE_INFLUENCE: dict[ArtifactClass, bool] = {
    ArtifactClass.CANONICAL_DOMAIN_ARTIFACT: True,
    ArtifactClass.GOVERNANCE_DECISION: True,
    ArtifactClass.AUDIT_EVIDENCE: False,
    ArtifactClass.BUILD_EVIDENCE: False,
    ArtifactClass.RUNTIME_EVENT: False,
    ArtifactClass.GENERATED_PLAN: False,
    ArtifactClass.HISTORICAL_RECEIPT: False,
}

REQUIRES_VALID_AUTHORITY: frozenset[ArtifactClass] = frozenset(
    {ArtifactClass.GOVERNANCE_DECISION}
)

_FORBIDDEN_AUTHORITY_TRUE_FLAGS = frozenset(
    {
        "promotion_allowed",
        "forecast_weight_allowed",
        "runtime_mutation_allowed",
        "baseline_mutation_allowed",
        "canon_mutation_allowed",
        "shadow_to_forecast_escalation_allowed",
        "aal_viz_inference_authority",
    }
)


class ArtifactClassificationError(ValueError):
    """Raised when classification or authority policy is violated."""


def influences_current_state(artifact_class: ArtifactClass | str) -> bool:
    return STATE_INFLUENCE[ArtifactClass(artifact_class)]


def policy_matrix() -> dict[str, dict[str, Any]]:
    return {
        cls.value: {
            "influences_current_state": STATE_INFLUENCE[cls],
            "requires_valid_authority": cls in REQUIRES_VALID_AUTHORITY,
        }
        for cls in ArtifactClass
    }


def _authority_violations(payload: dict[str, Any]) -> list[str]:
    locks = payload.get("authority_locks")
    if not isinstance(locks, dict):
        # GOVERNANCE_DECISION must carry explicit locked authority.
        return ["missing_authority_locks"]
    bad = [
        key
        for key, value in locks.items()
        if key in _FORBIDDEN_AUTHORITY_TRUE_FLAGS and value is True
    ]
    return bad


def validate_classification(
    payload: dict[str, Any],
    artifact_class: ArtifactClass | str,
) -> None:
    cls = ArtifactClass(artifact_class)
    expected_influence = STATE_INFLUENCE[cls]
    claimed = payload.get("influences_current_state")
    if claimed is not None and bool(claimed) != expected_influence:
        raise ArtifactClassificationError(
            f"influences_current_state={claimed!r} incompatible with {cls.value} "
            f"(expected {expected_influence})"
        )
    if cls in REQUIRES_VALID_AUTHORITY:
        violations = _authority_violations(payload)
        if violations:
            raise ArtifactClassificationError(
                f"{cls.value} requires valid authority; violations={violations}"
            )
    existing_class = payload.get("artifact_class")
    if existing_class is not None and str(existing_class) != cls.value:
        raise ArtifactClassificationError(
            f"payload artifact_class={existing_class!r} conflicts with requested {cls.value}"
        )


def stamp_classification(
    payload: dict[str, Any],
    artifact_class: ArtifactClass | str,
    *,
    rehash_fields: tuple[str, ...] = ("canonical_hash", "result_hash", "content_hash"),
) -> dict[str, Any]:
    """Return a shallow-copied payload with classification fields applied.

    Hash fields listed in *rehash_fields* are removed so callers can recompute
    after stamping. Does not write to disk.
    """
    cls = ArtifactClass(artifact_class)
    validate_classification(payload, cls)
    stamped = dict(payload)
    stamped["artifact_class"] = cls.value
    stamped["influences_current_state"] = STATE_INFLUENCE[cls]
    for field in rehash_fields:
        stamped.pop(field, None)
    return stamped
