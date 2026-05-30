from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryCpuBaselineValidationPlan.v1"
PLAN_TYPE = "NORM_GEOMETRY_CPU_BASELINE_VALIDATION_PLAN"
OPERATOR_ID = "NORM_GEOMETRY"
LOCKED_FALSE_FLAGS = (
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
FORBIDDEN = (
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class NormGeometryCpuBaselineValidationPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_fixture_validation_scope() -> dict[str, Any]:
    return {
        "valid_fixture_count": 6,
        "fixture_ids_declared": True,
        "expected_value_comparison_declared": True,
        "determinism_required": True,
        "execution_enabled": False,
    }


def default_tolerance_policy() -> dict[str, bool]:
    return {
        "float64_required": True,
        "zero_tolerance_for_integer_inputs_declared": True,
        "tolerance_execution_enabled": False,
    }


def default_invalid_fixture_rejection_scope() -> dict[str, Any]:
    return {
        "invalid_fixture_count": 4,
        "not_computable_fixture_count": 4,
        "rejection_policy_declared": True,
        "execution_enabled": False,
    }


def default_no_runtime_scan() -> dict[str, bool]:
    return {
        "scan_declared": True,
        "runtime_mutation_blocked": True,
        "runtime_binding_blocked": True,
    }


def default_no_forecast_scan() -> dict[str, bool]:
    return {
        "scan_declared": True,
        "forecast_influence_blocked": True,
    }


def default_no_p43_scan() -> dict[str, bool]:
    return {
        "scan_declared": True,
        "p43_surface_lanes_blocked": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_validation_plan": True,
    }


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def validate_norm_geometry_cpu_baseline_validation_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "operator_id",
        "source_implementation_plan_refs", "fixture_validation_scope",
        "tolerance_policy", "invalid_fixture_rejection_scope",
        "no_runtime_scan", "no_forecast_scan", "no_p43_scan",
        "execution_authorized", "output_contract",
        "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise NormGeometryCpuBaselineValidationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise NormGeometryCpuBaselineValidationPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise NormGeometryCpuBaselineValidationPlanValidationError("unknown_operator_id")
    if packet["execution_authorized"] is not False:
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            "execution_authorized_must_be_false"
        )

    fvs = packet["fixture_validation_scope"]
    if not isinstance(fvs.get("valid_fixture_count"), int) or fvs["valid_fixture_count"] < 1:
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            "invalid_fixture_validation_scope_count"
        )
    if fvs.get("execution_enabled") is not False:
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            "fixture_validation_execution_must_be_false"
        )

    tp = packet["tolerance_policy"]
    if tp.get("tolerance_execution_enabled") is not False:
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            "tolerance_execution_must_be_false"
        )

    ifrs = packet["invalid_fixture_rejection_scope"]
    if ifrs.get("execution_enabled") is not False:
        raise NormGeometryCpuBaselineValidationPlanValidationError(
            "rejection_execution_must_be_false"
        )

    if packet["no_runtime_scan"] != default_no_runtime_scan():
        raise NormGeometryCpuBaselineValidationPlanValidationError("invalid_no_runtime_scan")
    if packet["no_forecast_scan"] != default_no_forecast_scan():
        raise NormGeometryCpuBaselineValidationPlanValidationError("invalid_no_forecast_scan")
    if packet["no_p43_scan"] != default_no_p43_scan():
        raise NormGeometryCpuBaselineValidationPlanValidationError("invalid_no_p43_scan")
    if packet["output_contract"] != default_output_contract():
        raise NormGeometryCpuBaselineValidationPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise NormGeometryCpuBaselineValidationPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )
    _prov_safe(packet["provenance"])


def compute_norm_geometry_cpu_baseline_validation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_norm_geometry_cpu_baseline_validation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_norm_geometry_cpu_baseline_validation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_implementation_plan_refs": sorted(
            payload.get("source_implementation_plan_refs", [])
        ),
        "fixture_validation_scope": payload.get(
            "fixture_validation_scope", default_fixture_validation_scope()
        ),
        "tolerance_policy": payload.get("tolerance_policy", default_tolerance_policy()),
        "invalid_fixture_rejection_scope": payload.get(
            "invalid_fixture_rejection_scope", default_invalid_fixture_rejection_scope()
        ),
        "no_runtime_scan": payload.get("no_runtime_scan", default_no_runtime_scan()),
        "no_forecast_scan": payload.get("no_forecast_scan", default_no_forecast_scan()),
        "no_p43_scan": payload.get("no_p43_scan", default_no_p43_scan()),
        "execution_authorized": False,
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_norm_geometry_cpu_baseline_validation_plan_hash(base)
    validate_norm_geometry_cpu_baseline_validation_plan(base)
    return _finalize(base)
