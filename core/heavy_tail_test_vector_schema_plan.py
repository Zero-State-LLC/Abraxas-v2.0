from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "HeavyTailTestVectorSchemaPlan.v1"
PLAN_TYPE = "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN"
PLAN_STATUS = "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN_COMPLETE"
OPERATOR_ID = "HEAVY_TAIL"

SOURCE_AUTH_ARTIFACT_ID = "heavy_tail_shadow_stub_implementation_authorization_001"
SOURCE_AUTH_SCHEMA_TYPE = "HeavyTailShadowStubImplementationAuthorization.v1"
SOURCE_AUTH_HASH = (
    "988ed40a766a2fb5edf82bd33a0cdcf5540a4a38486bc36b180802b7ef7e2834"
)

ALLOWED_SCHEMA_FAMILY = (
    "MIXED_SCHEMA_PLAN",
    "VALID_ONLY_SCHEMA_PLAN",
    "INVALID_ONLY_SCHEMA_PLAN",
)
ALLOWED_INTENDED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_SCHEMA_STAGE = ("SCHEMA_PLAN_ONLY", "SCHEMA_DEFINITION_READY", "FIXTURE_READY")
ALLOWED_IMPLEMENTATION_STATUS = (
    "PLANNED_ONLY",
    "NOT_IMPLEMENTED",
    "BLOCKED_PENDING_REVIEW",
)

LOCKED_TRUE_FLAGS = (
    "advisory_only",
    "shadow_lane_only",
    "schema_plan_only",
    "heavy_tail_schema_defined",
)
LOCKED_FALSE_FLAGS = (
    "fixture_files_created",
    "computation_executed",
    "baseline_pack_updated",
    "emits_metric_values",
    "forecast_influence",
    "p43_surface_lanes_authorized",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
    "inference_authority",
)
FORBIDDEN = (
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class HeavyTailTestVectorSchemaPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise HeavyTailTestVectorSchemaPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def default_source_authorization_binding() -> dict[str, Any]:
    return {
        "authorization_artifact_id": SOURCE_AUTH_ARTIFACT_ID,
        "authorization_schema_type": SOURCE_AUTH_SCHEMA_TYPE,
        "authorization_canonical_hash": SOURCE_AUTH_HASH,
        "hash_confirmed": True,
        "implementation_authorized_acknowledged": True,
        "fixture_creation_authorized_acknowledged": True,
        "fixture_corpus_not_created_in_this_plan": True,
        "baseline_pack_update_authorized_acknowledged": True,
        "baseline_pack_not_updated_in_this_plan": True,
        "computation_not_performed": True,
        "metric_values_not_emitted": True,
        "forecast_influence_not_enabled": True,
        "p43_lanes_not_opened": True,
        "runtime_not_mutated": True,
        "production_not_activated": True,
        "canon_not_promoted": True,
        "execution_authority_not_granted": True,
    }


def default_schema_field_definition() -> dict[str, Any]:
    return {
        "alpha": {
            "type": "number",
            "description": (
                "Positive shape exponent for power-law tail classification. "
                "Fixture-only: bounded to (0.0, 5.0] for plan-time determinism."
            ),
            "fixture_allowed_range": [1.01, 5.0],
            "semantics": "SHAPE_EXPONENT",
        },
        "sample_count": {
            "type": "integer",
            "description": (
                "Number of values in sequence_values. "
                "Must equal len(sequence_values). Fixture bounded to [1, 1000]."
            ),
            "fixture_allowed_range": [1, 1000],
            "semantics": "SEQUENCE_LENGTH",
        },
        "expected_tail_threshold": {
            "type": "number",
            "description": (
                "Deterministic threshold distinguishing heavy-tail from light-tail behavior. "
                "Declared by fixture; not computed at plan stage. Bounded to (0.0, 10.0]."
            ),
            "fixture_allowed_range": [0.5, 10.0],
            "semantics": "CLASSIFICATION_THRESHOLD",
        },
        "sequence_values": {
            "type": "array",
            "item_type": "integer",
            "description": (
                "Bounded non-negative integer sequence. "
                "Fixture-declared; analytically derived from alpha and sample_count. "
                "No non-finite or negative elements."
            ),
            "semantics": "INPUT_SEQUENCE",
        },
        "expected_tail_index": {
            "type": "number",
            "description": (
                "Fixture-declared expected tail index. "
                "Derived analytically from alpha and closed-form rank-frequency statistics. "
                "Not computed at plan stage."
            ),
            "semantics": "EXPECTED_TAIL_CLASSIFICATION",
        },
        "expected_moment_summary": {
            "type": "object",
            "description": (
                "Closed-form or fixture-declared moment metadata: "
                "mean, variance, skewness, kurtosis (where finite). "
                "Not computed at plan stage."
            ),
            "semantics": "MOMENT_METADATA",
        },
        "expected_status": {
            "type": "string",
            "enum": ["COMPUTABLE", "INVALID_INPUT", "NOT_COMPUTABLE"],
            "description": "Expected computation status for this fixture case.",
            "semantics": "OUTCOME_STATUS",
        },
        "expected_outcome_reason": {
            "type": "string",
            "description": "Deterministic reason enum for expected_status outcome.",
            "semantics": "OUTCOME_REASON",
            "example_values": [
                "POWER_LAW_HEAVY_TAIL_DETECTED",
                "LIGHT_TAIL_CONTROL",
                "SINGLE_OUTLIER_DOMINATED",
                "MONOTONE_RANK_FREQUENCY",
                "REPEATED_EQUAL_VALUES",
                "MISSING_REQUIRED_FIELD",
                "INVALID_STATUS_VALUE",
                "ALPHA_NOT_POSITIVE",
                "ZERO_SAMPLE_COUNT",
                "EMPTY_SEQUENCE",
                "NON_FINITE_VALUE",
                "NEGATIVE_VALUE",
                "SAMPLE_COUNT_MISMATCH",
            ],
        },
    }


def default_parameter_bound_policy() -> dict[str, Any]:
    return {
        "alpha": {
            "min_exclusive": 0.0,
            "max_inclusive": 5.0,
            "fixture_only": True,
            "note": "alpha must be strictly positive; fixture alpha bounded to (0.0, 5.0]",
        },
        "sample_count": {
            "min_inclusive": 1,
            "max_inclusive": 1000,
            "fixture_only": True,
            "note": "positive integer; fixture bounded to [1, 1000]",
        },
        "expected_tail_threshold": {
            "min_exclusive": 0.0,
            "max_inclusive": 10.0,
            "fixture_only": True,
            "note": "positive real; fixture bounded to (0.0, 10.0]",
        },
        "sequence_values_elements": {
            "min_inclusive": 0,
            "fixture_only": True,
            "note": "non-negative integers only; no non-finite values",
        },
        "sample_count_must_equal_len_sequence_values": True,
    }


def default_valid_fixture_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "valid-ht-001",
            "group_label": "bounded_power_law_alpha_2",
            "description": (
                "Power-law sequence with alpha=2.0; 20 bounded non-negative integer values "
                "with rank-frequency slope consistent with heavy-tail classification. "
                "Expected status: COMPUTABLE."
            ),
            "expected_input_contract": {
                "alpha": 2.0,
                "sample_count": 20,
                "expected_tail_threshold": 1.5,
                "sequence_values_schema": "bounded_integer_power_law_alpha_2_n20",
                "expected_status": "COMPUTABLE",
                "expected_tail_index_schema": "power_law_rank_slope_alpha_2",
                "expected_moment_summary_schema": "closed_form_power_law_moments_alpha_2",
                "expected_outcome_reason": "POWER_LAW_HEAVY_TAIL_DETECTED",
            },
            "blocked_operations": ["heavy_tail_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-ht-002",
            "group_label": "bounded_power_law_alpha_3",
            "description": (
                "Power-law sequence with alpha=3.0; 20 bounded non-negative integer values; "
                "steeper slope than alpha=2 but still classifies as heavy-tail. "
                "Expected status: COMPUTABLE."
            ),
            "expected_input_contract": {
                "alpha": 3.0,
                "sample_count": 20,
                "expected_tail_threshold": 1.5,
                "sequence_values_schema": "bounded_integer_power_law_alpha_3_n20",
                "expected_status": "COMPUTABLE",
                "expected_tail_index_schema": "power_law_rank_slope_alpha_3",
                "expected_moment_summary_schema": "closed_form_power_law_moments_alpha_3",
                "expected_outcome_reason": "POWER_LAW_HEAVY_TAIL_DETECTED",
            },
            "blocked_operations": ["heavy_tail_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-ht-003",
            "group_label": "light_tail_control_sequence",
            "description": (
                "Exponentially decaying sequence (alpha=5.0, thin tail); "
                "tail index falls below threshold; serves as light-tail control case. "
                "Expected status: COMPUTABLE with LIGHT_TAIL_CONTROL outcome."
            ),
            "expected_input_contract": {
                "alpha": 5.0,
                "sample_count": 20,
                "expected_tail_threshold": 1.5,
                "sequence_values_schema": "bounded_integer_exponential_decay_n20",
                "expected_status": "COMPUTABLE",
                "expected_tail_index_schema": "light_tail_below_threshold",
                "expected_moment_summary_schema": "closed_form_thin_tail_moments",
                "expected_outcome_reason": "LIGHT_TAIL_CONTROL",
            },
            "blocked_operations": ["heavy_tail_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-ht-004",
            "group_label": "single_large_outlier_sequence",
            "description": (
                "Sequence of mostly equal values with one extreme outlier; "
                "outlier dominates tail classification; "
                "closed-form moments analytically tractable. "
                "Expected status: COMPUTABLE with SINGLE_OUTLIER_DOMINATED outcome."
            ),
            "expected_input_contract": {
                "alpha": 2.0,
                "sample_count": 20,
                "expected_tail_threshold": 1.5,
                "sequence_values_schema": "bounded_integer_single_outlier_n20",
                "expected_status": "COMPUTABLE",
                "expected_tail_index_schema": "outlier_dominated_tail_index",
                "expected_moment_summary_schema": "closed_form_outlier_moments",
                "expected_outcome_reason": "SINGLE_OUTLIER_DOMINATED",
            },
            "blocked_operations": ["heavy_tail_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-ht-005",
            "group_label": "monotone_rank_frequency_sequence",
            "description": (
                "Strictly monotone decreasing rank-frequency sequence; "
                "slope analytically bounded; "
                "rank-frequency slope provides clean tail index estimate. "
                "Expected status: COMPUTABLE with MONOTONE_RANK_FREQUENCY outcome."
            ),
            "expected_input_contract": {
                "alpha": 2.0,
                "sample_count": 20,
                "expected_tail_threshold": 1.5,
                "sequence_values_schema": "bounded_integer_strictly_monotone_n20",
                "expected_status": "COMPUTABLE",
                "expected_tail_index_schema": "monotone_rank_frequency_slope",
                "expected_moment_summary_schema": "closed_form_monotone_moments",
                "expected_outcome_reason": "MONOTONE_RANK_FREQUENCY",
            },
            "blocked_operations": ["heavy_tail_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-ht-006",
            "group_label": "repeated_equal_values_control",
            "description": (
                "All sequence values are equal; degenerate flat rank-frequency distribution; "
                "tail index is analytically zero (flat slope); "
                "tests boundary case for classification. "
                "Expected status: COMPUTABLE with REPEATED_EQUAL_VALUES outcome."
            ),
            "expected_input_contract": {
                "alpha": 2.0,
                "sample_count": 20,
                "expected_tail_threshold": 1.5,
                "sequence_values_schema": "bounded_integer_all_equal_n20",
                "expected_status": "COMPUTABLE",
                "expected_tail_index_schema": "degenerate_flat_rank_frequency",
                "expected_moment_summary_schema": "closed_form_equal_values_moments",
                "expected_outcome_reason": "REPEATED_EQUAL_VALUES",
            },
            "blocked_operations": ["heavy_tail_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_fixture_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "invalid-ht-001",
            "group_label": "missing_alpha",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "alpha",
            "expected_failure": "validation_error_missing_alpha",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-ht-002",
            "group_label": "missing_sample_count",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "sample_count",
            "expected_failure": "validation_error_missing_sample_count",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-ht-003",
            "group_label": "missing_sequence_values",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "sequence_values",
            "expected_failure": "validation_error_missing_sequence_values",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-ht-004",
            "group_label": "invalid_expected_status",
            "invalid_reason": "INVALID_FIELD_VALUE",
            "target_field": "expected_status",
            "expected_failure": "validation_error_invalid_expected_status",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "nc-ht-001",
            "group_label": "alpha_lte_zero",
            "not_computable_reason": "ALPHA_NOT_POSITIVE",
            "description": (
                "alpha <= 0; power-law shape exponent must be strictly positive; "
                "yields NOT_COMPUTABLE without any computation attempt."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-ht-002",
            "group_label": "sample_count_zero",
            "not_computable_reason": "ZERO_SAMPLE_COUNT",
            "description": (
                "sample_count = 0; no elements to classify; "
                "yields NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-ht-003",
            "group_label": "empty_sequence",
            "not_computable_reason": "EMPTY_SEQUENCE",
            "description": (
                "sequence_values is an empty list; no tail structure to analyze; "
                "yields NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-ht-004",
            "group_label": "non_finite_sequence_value",
            "not_computable_reason": "NON_FINITE_VALUE",
            "description": (
                "sequence_values contains a non-finite element (infinity or NaN); "
                "tail analysis requires finite non-negative integer values; "
                "yields NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-ht-005",
            "group_label": "negative_sequence_value",
            "not_computable_reason": "NEGATIVE_VALUE",
            "description": (
                "sequence_values contains a negative element; "
                "power-law tail analysis requires non-negative integer values; "
                "yields NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-ht-006",
            "group_label": "sample_count_mismatch",
            "not_computable_reason": "SAMPLE_COUNT_MISMATCH",
            "description": (
                "sample_count does not equal len(sequence_values); "
                "structural contract violation; yields NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_closed_form_derivation_policy() -> dict[str, Any]:
    return {
        "policy": "FIXTURE_DECLARED_CLOSED_FORM",
        "derivation_method": "ANALYTICALLY_BOUNDED_INTEGER_SEQUENCE",
        "closed_form_moments_available": True,
        "computation_in_plan": False,
        "fixture_values_analytically_derived": True,
        "derivation_authority": "FIXTURE_AUTHOR",
        "plan_stage_computation_allowed": False,
        "notes": (
            "All expected values are declared by fixture authors using analytically "
            "bounded integer sequences with closed-form power-law statistics. "
            "No computation is executed at schema plan stage. "
            "Actual computation will occur in the computation receipt phase "
            "(shadow stub only, no metric emission)."
        ),
    }


def default_fixture_corpus_strategy() -> dict[str, Any]:
    return {
        "strategy": "ANALYTICALLY_BOUNDED_INTEGER_SEQUENCES_WITH_CLOSED_FORM_MOMENTS",
        "fixture_creation_authorized": True,
        "fixture_corpus_created_in_this_plan": False,
        "valid_fixture_count_planned": 6,
        "invalid_fixture_count_planned": 4,
        "not_computable_fixture_count_planned": 6,
        "total_fixture_count_planned": 16,
        "schema_fields_covered": [
            "alpha",
            "sample_count",
            "expected_tail_threshold",
            "sequence_values",
            "expected_tail_index",
            "expected_moment_summary",
            "expected_status",
            "expected_outcome_reason",
        ],
        "shadow_stub_only": True,
        "metric_emission_in_fixture_corpus": False,
        "recommended_next_artifact": "heavy_tail_fixture_corpus_creation_plan_001",
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "schema_plan_only": True,
        "heavy_tail_schema_defined": True,
        "fixture_files_created": False,
        "computation_executed": False,
        "baseline_pack_updated": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_blocked_scope_review() -> dict[str, Any]:
    return {
        "fixture_corpus_creation": "AUTHORIZED_BUT_NOT_IN_THIS_PLAN",
        "baseline_pack_update": "AUTHORIZED_BUT_NOT_IN_THIS_PLAN",
        "computation": "BLOCKED",
        "metric_emission": "BLOCKED",
        "forecast_influence": "BLOCKED",
        "p43_lanes": "BLOCKED",
        "runtime_mutation": "BLOCKED",
        "production_activation": "BLOCKED",
        "canon_promotion": "BLOCKED",
        "execution_authority": "BLOCKED",
        "inference_authority": "BLOCKED",
        "confirmed": True,
        "all_blocked_scopes_correct": True,
    }


def validate_heavy_tail_test_vector_schema_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "plan_status", "operator_id",
        "source_authorization_binding", "schema_field_definition", "parameter_bound_policy",
        "valid_fixture_schema_groups", "invalid_fixture_schema_groups",
        "not_computable_schema_groups", "closed_form_derivation_policy",
        "fixture_corpus_strategy", "authority_lock_review", "blocked_scope_review",
        "recommended_next_step", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise HeavyTailTestVectorSchemaPlanValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise HeavyTailTestVectorSchemaPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise HeavyTailTestVectorSchemaPlanValidationError("invalid_plan_type")
    if packet["plan_status"] != PLAN_STATUS:
        raise HeavyTailTestVectorSchemaPlanValidationError("invalid_plan_status")
    if packet["operator_id"] != OPERATOR_ID:
        raise HeavyTailTestVectorSchemaPlanValidationError("unknown_operator_id")

    auth_binding = packet["source_authorization_binding"]
    if auth_binding.get("authorization_canonical_hash") != SOURCE_AUTH_HASH:
        raise HeavyTailTestVectorSchemaPlanValidationError(
            "authorization_hash_mismatch"
        )
    if auth_binding.get("hash_confirmed") is not True:
        raise HeavyTailTestVectorSchemaPlanValidationError(
            "authorization_hash_not_confirmed"
        )

    for list_key, label in (
        ("valid_fixture_schema_groups", "valid_fixture_schema_groups_must_be_non_empty"),
        ("invalid_fixture_schema_groups", "invalid_fixture_schema_groups_must_be_non_empty"),
        ("not_computable_schema_groups", "not_computable_schema_groups_must_be_non_empty"),
    ):
        if not packet.get(list_key):
            raise HeavyTailTestVectorSchemaPlanValidationError(label)

    for group_list in (
        packet["valid_fixture_schema_groups"],
        packet["invalid_fixture_schema_groups"],
        packet["not_computable_schema_groups"],
    ):
        seen_ids: set[str] = set()
        for g in group_list:
            gid = g.get("group_id")
            if gid in seen_ids:
                raise HeavyTailTestVectorSchemaPlanValidationError("duplicate_group_id")
            seen_ids.add(gid)
            if g.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
                raise HeavyTailTestVectorSchemaPlanValidationError(
                    "unknown_implementation_status"
                )

    auth_lock = packet["authority_lock_review"]
    for flag in LOCKED_TRUE_FLAGS:
        if auth_lock.get(flag) is not True:
            raise HeavyTailTestVectorSchemaPlanValidationError(
                f"authority_lock_must_be_true:{flag}"
            )
    for flag in LOCKED_FALSE_FLAGS:
        if auth_lock.get(flag) is not False:
            raise HeavyTailTestVectorSchemaPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )

    _prov_safe(packet["provenance"])


def compute_heavy_tail_test_vector_schema_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_heavy_tail_test_vector_schema_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_heavy_tail_test_vector_schema_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "plan_status": PLAN_STATUS,
        "operator_id": OPERATOR_ID,
        "source_authorization_binding": payload.get(
            "source_authorization_binding", default_source_authorization_binding()
        ),
        "schema_field_definition": payload.get(
            "schema_field_definition", default_schema_field_definition()
        ),
        "parameter_bound_policy": payload.get(
            "parameter_bound_policy", default_parameter_bound_policy()
        ),
        "valid_fixture_schema_groups": sorted(
            payload.get(
                "valid_fixture_schema_groups", default_valid_fixture_schema_groups()
            ),
            key=lambda x: x["group_id"],
        ),
        "invalid_fixture_schema_groups": sorted(
            payload.get(
                "invalid_fixture_schema_groups", default_invalid_fixture_schema_groups()
            ),
            key=lambda x: x["group_id"],
        ),
        "not_computable_schema_groups": sorted(
            payload.get(
                "not_computable_schema_groups", default_not_computable_schema_groups()
            ),
            key=lambda x: x["group_id"],
        ),
        "closed_form_derivation_policy": payload.get(
            "closed_form_derivation_policy", default_closed_form_derivation_policy()
        ),
        "fixture_corpus_strategy": payload.get(
            "fixture_corpus_strategy", default_fixture_corpus_strategy()
        ),
        "authority_lock_review": payload.get(
            "authority_lock_review", default_authority_lock_review()
        ),
        "blocked_scope_review": payload.get(
            "blocked_scope_review", default_blocked_scope_review()
        ),
        "recommended_next_step": payload.get(
            "recommended_next_step", "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN"
        ),
    }
    base["canonical_hash"] = compute_heavy_tail_test_vector_schema_plan_hash(base)
    validate_heavy_tail_test_vector_schema_plan(base)
    return _finalize(base)
