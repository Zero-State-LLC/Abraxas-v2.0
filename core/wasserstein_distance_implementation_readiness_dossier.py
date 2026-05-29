from __future__ import annotations

import json
import re
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinDistanceImplementationReadinessDossier.v1"
DOSSIER_TYPE = "WASSERSTEIN_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"
OPERATOR_ID = "WASSERSTEIN"
INTENDED_LANE = "SHADOW"
READINESS_SCOPE = "IMPLEMENTATION_READINESS_ONLY"
DOSSIER_STATUS = "WASSERSTEIN_READINESS_DOSSIER_DEFINED"

ALLOWED_SCOPE_MODES = ("PLANNING_ONLY", "SHADOW_REFERENCE_ONLY", "CPU_REFERENCE_ONLY")
ALLOWED_PREREQ_STATUS = ("REQUIRED", "OPTIONAL", "DEFERRED")
ALLOWED_DEPENDENCY_TYPES = (
    "NUMERICAL_LIBRARY",
    "DATA_LAYOUT",
    "TEST_VECTOR",
    "MEMORY_LAYOUT",
    "FUTURE_ACCELERATION",
    "GEOMETRIC_ABSTRACTION",
)
ALLOWED_VALIDATION_TYPES = (
    "REFERENCE_VECTOR",
    "NUMERICAL_STABILITY",
    "DETERMINISTIC_REPLAY",
    "FLOATING_POINT_DRIFT",
    "EDGE_CASE_VALIDATION",
)
ALLOWED_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "DEFERRED")

REQUIRED_BLOCKED_SCOPES: frozenset[str] = frozenset({
    "wasserstein_computation",
    "emits_metric_values",
    "forecast_influence",
    "p43_surface_lanes",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
    "inference_authority",
})

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "shadow_lane_only",
    "readiness_dossier_only",
)
LOCKED_FALSE_AUTHORITY_KEYS = (
    "wasserstein_computation_authorized",
    "emits_metric_values",
    "forecast_influence",
    "p43_surface_lanes_authorized",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
    "inference_authority",
)
LOCKED_FALSE_GOVERNANCE_FLAGS = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)

FORBIDDEN_PROVENANCE_TOKENS = (
    "runtime activation",
    "autonomous execution",
    "scheduler mutation",
    "forecast routing",
    "self-modifying",
    "production deployment",
    "live execution",
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class WassersteinDistanceImplementationReadinessDossierValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_output_contract() -> dict[str, bool]:
    return {
        "implementation_completed": False,
        "runtime_enabled": False,
        "scheduler_enabled": False,
        "renderer_enabled": False,
        "oracle_enabled": False,
        "forecast_enabled": False,
        "production_ready": False,
    }


def default_authority_locks() -> dict[str, bool]:
    locks: dict[str, bool] = {}
    for k in LOCKED_TRUE_AUTHORITY_KEYS:
        locks[k] = True
    for k in LOCKED_FALSE_AUTHORITY_KEYS:
        locks[k] = False
    return locks


def default_governance_flags() -> dict[str, bool]:
    return {k: False for k in LOCKED_FALSE_GOVERNANCE_FLAGS}


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
    elif isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                "forbidden_provenance_reference_detected"
            )


def _assert_unique_by_id(items: list[dict[str, Any]], key: str, err: str) -> None:
    seen: set[str] = set()
    for item in items:
        ident = item.get(key)
        if ident in seen:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(err)
        seen.add(ident)


def _assert_sha256(value: str, field: str) -> None:
    if not _SHA256_RE.match(value):
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            f"invalid_sha256_hash:{field}"
        )


def validate_wasserstein_distance_implementation_readiness_dossier(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version", "dossier_id", "dossier_type", "selected_operator",
        "dossier_status", "source_selection_plan_hash", "source_metric_preflight_hash",
        "source_metric_registry_hash", "source_baseline_vector_pack_hash",
        "intended_lane", "readiness_scope", "implementation_scope",
        "mathematical_requirements", "input_shape_requirements",
        "determinism_requirements", "numerical_stability_requirements",
        "validation_requirements", "implementation_prerequisites",
        "dependency_inventory", "numerical_constraints", "implementation_risks",
        "blocked_scopes", "authority_locks", "recommended_next_step",
        "output_contract", "governance_flags", "provenance", "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_schema_version"
        )
    if packet["dossier_type"] != DOSSIER_TYPE:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_type"
        )
    if packet["selected_operator"] != OPERATOR_ID:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_selected_operator"
        )
    if packet["dossier_status"] != DOSSIER_STATUS:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_dossier_status"
        )
    if packet["intended_lane"] != INTENDED_LANE:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_intended_lane"
        )
    if packet["readiness_scope"] != READINESS_SCOPE:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_readiness_scope"
        )

    _assert_sha256(packet["source_selection_plan_hash"], "source_selection_plan_hash")
    _assert_sha256(packet["source_metric_preflight_hash"], "source_metric_preflight_hash")
    _assert_sha256(packet["source_metric_registry_hash"], "source_metric_registry_hash")
    _assert_sha256(
        packet["source_baseline_vector_pack_hash"], "source_baseline_vector_pack_hash"
    )

    scope_mode = packet["implementation_scope"].get("mode")
    if scope_mode not in ALLOWED_SCOPE_MODES:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "unknown_implementation_scope_mode"
        )

    for req_list in (
        "mathematical_requirements",
        "input_shape_requirements",
        "determinism_requirements",
        "numerical_stability_requirements",
        "numerical_constraints",
    ):
        val = packet[req_list]
        if not val or not all(isinstance(s, str) and s for s in val):
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                f"invalid_{req_list}"
            )

    prereqs = packet["implementation_prerequisites"]
    deps = packet["dependency_inventory"]
    val_reqs = packet["validation_requirements"]
    risks = packet["implementation_risks"]

    _assert_unique_by_id(prereqs, "prerequisite_id", "duplicate_prerequisite_id")
    _assert_unique_by_id(deps, "dependency_id", "duplicate_dependency_id")
    _assert_unique_by_id(val_reqs, "strategy_id", "duplicate_validation_strategy_id")
    _assert_unique_by_id(risks, "risk_id", "duplicate_risk_id")

    for item in prereqs:
        if item.get("status") not in ALLOWED_PREREQ_STATUS:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                "unknown_prerequisite_status"
            )
    for item in deps:
        if item.get("dependency_type") not in ALLOWED_DEPENDENCY_TYPES:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                "unknown_dependency_type"
            )
    for item in val_reqs:
        if item.get("validation_type") not in ALLOWED_VALIDATION_TYPES:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                "unknown_validation_type"
            )
    for item in risks:
        if item.get("risk_level") not in ALLOWED_RISK_LEVELS:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                "unknown_risk_level"
            )

    blocked = set(packet["blocked_scopes"])
    missing_scopes = sorted(REQUIRED_BLOCKED_SCOPES - blocked)
    if missing_scopes:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            f"missing_required_blocked_scopes:{missing_scopes}"
        )

    locks = packet["authority_locks"]
    for k in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(k) is not True:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_true:{k}"
            )
    for k in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(k) is not False:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                f"authority_lock_must_be_false:{k}"
            )

    if packet["output_contract"] != default_output_contract():
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_output_contract"
        )

    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise WassersteinDistanceImplementationReadinessDossierValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if not isinstance(packet.get("recommended_next_step"), str) or not packet["recommended_next_step"]:
        raise WassersteinDistanceImplementationReadinessDossierValidationError(
            "invalid_recommended_next_step"
        )

    _assert_provenance_safe(packet["provenance"])


def compute_wasserstein_distance_implementation_readiness_dossier_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_distance_implementation_readiness_dossier(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_distance_implementation_readiness_dossier(
    payload: dict[str, Any],
) -> dict[str, Any]:
    prereqs = sorted(
        payload.get("implementation_prerequisites", []),
        key=lambda x: x["prerequisite_id"],
    )
    deps = sorted(
        payload.get("dependency_inventory", []),
        key=lambda x: x["dependency_id"],
    )
    val_reqs = sorted(
        payload.get("validation_requirements", []),
        key=lambda x: x["strategy_id"],
    )
    risks = sorted(
        payload.get("implementation_risks", []),
        key=lambda x: x["risk_id"],
    )

    for item in prereqs + deps + val_reqs + risks:
        if "evidence_refs" in item:
            item["evidence_refs"] = sorted(item["evidence_refs"])

    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "dossier_type": DOSSIER_TYPE,
        "selected_operator": OPERATOR_ID,
        "dossier_status": DOSSIER_STATUS,
        "intended_lane": INTENDED_LANE,
        "readiness_scope": READINESS_SCOPE,
        "implementation_prerequisites": prereqs,
        "dependency_inventory": deps,
        "validation_requirements": val_reqs,
        "implementation_risks": risks,
        "mathematical_requirements": sorted(payload.get("mathematical_requirements", [])),
        "input_shape_requirements": sorted(payload.get("input_shape_requirements", [])),
        "determinism_requirements": sorted(payload.get("determinism_requirements", [])),
        "numerical_stability_requirements": sorted(
            payload.get("numerical_stability_requirements", [])
        ),
        "numerical_constraints": sorted(payload.get("numerical_constraints", [])),
        "blocked_scopes": sorted(payload.get("blocked_scopes", [])),
        "output_contract": payload.get("output_contract", default_output_contract()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
    }
    base["canonical_hash"] = compute_wasserstein_distance_implementation_readiness_dossier_hash(
        base
    )
    validate_wasserstein_distance_implementation_readiness_dossier(base)
    return _finalize(base)
