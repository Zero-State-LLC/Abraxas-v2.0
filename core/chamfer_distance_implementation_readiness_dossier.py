from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferDistanceImplementationReadinessDossier.v1"
DOSSIER_TYPE = "CHAMFER_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"
ALLOWED_OPERATOR_IDS = ("CHAMFER_DISTANCE",)
ALLOWED_SCOPE_MODES = ("CPU_ONLY", "CPU_REFERENCE_ONLY", "FUTURE_GPU_CANDIDATE", "FUTURE_STREAMING_CANDIDATE")
ALLOWED_PREREQ_STATUS = ("REQUIRED", "OPTIONAL", "DEFERRED")
ALLOWED_DEPENDENCY_TYPES = ("NUMERICAL_LIBRARY", "DATA_LAYOUT", "TEST_VECTOR", "MEMORY_LAYOUT", "FUTURE_ACCELERATION", "GEOMETRIC_ABSTRACTION")
ALLOWED_VALIDATION_TYPES = ("REFERENCE_VECTOR", "NUMERICAL_STABILITY", "DETERMINISTIC_REPLAY", "FLOATING_POINT_DRIFT", "EDGE_CASE_VALIDATION")
ALLOWED_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "DEFERRED")
LOCKED_FALSE_FLAGS = ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")
FORBIDDEN_PROVENANCE_TOKENS = ("runtime activation", "autonomous execution", "scheduler mutation", "forecast routing", "self-modifying", "production deployment", "live execution")


class ChamferDistanceImplementationReadinessDossierValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_output_contract() -> dict[str, bool]:
    return {"implementation_completed": False, "runtime_enabled": False, "scheduler_enabled": False, "renderer_enabled": False, "oracle_enabled": False, "forecast_enabled": False, "production_ready": False}


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
            raise ChamferDistanceImplementationReadinessDossierValidationError("forbidden_provenance_reference_detected")


def _assert_unique_by_id(items: list[dict[str, Any]], key: str, err: str) -> None:
    seen: set[str] = set()
    for item in items:
        ident = item.get(key)
        if ident in seen:
            raise ChamferDistanceImplementationReadinessDossierValidationError(err)
        seen.add(ident)


def validate_chamfer_distance_implementation_readiness_dossier(packet: dict[str, Any]) -> None:
    required = {"schema_version", "dossier_id", "dossier_type", "operator_id", "implementation_scope", "implementation_prerequisites", "dependency_inventory", "numerical_constraints", "validation_strategy", "implementation_risks", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"}
    missing = sorted(required - packet.keys())
    if missing:
        raise ChamferDistanceImplementationReadinessDossierValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise ChamferDistanceImplementationReadinessDossierValidationError("invalid_schema_version")
    if packet["dossier_type"] != DOSSIER_TYPE:
        raise ChamferDistanceImplementationReadinessDossierValidationError("invalid_dossier_type")
    if packet["operator_id"] not in ALLOWED_OPERATOR_IDS:
        raise ChamferDistanceImplementationReadinessDossierValidationError("unknown_operator_id")

    scope_mode = packet["implementation_scope"].get("mode")
    if scope_mode not in ALLOWED_SCOPE_MODES:
        raise ChamferDistanceImplementationReadinessDossierValidationError("unknown_implementation_scope_mode")

    prereqs = packet["implementation_prerequisites"]
    deps = packet["dependency_inventory"]
    validations = packet["validation_strategy"]
    risks = packet["implementation_risks"]

    _assert_unique_by_id(prereqs, "prerequisite_id", "duplicate_prerequisite_id")
    _assert_unique_by_id(deps, "dependency_id", "duplicate_dependency_id")
    _assert_unique_by_id(validations, "strategy_id", "duplicate_validation_strategy_id")
    _assert_unique_by_id(risks, "risk_id", "duplicate_risk_id")

    for item in prereqs:
        if item.get("status") not in ALLOWED_PREREQ_STATUS:
            raise ChamferDistanceImplementationReadinessDossierValidationError("unknown_prerequisite_status")
    for item in deps:
        if item.get("dependency_type") not in ALLOWED_DEPENDENCY_TYPES:
            raise ChamferDistanceImplementationReadinessDossierValidationError("unknown_dependency_type")
    for item in validations:
        if item.get("validation_type") not in ALLOWED_VALIDATION_TYPES:
            raise ChamferDistanceImplementationReadinessDossierValidationError("unknown_validation_type")
    for item in risks:
        if item.get("risk_level") not in ALLOWED_RISK_LEVELS:
            raise ChamferDistanceImplementationReadinessDossierValidationError("unknown_risk_level")

    if packet["output_contract"] != default_output_contract():
        raise ChamferDistanceImplementationReadinessDossierValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise ChamferDistanceImplementationReadinessDossierValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(packet["provenance"])


def compute_chamfer_distance_implementation_readiness_dossier_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_distance_implementation_readiness_dossier(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_chamfer_distance_implementation_readiness_dossier(payload: dict[str, Any]) -> dict[str, Any]:
    prereqs = sorted(payload.get("implementation_prerequisites", []), key=lambda x: x["prerequisite_id"])
    deps = sorted(payload.get("dependency_inventory", []), key=lambda x: x["dependency_id"])
    validations = sorted(payload.get("validation_strategy", []), key=lambda x: x["strategy_id"])
    risks = sorted(payload.get("implementation_risks", []), key=lambda x: x["risk_id"])

    for item in prereqs + deps + validations + risks:
        if "evidence_refs" in item:
            item["evidence_refs"] = sorted(item.get("evidence_refs", []))

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "dossier_type": DOSSIER_TYPE,
        "operator_id": "CHAMFER_DISTANCE",
        "implementation_prerequisites": prereqs,
        "dependency_inventory": deps,
        "validation_strategy": validations,
        "implementation_risks": risks,
        "numerical_constraints": sorted(payload.get("numerical_constraints", [])),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_chamfer_distance_implementation_readiness_dossier_hash(base)
    validate_chamfer_distance_implementation_readiness_dossier(base)
    return _finalize(base)
