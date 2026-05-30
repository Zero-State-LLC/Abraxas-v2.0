from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorRegistryStabilization.v1"

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

ALLOWED_VECTOR_TYPES = (
    "VALID_METADATA_VECTOR",
    "VALID_ABSENT_VECTOR",
    "VALID_NOT_COMPUTABLE_VECTOR",
    "VALID_SHADOW_ONLY_VECTOR",
)

ALLOWED_COMPUTATION_STATUS = (
    "DECLARED_ONLY",
    "METADATA_ONLY",
    "NOT_IMPLEMENTED",
    "SHADOW_STUB_ONLY",
    "NOT_COMPUTABLE",
)

ALLOWED_STABILIZATION_STATUS = ("STABLE", "DEGRADED", "PARTIAL")

FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-value",
)


class MetricOperatorRegistryStabilizationError(ValueError):
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
        "emits_stabilization_record": True,
    }


def default_governance_flags() -> dict[str, bool]:
    return {flag: False for flag in LOCKED_FALSE_FLAGS}


def three_operator_default_operator_entries() -> list[dict[str, Any]]:
    shadow_operators = {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"}
    all_operators = (
        "WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT",
        "HYPERVECTOR_BINDING", "RESERVOIR_STATE_SPACE", "COUNTERFACTUAL_DIFFUSION",
        "HEAVY_TAIL", "HYSTERESIS", "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
    )
    entries = []
    for op in all_operators:
        if op in shadow_operators:
            entries.append({"operator_id": op, "vector_type": "VALID_SHADOW_ONLY_VECTOR", "expected_computation_status": "SHADOW_STUB_ONLY", "execution_blocked": True, "metric_emission_blocked": True})
        else:
            entries.append({"operator_id": op, "vector_type": "VALID_METADATA_VECTOR", "expected_computation_status": "NOT_IMPLEMENTED", "execution_blocked": True, "metric_emission_blocked": True})
    return entries


def four_operator_default_operator_entries() -> list[dict[str, Any]]:
    shadow_operators = {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY"}
    all_operators = (
        "WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT",
        "HYPERVECTOR_BINDING", "RESERVOIR_STATE_SPACE", "COUNTERFACTUAL_DIFFUSION",
        "HEAVY_TAIL", "HYSTERESIS", "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
    )
    entries = []
    for op in all_operators:
        if op in shadow_operators:
            entries.append({"operator_id": op, "vector_type": "VALID_SHADOW_ONLY_VECTOR", "expected_computation_status": "SHADOW_STUB_ONLY", "execution_blocked": True, "metric_emission_blocked": True})
        elif op == "TRANSPORT":
            entries.append({"operator_id": op, "vector_type": "VALID_METADATA_VECTOR", "expected_computation_status": "NOT_IMPLEMENTED", "execution_blocked": True, "metric_emission_blocked": True, "cpu_baseline_planning_status": "CPU_BASELINE_PLANNING_COMPLETE"})
        else:
            entries.append({"operator_id": op, "vector_type": "VALID_METADATA_VECTOR", "expected_computation_status": "NOT_IMPLEMENTED", "execution_blocked": True, "metric_emission_blocked": True})
    return entries


def default_operator_entries() -> list[dict[str, Any]]:
    shadow_operators = {"WASSERSTEIN", "CHAMFER_DISTANCE"}
    all_operators = (
        "WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT",
        "HYPERVECTOR_BINDING", "RESERVOIR_STATE_SPACE", "COUNTERFACTUAL_DIFFUSION",
        "HEAVY_TAIL", "HYSTERESIS", "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
    )
    entries = []
    for op in all_operators:
        if op in shadow_operators:
            entries.append({
                "operator_id": op,
                "vector_type": "VALID_SHADOW_ONLY_VECTOR",
                "expected_computation_status": "SHADOW_STUB_ONLY",
                "execution_blocked": True,
                "metric_emission_blocked": True,
            })
        else:
            entries.append({
                "operator_id": op,
                "vector_type": "VALID_METADATA_VECTOR",
                "expected_computation_status": "NOT_IMPLEMENTED",
                "execution_blocked": True,
                "metric_emission_blocked": True,
            })
    return entries


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
            raise MetricOperatorRegistryStabilizationError(
                "forbidden_provenance_reference_detected"
            )


def validate_metric_operator_registry_stabilization(record: dict[str, Any]) -> None:
    required = {
        "schema_version", "stabilization_id", "title", "stabilization_status",
        "operator_entries", "source_refs", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - record.keys())
    if missing:
        raise MetricOperatorRegistryStabilizationError(f"missing_required_fields:{missing}")

    if record["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorRegistryStabilizationError("invalid_schema_version")

    if record["stabilization_status"] not in ALLOWED_STABILIZATION_STATUS:
        raise MetricOperatorRegistryStabilizationError(
            f"invalid_stabilization_status:{record['stabilization_status']}"
        )

    entries = record["operator_entries"]
    if not entries:
        raise MetricOperatorRegistryStabilizationError("operator_entries_must_be_non_empty")

    seen_ids: set[str] = set()
    for entry in entries:
        oid = entry.get("operator_id", "")
        if oid in seen_ids:
            raise MetricOperatorRegistryStabilizationError(f"duplicate_operator_id:{oid}")
        seen_ids.add(oid)
        if entry.get("vector_type") not in ALLOWED_VECTOR_TYPES:
            raise MetricOperatorRegistryStabilizationError(
                f"invalid_vector_type:{entry.get('vector_type')}"
            )
        if entry.get("expected_computation_status") not in ALLOWED_COMPUTATION_STATUS:
            raise MetricOperatorRegistryStabilizationError(
                f"invalid_expected_computation_status:{entry.get('expected_computation_status')}"
            )
        if entry.get("execution_blocked") is not True:
            raise MetricOperatorRegistryStabilizationError(
                f"execution_blocked_must_be_true:{oid}"
            )
        if entry.get("metric_emission_blocked") is not True:
            raise MetricOperatorRegistryStabilizationError(
                f"metric_emission_blocked_must_be_true:{oid}"
            )

    if record["output_contract"] != default_output_contract():
        raise MetricOperatorRegistryStabilizationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if record["governance_flags"].get(flag) is not False:
            raise MetricOperatorRegistryStabilizationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(record["provenance"])


def compute_metric_operator_registry_stabilization_hash(record: dict[str, Any]) -> str:
    return canonical_hash(_preimage(record))


def serialize_metric_operator_registry_stabilization(record: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(record)) + "\n"


def build_metric_operator_registry_stabilization(payload: dict[str, Any]) -> dict[str, Any]:
    entries = sorted(
        payload.get("operator_entries", []),
        key=lambda e: e["operator_id"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "operator_entries": entries,
        "source_refs": sorted(payload.get("source_refs", [])),
    }
    base["canonical_hash"] = compute_metric_operator_registry_stabilization_hash(base)
    validate_metric_operator_registry_stabilization(base)
    return _finalize(base)
