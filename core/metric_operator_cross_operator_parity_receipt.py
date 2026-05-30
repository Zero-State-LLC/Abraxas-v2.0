from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorCrossOperatorParityReceipt.v1"

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

ALLOWED_PARITY_STATUS = ("PARITY_CONFIRMED", "PARITY_NOT_CONFIRMED", "PARITY_PARTIAL")

FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-value",
)


class MetricOperatorCrossOperatorParityReceiptError(ValueError):
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
        "emits_parity_receipt": True,
    }


def default_governance_flags() -> dict[str, bool]:
    return {flag: False for flag in LOCKED_FALSE_FLAGS}


def three_operator_default_parity_dimensions() -> list[dict[str, Any]]:
    ops = {"WASSERSTEIN": "VALID_SHADOW_ONLY_VECTOR", "CHAMFER_DISTANCE": "VALID_SHADOW_ONLY_VECTOR", "GEODESIC": "VALID_SHADOW_ONLY_VECTOR"}
    return [
        {"dimension_id": "dim-001-vector-type", "dimension_name": "baseline_vector_type", "observed_values": {k: ops[k] for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-002-computation-status", "dimension_name": "expected_computation_status", "observed_values": {k: "SHADOW_STUB_ONLY" for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-003-shadow-posture", "dimension_name": "shadow_only_posture", "observed_values": {k: "SHADOW_LANE_ONLY" for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-004-expected-values-completion", "dimension_name": "expected_values_chain_complete", "observed_values": {k: "COMPLETE" for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-005-metric-emission", "dimension_name": "metric_emission_blocked", "observed_values": {k: "BLOCKED" for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-006-forecast-influence", "dimension_name": "forecast_influence_blocked", "observed_values": {k: "BLOCKED" for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-007-p43-surface-lanes", "dimension_name": "p43_surface_lanes_blocked", "observed_values": {k: "BLOCKED" for k in sorted(ops)}, "parity_confirmed": True},
        {"dimension_id": "dim-008-computation-phase", "dimension_name": "computation_phase_closed", "observed_values": {k: "CLOSED" for k in sorted(ops)}, "parity_confirmed": True},
    ]


def default_parity_dimensions() -> list[dict[str, Any]]:
    return [
        {
            "dimension_id": "dim-001-vector-type",
            "dimension_name": "baseline_vector_type",
            "observed_values": {
                "WASSERSTEIN": "VALID_SHADOW_ONLY_VECTOR",
                "CHAMFER_DISTANCE": "VALID_SHADOW_ONLY_VECTOR",
            },
            "parity_confirmed": True,
        },
        {
            "dimension_id": "dim-002-computation-status",
            "dimension_name": "expected_computation_status",
            "observed_values": {
                "WASSERSTEIN": "SHADOW_STUB_ONLY",
                "CHAMFER_DISTANCE": "SHADOW_STUB_ONLY",
            },
            "parity_confirmed": True,
        },
        {
            "dimension_id": "dim-003-shadow-posture",
            "dimension_name": "shadow_only_posture",
            "observed_values": {
                "WASSERSTEIN": "SHADOW_LANE_ONLY",
                "CHAMFER_DISTANCE": "SHADOW_LANE_ONLY",
            },
            "parity_confirmed": True,
        },
        {
            "dimension_id": "dim-004-expected-values-completion",
            "dimension_name": "expected_values_chain_complete",
            "observed_values": {
                "WASSERSTEIN": "COMPLETE",
                "CHAMFER_DISTANCE": "COMPLETE",
            },
            "parity_confirmed": True,
        },
        {
            "dimension_id": "dim-005-metric-emission",
            "dimension_name": "metric_emission_blocked",
            "observed_values": {
                "WASSERSTEIN": "BLOCKED",
                "CHAMFER_DISTANCE": "BLOCKED",
            },
            "parity_confirmed": True,
        },
        {
            "dimension_id": "dim-006-forecast-influence",
            "dimension_name": "forecast_influence_blocked",
            "observed_values": {
                "WASSERSTEIN": "BLOCKED",
                "CHAMFER_DISTANCE": "BLOCKED",
            },
            "parity_confirmed": True,
        },
        {
            "dimension_id": "dim-007-p43-surface-lanes",
            "dimension_name": "p43_surface_lanes_blocked",
            "observed_values": {
                "WASSERSTEIN": "BLOCKED",
                "CHAMFER_DISTANCE": "BLOCKED",
            },
            "parity_confirmed": True,
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
            raise MetricOperatorCrossOperatorParityReceiptError(
                "forbidden_provenance_reference_detected"
            )


def validate_metric_operator_cross_operator_parity_receipt(receipt: dict[str, Any]) -> None:
    required = {
        "schema_version", "receipt_id", "parity_status", "operators_compared",
        "parity_dimensions", "output_contract", "governance_flags",
        "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - receipt.keys())
    if missing:
        raise MetricOperatorCrossOperatorParityReceiptError(f"missing_required_fields:{missing}")

    if receipt["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorCrossOperatorParityReceiptError("invalid_schema_version")

    if receipt["parity_status"] not in ALLOWED_PARITY_STATUS:
        raise MetricOperatorCrossOperatorParityReceiptError(
            f"invalid_parity_status:{receipt['parity_status']}"
        )

    operators = receipt["operators_compared"]
    if len(operators) < 2:
        raise MetricOperatorCrossOperatorParityReceiptError("operators_compared_must_have_at_least_2")

    dimensions = receipt["parity_dimensions"]
    if not dimensions:
        raise MetricOperatorCrossOperatorParityReceiptError("parity_dimensions_must_be_non_empty")

    dim_ids: set[str] = set()
    for dim in dimensions:
        did = dim.get("dimension_id", "")
        if did in dim_ids:
            raise MetricOperatorCrossOperatorParityReceiptError(f"duplicate_dimension_id:{did}")
        dim_ids.add(did)

    all_confirmed = all(dim.get("parity_confirmed") is True for dim in dimensions)
    if receipt["parity_status"] == "PARITY_CONFIRMED" and not all_confirmed:
        raise MetricOperatorCrossOperatorParityReceiptError(
            "parity_status_confirmed_but_not_all_dimensions_confirmed"
        )

    if receipt["output_contract"] != default_output_contract():
        raise MetricOperatorCrossOperatorParityReceiptError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if receipt["governance_flags"].get(flag) is not False:
            raise MetricOperatorCrossOperatorParityReceiptError(
                f"authority_lock_must_be_false:{flag}"
            )

    _assert_provenance_safe(receipt["provenance"])


def compute_metric_operator_cross_operator_parity_receipt_hash(receipt: dict[str, Any]) -> str:
    return canonical_hash(_preimage(receipt))


def serialize_metric_operator_cross_operator_parity_receipt(receipt: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(receipt)) + "\n"


def build_metric_operator_cross_operator_parity_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    dims = sorted(
        payload.get("parity_dimensions", []),
        key=lambda d: d["dimension_id"],
    )
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "operators_compared": sorted(payload.get("operators_compared", [])),
        "parity_dimensions": dims,
    }
    base["canonical_hash"] = compute_metric_operator_cross_operator_parity_receipt_hash(base)
    validate_metric_operator_cross_operator_parity_receipt(base)
    return _finalize(base)
