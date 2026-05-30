from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportImplementationAuthorizationDecisionRecord.v1"
RECORD_STATUS = "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORDED"

EXPECTED_DECISION = "approve_transport_shadow_computation_implementation"
EXPECTED_LANE = "TEST_VECTOR_COMPUTATION_ONLY"
EXPECTED_BASELINE = "SHADOW_STUB_ONLY"

REQUIRED_LOCKED_CONSTANT_KEYS = (
    "lp_solver_variant_declaration",
    "pivot_rule_declaration",
    "tie_breaking_rule_declaration",
    "balance_tolerance_declaration",
    "max_problem_size_declaration",
    "cost_matrix_magnitude_bound_declaration",
    "not_computable_branch_enumeration_confirmation",
)

REQUIRED_ACKNOWLEDGEMENT_KEYS = (
    "shadow_lane_only_acknowledged",
    "test_vector_computation_only_acknowledged",
    "lp_solver_invocation_limited_to_test_vector_scope_acknowledged",
    "metric_values_emission_blocked_acknowledged",
    "forecast_influence_blocked_acknowledged",
    "p43_surface_lanes_blocked_acknowledged",
    "production_activation_blocked_acknowledged",
    "canon_promotion_blocked_acknowledged",
    "runtime_mutation_blocked_acknowledged",
    "execution_authority_blocked_acknowledged",
)

AUTHORITY_FALSE_KEYS = (
    "valid_for_execution",
    "authorization_granted",
    "emits_metric_values",
    "forecast_authority",
    "inference_authority",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
)

FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-value",
)


class TransportImplementationAuthorizationDecisionRecordError(ValueError):
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
        "emits_decision_record": True,
        "emits_authority_tokens": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "decision_record_only": True,
        "implementation_lane_authorized": EXPECTED_LANE,
        "transport_computation_implementation_authorized": False,
        "lp_solver_invocation_authorized_for_test_vectors": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_blocked_scopes() -> list[str]:
    return [
        "METRIC_EMISSION",
        "FORECAST_INFLUENCE",
        "P43_SURFACE_LANES",
        "PRODUCTION_ACTIVATION",
        "CANON_PROMOTION",
        "RUNTIME_MUTATION",
        "EXECUTION_AUTHORITY",
        "LP_SOLVER_INVOCATION_OUTSIDE_TEST_VECTOR_SCOPE",
    ]


def _build_locked_constants_record(locked_constants: dict[str, Any]) -> dict[str, Any]:
    all_present = all(k in locked_constants for k in REQUIRED_LOCKED_CONSTANT_KEYS)
    rec: dict[str, Any] = {}
    for key in REQUIRED_LOCKED_CONSTANT_KEYS:
        rec[key] = locked_constants.get(key)
    rec["all_locked_constants_present"] = all_present
    rec["constants_valid_for_test_vector_scope"] = all_present
    return rec


def _build_decision_validation_review(decision_data: dict[str, Any]) -> dict[str, Any]:
    decision_match = decision_data.get("decision") == EXPECTED_DECISION
    lane_match = decision_data.get("implementation_lane_authorized") == EXPECTED_LANE
    baseline_match = decision_data.get("baseline_target") == EXPECTED_BASELINE
    authority_flags_false = all(
        decision_data.get(k) is False for k in AUTHORITY_FALSE_KEYS
    )
    return {
        "decision_match": decision_match,
        "implementation_lane_match": lane_match,
        "baseline_target_match": baseline_match,
        "all_authority_flags_false": authority_flags_false,
        "decision_valid": (
            decision_match and lane_match and baseline_match and authority_flags_false
        ),
    }


def _build_blocked_scope_acknowledgement_review(
    decision_data: dict[str, Any],
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for key in REQUIRED_ACKNOWLEDGEMENT_KEYS:
        results[key] = decision_data.get(key) is True
    all_confirmed = all(results[k] for k in REQUIRED_ACKNOWLEDGEMENT_KEYS)
    results["all_acknowledgements_confirmed"] = all_confirmed
    return results


def _build_implementation_gate_prerequisite_review() -> dict[str, Any]:
    return {
        "four_operator_shadow_stub_parity_confirmed": True,
        "parity_receipt_ref": (
            "MetricOperatorCrossOperatorParityReceipt.v1"
            ":metric_operator_cross_operator_parity_receipt_003"
        ),
        "transport_selection_complete": True,
        "transport_readiness_dossier_complete": True,
        "transport_cpu_baseline_planning_complete": True,
        "operator_decision_file_present": True,
        "seven_locked_constants_declared": True,
        "prerequisites_met": True,
    }


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
            raise TransportImplementationAuthorizationDecisionRecordError(
                "forbidden_provenance_reference_detected"
            )


def validate_transport_implementation_authorization_decision_record(
    record: dict[str, Any],
) -> None:
    required = (
        "schema_version", "record_id", "operator_id", "source_operator_decision_hash",
        "decision_id", "implementation_lane_authorized", "baseline_target", "record_status",
        "locked_constants_record", "decision_validation_review",
        "blocked_scope_acknowledgement_review", "implementation_gate_prerequisite_review",
        "authority_locks", "blocked_scopes", "recommended_next_step",
        "output_contract", "provenance", "created_at_utc", "canonical_hash",
    )
    for field in required:
        if field not in record:
            raise TransportImplementationAuthorizationDecisionRecordError(
                f"missing_required_field:{field}"
            )
    if record.get("schema_version") != SCHEMA_VERSION:
        raise TransportImplementationAuthorizationDecisionRecordError(
            f"schema_version_mismatch:{record.get('schema_version')!r}"
        )
    if record.get("operator_id") != "TRANSPORT":
        raise TransportImplementationAuthorizationDecisionRecordError(
            f"operator_id_mismatch:{record.get('operator_id')!r}"
        )
    if record.get("implementation_lane_authorized") != EXPECTED_LANE:
        raise TransportImplementationAuthorizationDecisionRecordError(
            f"implementation_lane_mismatch:{record.get('implementation_lane_authorized')!r}"
        )
    if record.get("record_status") != RECORD_STATUS:
        raise TransportImplementationAuthorizationDecisionRecordError(
            f"record_status_mismatch:{record.get('record_status')!r}"
        )
    locks = record.get("authority_locks", {})
    for lock_key in (
        "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(lock_key) is not False:
            raise TransportImplementationAuthorizationDecisionRecordError(
                f"authority_lock_must_be_false:{lock_key}"
            )
    for true_key in ("advisory_only", "shadow_lane_only", "decision_record_only"):
        if locks.get(true_key) is not True:
            raise TransportImplementationAuthorizationDecisionRecordError(
                f"authority_lock_must_be_true:{true_key}"
            )
    lcr = record.get("locked_constants_record", {})
    if lcr.get("all_locked_constants_present") is not True:
        raise TransportImplementationAuthorizationDecisionRecordError(
            "locked_constants_not_all_present"
        )
    if lcr.get("constants_valid_for_test_vector_scope") is not True:
        raise TransportImplementationAuthorizationDecisionRecordError(
            "constants_not_valid_for_test_vector_scope"
        )
    dvr = record.get("decision_validation_review", {})
    if dvr.get("decision_valid") is not True:
        raise TransportImplementationAuthorizationDecisionRecordError(
            "decision_validation_failed"
        )
    bsar = record.get("blocked_scope_acknowledgement_review", {})
    if bsar.get("all_acknowledgements_confirmed") is not True:
        raise TransportImplementationAuthorizationDecisionRecordError(
            "blocked_scope_acknowledgements_not_confirmed"
        )
    prereqs = record.get("implementation_gate_prerequisite_review", {})
    if prereqs.get("prerequisites_met") is not True:
        raise TransportImplementationAuthorizationDecisionRecordError(
            "implementation_gate_prerequisites_not_met"
        )
    _assert_provenance_safe(record.get("provenance"))
    h = record.get("canonical_hash", "")
    if not (isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h)):
        raise TransportImplementationAuthorizationDecisionRecordError(
            "canonical_hash_invalid"
        )


def compute_transport_implementation_authorization_decision_record_hash(
    record: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(record))


def serialize_transport_implementation_authorization_decision_record(
    record: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(record)) + "\n"


def build_transport_implementation_authorization_decision_record(
    payload: dict[str, Any],
) -> dict[str, Any]:
    _assert_provenance_safe(payload.get("provenance"))
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_id": payload["record_id"],
        "operator_id": "TRANSPORT",
        "source_operator_decision_hash": payload["source_operator_decision_hash"],
        "decision_id": payload["decision_id"],
        "implementation_lane_authorized": EXPECTED_LANE,
        "baseline_target": EXPECTED_BASELINE,
        "record_status": RECORD_STATUS,
        "locked_constants_record": payload["locked_constants_record"],
        "decision_validation_review": payload["decision_validation_review"],
        "blocked_scope_acknowledgement_review": payload[
            "blocked_scope_acknowledgement_review"
        ],
        "implementation_gate_prerequisite_review": payload[
            "implementation_gate_prerequisite_review"
        ],
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
        "recommended_next_step": payload["recommended_next_step"],
        "output_contract": payload.get("output_contract", default_output_contract()),
        "provenance": payload["provenance"],
        "created_at_utc": payload["created_at_utc"],
    }
    base["canonical_hash"] = compute_transport_implementation_authorization_decision_record_hash(
        base
    )
    validate_transport_implementation_authorization_decision_record(base)
    return _finalize(base)
