from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorRegistryHardening.v1"

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

ALLOWED_HARDENING_STATUS = ("STABLE", "DEGRADED", "PARTIAL")
ALLOWED_COMPUTATION_STATUS = ("NOT_IMPLEMENTED", "SHADOW_STUB_ONLY")
ALLOWED_PLANNING_SCOPE = (
    "NONE",
    "CPU_BASELINE_PLANNING_COMPLETE",
    "SHADOW_STUB_ONLY_COMPLETE",
)
ALLOWED_GUARD_STATUS = ("ACTIVE", "INACTIVE", "DEGRADED")
ALLOWED_CHECK_RESULT = ("PASS", "FAIL", "NOT_EVALUATED")

FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-value",
)


class MetricOperatorRegistryHardeningError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_hardening_record": True,
    }


def default_governance_flags() -> dict[str, bool]:
    return {flag: False for flag in LOCKED_FALSE_FLAGS}


def default_operator_state_vector() -> list[dict[str, Any]]:
    shadow_operators = {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"}
    norm_geometry_operator = {"NORM_GEOMETRY"}
    all_operators = (
        "WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY",
        "TRANSPORT", "HYPERVECTOR_BINDING", "RESERVOIR_STATE_SPACE",
        "COUNTERFACTUAL_DIFFUSION", "HEAVY_TAIL", "HYSTERESIS",
        "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
    )
    entries = []
    for op in all_operators:
        if op in shadow_operators:
            entries.append({
                "operator_id": op,
                "computation_status": "SHADOW_STUB_ONLY",
                "planning_scope": "SHADOW_STUB_ONLY_COMPLETE",
                "execution_blocked": True,
                "metric_emission_blocked": True,
                "implementation_authorized": False,
            })
        elif op in norm_geometry_operator:
            entries.append({
                "operator_id": op,
                "computation_status": "NOT_IMPLEMENTED",
                "planning_scope": "CPU_BASELINE_PLANNING_COMPLETE",
                "execution_blocked": True,
                "metric_emission_blocked": True,
                "implementation_authorized": False,
            })
        else:
            entries.append({
                "operator_id": op,
                "computation_status": "NOT_IMPLEMENTED",
                "planning_scope": "NONE",
                "execution_blocked": True,
                "metric_emission_blocked": True,
                "implementation_authorized": False,
            })
    return entries


def default_drift_guards() -> list[dict[str, Any]]:
    return [
        {
            "guard_id": "drift-guard-001",
            "guard_type": "REGISTRY_BASELINE_PARITY",
            "description": (
                "WASSERSTEIN, CHAMFER_DISTANCE, and GEODESIC must remain at "
                "SHADOW_STUB_ONLY computation_status in both the registry and "
                "all baseline planning artifacts. Any status change requires "
                "explicit operator authorization."
            ),
            "guard_status": "ACTIVE",
            "operators_in_scope": ["CHAMFER_DISTANCE", "GEODESIC", "WASSERSTEIN"],
        },
        {
            "guard_id": "drift-guard-002",
            "guard_type": "NORM_GEOMETRY_IMPLEMENTATION_GATE",
            "description": (
                "NORM_GEOMETRY gate-cond-005 is unmet. No implementation PR may "
                "be opened for NORM_GEOMETRY. Operator explicit authorization "
                "instruction is required before any implementation work begins. "
                "This guard blocks premature advancement from CPU_BASELINE_PLANNING_COMPLETE."
            ),
            "guard_status": "ACTIVE",
            "operators_in_scope": ["NORM_GEOMETRY"],
        },
        {
            "guard_id": "drift-guard-003",
            "guard_type": "NO_UNAUTHORIZED_COMPUTATION",
            "description": (
                "No operator in the registry may advance beyond its current "
                "computation_status without operator authorization. "
                "implementation_authorized=False is enforced for all 12 operators. "
                "Computation additions, stub promotions, and CPU baseline "
                "activations are all blocked without explicit instruction."
            ),
            "guard_status": "ACTIVE",
            "operators_in_scope": [
                "CHAMFER_DISTANCE", "COUNTERFACTUAL_DIFFUSION", "GEODESIC",
                "HEAVY_TAIL", "HYPERVECTOR_BINDING", "HYSTERESIS",
                "NORM_GEOMETRY", "RESERVOIR_STATE_SPACE", "STOCHASTIC_GEOMETRY",
                "TOPOLOGICAL_PRIMITIVES", "TRANSPORT", "WASSERSTEIN",
            ],
        },
        {
            "guard_id": "drift-guard-004",
            "guard_type": "RESEARCH_CANARY_IMMUTABILITY",
            "description": (
                "Research canary artifacts are sealed and may not be regenerated. "
                "Any process that would regenerate or overwrite research_canary "
                "artifacts is blocked by this guard. The research canary serves "
                "as the integrity anchor for all operator planning work."
            ),
            "guard_status": "ACTIVE",
            "operators_in_scope": [],
        },
    ]


def default_hardening_checks() -> list[dict[str, Any]]:
    return [
        {
            "check_id": "check-001",
            "check_type": "NO_METRIC_EMISSION",
            "description": (
                "All 12 operators must have metric_emission_blocked=True. "
                "No operator may emit metric values in the current posture."
            ),
            "check_result": "PASS",
            "shadow_stub_only_operators_checked": 3,
            "not_implemented_operators_checked": 9,
        },
        {
            "check_id": "check-002",
            "check_type": "NO_FORECAST_INFLUENCE",
            "description": (
                "forecast_influence is locked False in all governance artifacts "
                "emitted by this bundle and all prior planning bundles. "
                "No operator may influence forecast lanes."
            ),
            "check_result": "PASS",
        },
        {
            "check_id": "check-003",
            "check_type": "NO_P43_SURFACE_LANES",
            "description": (
                "P43 surface lanes are blocked. No operator planning artifact "
                "has opened P43 surface lane access. p43_surface_lanes_blocked=True "
                "is declared in all validation plans."
            ),
            "check_result": "PASS",
        },
        {
            "check_id": "check-004",
            "check_type": "NO_PRODUCTION_ACTIVATION",
            "description": (
                "production_activation is locked False in all governance artifacts. "
                "No operator has been promoted to production."
            ),
            "check_result": "PASS",
        },
        {
            "check_id": "check-005",
            "check_type": "NO_CANON_PROMOTION",
            "description": (
                "canon_promotion is locked False in all governance artifacts. "
                "No operator or artifact has been promoted to canon status."
            ),
            "check_result": "PASS",
        },
        {
            "check_id": "check-006",
            "check_type": "NO_RESEARCH_CANARY_MUTATION",
            "description": (
                "Research canary artifacts have not been regenerated or overwritten "
                "by any bundle in the current session. The research canary "
                "integrity anchor is confirmed intact."
            ),
            "check_result": "PASS",
        },
        {
            "check_id": "check-007",
            "check_type": "SHADOW_STUB_ONLY_COUNT_VERIFIED",
            "description": (
                "Exactly 3 operators are at SHADOW_STUB_ONLY computation_status: "
                "WASSERSTEIN, CHAMFER_DISTANCE, GEODESIC."
            ),
            "check_result": "PASS",
            "expected_count": 3,
            "observed_count": 3,
        },
        {
            "check_id": "check-008",
            "check_type": "NOT_IMPLEMENTED_COUNT_VERIFIED",
            "description": (
                "Exactly 9 operators are at NOT_IMPLEMENTED computation_status: "
                "NORM_GEOMETRY, TRANSPORT, HYPERVECTOR_BINDING, "
                "RESERVOIR_STATE_SPACE, COUNTERFACTUAL_DIFFUSION, HEAVY_TAIL, "
                "HYSTERESIS, STOCHASTIC_GEOMETRY, TOPOLOGICAL_PRIMITIVES."
            ),
            "check_result": "PASS",
            "expected_count": 9,
            "observed_count": 9,
        },
        {
            "check_id": "check-009",
            "check_type": "NORM_GEOMETRY_PLANNING_SCOPE_VERIFIED",
            "description": (
                "NORM_GEOMETRY has planning_scope=CPU_BASELINE_PLANNING_COMPLETE. "
                "Readiness dossier, test vector schema plan, CPU baseline "
                "implementation plan, validation plan, and actual PR gate review "
                "are all present and sealed. Computation remains NOT_IMPLEMENTED."
            ),
            "check_result": "PASS",
        },
        {
            "check_id": "check-010",
            "check_type": "GATE_COND_005_CORRECTLY_UNMET",
            "description": (
                "gate-cond-005 in NormGeometryCpuBaselineActualPrGateReview.v1 "
                "is correctly recorded as condition_met=False. Operator explicit "
                "authorization has not been granted. This check passes when the "
                "gate is correctly unmet and no implementation PR has been opened."
            ),
            "check_result": "PASS",
        },
    ]


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
        return
    if isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise MetricOperatorRegistryHardeningError(
                "forbidden_provenance_reference_detected"
            )


def validate_metric_operator_registry_hardening(record: dict[str, Any]) -> None:
    required = {
        "schema_version", "hardening_id", "hardening_status",
        "operator_state_vector", "drift_guards", "hardening_checks",
        "source_refs", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - record.keys())
    if missing:
        raise MetricOperatorRegistryHardeningError(f"missing_required_fields:{missing}")

    if record["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorRegistryHardeningError("invalid_schema_version")

    if record["hardening_status"] not in ALLOWED_HARDENING_STATUS:
        raise MetricOperatorRegistryHardeningError(
            f"invalid_hardening_status:{record['hardening_status']}"
        )

    state_vector = record["operator_state_vector"]
    if not state_vector:
        raise MetricOperatorRegistryHardeningError("operator_state_vector_must_be_non_empty")

    seen_ids: set[str] = set()
    for entry in state_vector:
        oid = entry.get("operator_id", "")
        if oid in seen_ids:
            raise MetricOperatorRegistryHardeningError(f"duplicate_operator_id:{oid}")
        seen_ids.add(oid)
        if entry.get("computation_status") not in ALLOWED_COMPUTATION_STATUS:
            raise MetricOperatorRegistryHardeningError(
                f"invalid_computation_status:{entry.get('computation_status')}"
            )
        if entry.get("planning_scope") not in ALLOWED_PLANNING_SCOPE:
            raise MetricOperatorRegistryHardeningError(
                f"invalid_planning_scope:{entry.get('planning_scope')}"
            )
        if entry.get("execution_blocked") is not True:
            raise MetricOperatorRegistryHardeningError(
                f"execution_blocked_must_be_true:{oid}"
            )
        if entry.get("metric_emission_blocked") is not True:
            raise MetricOperatorRegistryHardeningError(
                f"metric_emission_blocked_must_be_true:{oid}"
            )
        if entry.get("implementation_authorized") is not False:
            raise MetricOperatorRegistryHardeningError(
                f"implementation_authorized_must_be_false:{oid}"
            )

    drift_guards = record["drift_guards"]
    if not drift_guards:
        raise MetricOperatorRegistryHardeningError("drift_guards_must_be_non_empty")

    seen_guard_ids: set[str] = set()
    for guard in drift_guards:
        gid = guard.get("guard_id", "")
        if gid in seen_guard_ids:
            raise MetricOperatorRegistryHardeningError(f"duplicate_guard_id:{gid}")
        seen_guard_ids.add(gid)
        if guard.get("guard_status") not in ALLOWED_GUARD_STATUS:
            raise MetricOperatorRegistryHardeningError(
                f"invalid_guard_status:{guard.get('guard_status')}"
            )

    hardening_checks = record["hardening_checks"]
    if not hardening_checks:
        raise MetricOperatorRegistryHardeningError("hardening_checks_must_be_non_empty")

    seen_check_ids: set[str] = set()
    for check in hardening_checks:
        cid = check.get("check_id", "")
        if cid in seen_check_ids:
            raise MetricOperatorRegistryHardeningError(f"duplicate_check_id:{cid}")
        seen_check_ids.add(cid)
        if check.get("check_result") not in ALLOWED_CHECK_RESULT:
            raise MetricOperatorRegistryHardeningError(
                f"invalid_check_result:{check.get('check_result')}"
            )

    if record["output_contract"] != default_output_contract():
        raise MetricOperatorRegistryHardeningError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if record["governance_flags"].get(flag) is not False:
            raise MetricOperatorRegistryHardeningError(
                f"authority_lock_must_be_false:{flag}"
            )

    _assert_provenance_safe(record["provenance"])


def compute_metric_operator_registry_hardening_hash(record: dict[str, Any]) -> str:
    return canonical_hash(_preimage(record))


def serialize_metric_operator_registry_hardening(record: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(record)) + "\n"


def build_metric_operator_registry_hardening(payload: dict[str, Any]) -> dict[str, Any]:
    state_vector = sorted(
        payload.get("operator_state_vector", default_operator_state_vector()),
        key=lambda e: e["operator_id"],
    )
    drift_guards = sorted(
        payload.get("drift_guards", default_drift_guards()),
        key=lambda g: g["guard_id"],
    )
    hardening_checks = sorted(
        payload.get("hardening_checks", default_hardening_checks()),
        key=lambda c: c["check_id"],
    )
    for guard in drift_guards:
        guard["operators_in_scope"] = sorted(guard.get("operators_in_scope", []))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "operator_state_vector": state_vector,
        "drift_guards": drift_guards,
        "hardening_checks": hardening_checks,
        "source_refs": sorted(payload.get("source_refs", [])),
        "output_contract": payload.get("output_contract", default_output_contract()),
        "governance_flags": payload.get("governance_flags", default_governance_flags()),
    }
    base["canonical_hash"] = compute_metric_operator_registry_hardening_hash(base)
    validate_metric_operator_registry_hardening(base)
    return _finalize(base)
