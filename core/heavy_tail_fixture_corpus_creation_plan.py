from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "HeavyTailFixtureCorpusCreationPlan.v1"
PLAN_TYPE = "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN"
PLAN_STATUS = "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN_COMPLETE"
OPERATOR_ID = "HEAVY_TAIL"

SOURCE_AUTH_ARTIFACT_ID = "heavy_tail_shadow_stub_implementation_authorization_001"
SOURCE_AUTH_SCHEMA_TYPE = "HeavyTailShadowStubImplementationAuthorization.v1"
SOURCE_AUTH_HASH = (
    "988ed40a766a2fb5edf82bd33a0cdcf5540a4a38486bc36b180802b7ef7e2834"
)

SOURCE_SCHEMA_PLAN_ARTIFACT_ID = "heavy_tail_test_vector_schema_plan_001"
SOURCE_SCHEMA_PLAN_SCHEMA_TYPE = "HeavyTailTestVectorSchemaPlan.v1"
SOURCE_SCHEMA_PLAN_HASH = (
    "d42a9570d5958822f788cae937ce808649e5d9bf6bf2811f960ed2502ed6bd04"
)

FIXTURE_BASE_DIRECTORY = "tests/fixtures/heavy_tail"
TOTAL_FIXTURE_COUNT = 16
VALID_FIXTURE_COUNT = 6
INVALID_FIXTURE_COUNT = 4
NOT_COMPUTABLE_FIXTURE_COUNT = 6

ALLOWED_IMPLEMENTATION_STATUS = (
    "PLANNED_ONLY",
    "NOT_IMPLEMENTED",
    "BLOCKED_PENDING_REVIEW",
)

LOCKED_TRUE_FLAGS = (
    "advisory_only",
    "shadow_lane_only",
    "fixture_corpus_creation_plan_only",
    "fixture_creation_authorized",
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


class HeavyTailFixtureCorpusCreationPlanValidationError(ValueError):
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
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def default_source_authorization_binding() -> dict[str, Any]:
    return {
        "authorization_artifact_id": SOURCE_AUTH_ARTIFACT_ID,
        "authorization_schema_type": SOURCE_AUTH_SCHEMA_TYPE,
        "authorization_canonical_hash": SOURCE_AUTH_HASH,
        "hash_confirmed": True,
        "fixture_creation_authorized_acknowledged": True,
        "implementation_authorized_acknowledged": True,
        "fixture_files_not_created_in_this_plan": True,
        "computation_not_performed": True,
        "metric_values_not_emitted": True,
        "baseline_pack_not_updated": True,
        "shadow_stub_only_posture_preserved": True,
    }


def default_schema_plan_binding() -> dict[str, Any]:
    return {
        "schema_plan_artifact_id": SOURCE_SCHEMA_PLAN_ARTIFACT_ID,
        "schema_plan_schema_type": SOURCE_SCHEMA_PLAN_SCHEMA_TYPE,
        "schema_plan_canonical_hash": SOURCE_SCHEMA_PLAN_HASH,
        "hash_confirmed": True,
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
        "valid_fixture_schema_groups_count": 6,
        "invalid_fixture_schema_groups_count": 4,
        "not_computable_schema_groups_count": 6,
        "fixture_count_consistent_with_schema_plan": True,
    }


def default_fixture_manifest_plan() -> dict[str, Any]:
    return {
        "total_fixture_count": TOTAL_FIXTURE_COUNT,
        "valid_fixture_count": VALID_FIXTURE_COUNT,
        "invalid_fixture_count": INVALID_FIXTURE_COUNT,
        "not_computable_fixture_count": NOT_COMPUTABLE_FIXTURE_COUNT,
        "fixture_files_created_in_this_plan": False,
        "fixture_ids_deterministic": True,
        "fixture_ids_unique": True,
        "all_fixture_expected_outcomes_fixture_declared": True,
        "closed_form_derivation_used": True,
        "computation_not_performed": True,
        "shadow_stub_only": True,
    }


def default_valid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "ht-valid-001",
            "fixture_label": "bounded_power_law_alpha_2",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}"
                "/ht_valid_001_bounded_power_law_alpha_2.json"
            ),
            "planned_alpha": 2.0,
            "planned_sample_count": 20,
            "planned_expected_tail_threshold": 1.5,
            "sequence_derivation": "BOUNDED_INTEGER_POWER_LAW",
            "sequence_generation_note": (
                "20 non-negative integers with frequency proportional to k^{-2.0} "
                "for k=1..20, scaled to integer range [0, 500]. "
                "Analytically bounded; closed-form moments computable."
            ),
            "planned_expected_status": "COMPUTABLE",
            "planned_expected_tail_index_derivation": "RANK_FREQUENCY_SLOPE",
            "planned_expected_moment_summary_derivation": "CLOSED_FORM_POWER_LAW",
            "planned_expected_outcome_reason": "POWER_LAW_HEAVY_TAIL_DETECTED",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-valid-002",
            "fixture_label": "bounded_power_law_alpha_3",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}"
                "/ht_valid_002_bounded_power_law_alpha_3.json"
            ),
            "planned_alpha": 3.0,
            "planned_sample_count": 20,
            "planned_expected_tail_threshold": 1.5,
            "sequence_derivation": "BOUNDED_INTEGER_POWER_LAW",
            "sequence_generation_note": (
                "20 non-negative integers with frequency proportional to k^{-3.0} "
                "for k=1..20, scaled to integer range [0, 500]. "
                "Steeper decay than alpha=2.0; still classifies as heavy-tail."
            ),
            "planned_expected_status": "COMPUTABLE",
            "planned_expected_tail_index_derivation": "RANK_FREQUENCY_SLOPE",
            "planned_expected_moment_summary_derivation": "CLOSED_FORM_POWER_LAW",
            "planned_expected_outcome_reason": "POWER_LAW_HEAVY_TAIL_DETECTED",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-valid-003",
            "fixture_label": "light_tail_control_sequence",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}"
                "/ht_valid_003_light_tail_control_sequence.json"
            ),
            "planned_alpha": 5.0,
            "planned_sample_count": 20,
            "planned_expected_tail_threshold": 1.5,
            "sequence_derivation": "BOUNDED_INTEGER_EXPONENTIAL_DECAY",
            "sequence_generation_note": (
                "20 non-negative integers with rapidly decaying distribution "
                "(alpha=5.0); rank-frequency slope falls below threshold; "
                "serves as light-tail control case."
            ),
            "planned_expected_status": "COMPUTABLE",
            "planned_expected_tail_index_derivation": "RANK_FREQUENCY_SLOPE",
            "planned_expected_moment_summary_derivation": "CLOSED_FORM_THIN_TAIL",
            "planned_expected_outcome_reason": "LIGHT_TAIL_CONTROL",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-valid-004",
            "fixture_label": "single_large_outlier_sequence",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}"
                "/ht_valid_004_single_large_outlier_sequence.json"
            ),
            "planned_alpha": 2.0,
            "planned_sample_count": 20,
            "planned_expected_tail_threshold": 1.5,
            "sequence_derivation": "BOUNDED_INTEGER_SINGLE_OUTLIER",
            "sequence_generation_note": (
                "19 values equal to 1 plus one extreme value of 1000; "
                "tail classification dominated by the single outlier; "
                "moments analytically computable."
            ),
            "planned_expected_status": "COMPUTABLE",
            "planned_expected_tail_index_derivation": "OUTLIER_DOMINATED_SLOPE",
            "planned_expected_moment_summary_derivation": "CLOSED_FORM_OUTLIER",
            "planned_expected_outcome_reason": "SINGLE_OUTLIER_DOMINATED",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-valid-005",
            "fixture_label": "monotone_rank_frequency_sequence",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}"
                "/ht_valid_005_monotone_rank_frequency_sequence.json"
            ),
            "planned_alpha": 2.0,
            "planned_sample_count": 20,
            "planned_expected_tail_threshold": 1.5,
            "sequence_derivation": "BOUNDED_INTEGER_STRICTLY_MONOTONE",
            "sequence_generation_note": (
                "Strictly decreasing integers [20, 19, 18, ..., 1]; "
                "perfectly monotone rank-frequency sequence; "
                "slope analytically determined."
            ),
            "planned_expected_status": "COMPUTABLE",
            "planned_expected_tail_index_derivation": "MONOTONE_RANK_FREQUENCY_SLOPE",
            "planned_expected_moment_summary_derivation": "CLOSED_FORM_MONOTONE",
            "planned_expected_outcome_reason": "MONOTONE_RANK_FREQUENCY",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-valid-006",
            "fixture_label": "repeated_equal_values_control",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}"
                "/ht_valid_006_repeated_equal_values_control.json"
            ),
            "planned_alpha": 2.0,
            "planned_sample_count": 20,
            "planned_expected_tail_threshold": 1.5,
            "sequence_derivation": "BOUNDED_INTEGER_ALL_EQUAL",
            "sequence_generation_note": (
                "All 20 values equal to 10; degenerate flat rank-frequency "
                "distribution; tail index is zero (below any positive threshold); "
                "boundary case for classification logic."
            ),
            "planned_expected_status": "COMPUTABLE",
            "planned_expected_tail_index_derivation": "DEGENERATE_FLAT_SLOPE",
            "planned_expected_moment_summary_derivation": "CLOSED_FORM_EQUAL_VALUES",
            "planned_expected_outcome_reason": "REPEATED_EQUAL_VALUES",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "ht-invalid-001",
            "fixture_label": "missing_alpha",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_001_missing_alpha.json"
            ),
            "missing_or_invalid_field": "alpha",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "planned_expected_failure": "validation_error_missing_alpha",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-invalid-002",
            "fixture_label": "missing_sample_count",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_002_missing_sample_count.json"
            ),
            "missing_or_invalid_field": "sample_count",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "planned_expected_failure": "validation_error_missing_sample_count",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-invalid-003",
            "fixture_label": "missing_sequence_values",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_003_missing_sequence_values.json"
            ),
            "missing_or_invalid_field": "sequence_values",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "planned_expected_failure": "validation_error_missing_sequence_values",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-invalid-004",
            "fixture_label": "invalid_expected_status",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_004_invalid_expected_status.json"
            ),
            "missing_or_invalid_field": "expected_status",
            "invalid_reason": "INVALID_FIELD_VALUE",
            "planned_expected_failure": "validation_error_invalid_expected_status",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "ht-nc-001",
            "fixture_label": "alpha_lte_zero",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_nc_001_alpha_lte_zero.json"
            ),
            "not_computable_reason": "ALPHA_NOT_POSITIVE",
            "trigger_note": "alpha set to -1.0; violates alpha > 0 bound.",
            "planned_expected_state": "NOT_COMPUTABLE",
            "planned_expected_outcome_reason": "ALPHA_NOT_POSITIVE",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-nc-002",
            "fixture_label": "sample_count_zero",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_nc_002_sample_count_zero.json"
            ),
            "not_computable_reason": "ZERO_SAMPLE_COUNT",
            "trigger_note": "sample_count set to 0; empty population.",
            "planned_expected_state": "NOT_COMPUTABLE",
            "planned_expected_outcome_reason": "ZERO_SAMPLE_COUNT",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-nc-003",
            "fixture_label": "empty_sequence",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_nc_003_empty_sequence.json"
            ),
            "not_computable_reason": "EMPTY_SEQUENCE",
            "trigger_note": "sequence_values is an empty list [].",
            "planned_expected_state": "NOT_COMPUTABLE",
            "planned_expected_outcome_reason": "EMPTY_SEQUENCE",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-nc-004",
            "fixture_label": "non_finite_sequence_value",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_nc_004_non_finite_sequence_value.json"
            ),
            "not_computable_reason": "NON_FINITE_VALUE",
            "trigger_note": (
                "sequence_values contains a sentinel token representing "
                "a non-finite value (e.g., null or a string marker); "
                "tail analysis requires finite non-negative integers."
            ),
            "planned_expected_state": "NOT_COMPUTABLE",
            "planned_expected_outcome_reason": "NON_FINITE_VALUE",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-nc-005",
            "fixture_label": "negative_sequence_value",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_nc_005_negative_sequence_value.json"
            ),
            "not_computable_reason": "NEGATIVE_VALUE",
            "trigger_note": "sequence_values contains -1 among otherwise valid values.",
            "planned_expected_state": "NOT_COMPUTABLE",
            "planned_expected_outcome_reason": "NEGATIVE_VALUE",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_id": "ht-nc-006",
            "fixture_label": "sample_count_mismatch",
            "planned_file_path": (
                f"{FIXTURE_BASE_DIRECTORY}/ht_nc_006_sample_count_mismatch.json"
            ),
            "not_computable_reason": "SAMPLE_COUNT_MISMATCH",
            "trigger_note": (
                "sample_count declared as 20 but sequence_values contains 10 elements; "
                "structural contract violation."
            ),
            "planned_expected_state": "NOT_COMPUTABLE",
            "planned_expected_outcome_reason": "SAMPLE_COUNT_MISMATCH",
            "fixture_file_created": False,
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_expected_value_derivation_plan() -> dict[str, Any]:
    return {
        "derivation_policy": "FIXTURE_DECLARED_CLOSED_FORM",
        "approach": "ANALYTICALLY_BOUNDED_INTEGER_SEQUENCES_WITH_CLOSED_FORM_MOMENTS",
        "power_law_alpha_2_note": (
            "For alpha=2.0, n=20: frequency of rank k proportional to k^{-2}. "
            "Scaled to integer range to avoid floating-point representation. "
            "Mean and variance derived from partial sums of the power-law distribution."
        ),
        "power_law_alpha_3_note": (
            "For alpha=3.0, n=20: steeper decay than alpha=2.0. "
            "Closed-form moments finite and analytically tractable."
        ),
        "light_tail_note": (
            "Exponentially decaying sequence with alpha=5.0. "
            "Rank-frequency slope falls below the threshold; LIGHT_TAIL_CONTROL outcome."
        ),
        "outlier_note": (
            "One extreme value (1000) plus 19 equal values (1). "
            "Tail dominated by the outlier; moments analytically computable."
        ),
        "monotone_note": (
            "Strictly decreasing integers [20, 19, 18, ..., 1]. "
            "Rank-frequency slope analytically determined from arithmetic progression."
        ),
        "equal_values_note": (
            "All 20 values equal to 10. Degenerate distribution; "
            "tail index is zero (flat slope); REPEATED_EQUAL_VALUES outcome."
        ),
        "computation_in_plan": False,
        "derivation_executed_at_plan_stage": False,
        "actual_values_declared_at_fixture_receipt_stage": True,
    }


def default_fixture_file_path_plan() -> dict[str, Any]:
    valid_paths = [
        f"{FIXTURE_BASE_DIRECTORY}/ht_valid_001_bounded_power_law_alpha_2.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_valid_002_bounded_power_law_alpha_3.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_valid_003_light_tail_control_sequence.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_valid_004_single_large_outlier_sequence.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_valid_005_monotone_rank_frequency_sequence.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_valid_006_repeated_equal_values_control.json",
    ]
    invalid_paths = [
        f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_001_missing_alpha.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_002_missing_sample_count.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_003_missing_sequence_values.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_invalid_004_invalid_expected_status.json",
    ]
    nc_paths = [
        f"{FIXTURE_BASE_DIRECTORY}/ht_nc_001_alpha_lte_zero.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_nc_002_sample_count_zero.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_nc_003_empty_sequence.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_nc_004_non_finite_sequence_value.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_nc_005_negative_sequence_value.json",
        f"{FIXTURE_BASE_DIRECTORY}/ht_nc_006_sample_count_mismatch.json",
    ]
    return {
        "fixture_base_directory": FIXTURE_BASE_DIRECTORY,
        "fixture_file_format": "json",
        "fixture_naming_convention": "ht_{category}_{nnn}_{group_label}.json",
        "fixture_files_created_in_this_plan": False,
        "fixture_file_paths": sorted(valid_paths + invalid_paths + nc_paths),
    }


def default_corpus_creation_scope_review() -> dict[str, Any]:
    return {
        "fixture_creation_authorized": True,
        "fixture_files_created_in_this_plan": False,
        "fixture_files_will_be_created_in_next_step": True,
        "computation_not_in_scope": True,
        "metric_emission_not_in_scope": True,
        "baseline_pack_update_not_in_scope": True,
        "shadow_stub_only_posture_preserved": True,
        "all_planned_fixture_ids_deterministic": True,
        "all_planned_fixture_ids_unique": True,
        "confirmed": True,
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_corpus_creation_plan_only": True,
        "fixture_creation_authorized": True,
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
        "fixture_corpus_creation": "AUTHORIZED_PENDING_THIS_PLAN_SEAL",
        "computation": "BLOCKED",
        "metric_emission": "BLOCKED",
        "forecast_influence": "BLOCKED",
        "p43_lanes": "BLOCKED",
        "runtime_mutation": "BLOCKED",
        "production_activation": "BLOCKED",
        "canon_promotion": "BLOCKED",
        "execution_authority": "BLOCKED",
        "inference_authority": "BLOCKED",
        "baseline_pack_update": "BLOCKED_UNTIL_COMPUTATION_RECEIPT",
        "confirmed": True,
        "all_blocked_scopes_correct": True,
    }


def validate_heavy_tail_fixture_corpus_creation_plan(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "plan_id", "plan_type", "plan_status", "operator_id",
        "source_authorization_binding", "schema_plan_binding", "fixture_manifest_plan",
        "valid_fixture_plan", "invalid_fixture_plan", "not_computable_fixture_plan",
        "expected_value_derivation_plan", "fixture_file_path_plan",
        "corpus_creation_scope_review", "authority_lock_review", "blocked_scope_review",
        "recommended_next_step", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise HeavyTailFixtureCorpusCreationPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise HeavyTailFixtureCorpusCreationPlanValidationError("invalid_plan_type")
    if packet["plan_status"] != PLAN_STATUS:
        raise HeavyTailFixtureCorpusCreationPlanValidationError("invalid_plan_status")
    if packet["operator_id"] != OPERATOR_ID:
        raise HeavyTailFixtureCorpusCreationPlanValidationError("unknown_operator_id")

    auth_binding = packet["source_authorization_binding"]
    if auth_binding.get("authorization_canonical_hash") != SOURCE_AUTH_HASH:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "authorization_hash_mismatch"
        )
    if auth_binding.get("hash_confirmed") is not True:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "authorization_hash_not_confirmed"
        )

    sp_binding = packet["schema_plan_binding"]
    if sp_binding.get("schema_plan_canonical_hash") != SOURCE_SCHEMA_PLAN_HASH:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "schema_plan_hash_mismatch"
        )
    if sp_binding.get("hash_confirmed") is not True:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "schema_plan_hash_not_confirmed"
        )

    manifest = packet["fixture_manifest_plan"]
    if manifest.get("total_fixture_count") != TOTAL_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "total_fixture_count_mismatch"
        )
    if manifest.get("valid_fixture_count") != VALID_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "valid_fixture_count_mismatch"
        )
    if manifest.get("invalid_fixture_count") != INVALID_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "invalid_fixture_count_mismatch"
        )
    if manifest.get("not_computable_fixture_count") != NOT_COMPUTABLE_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "not_computable_fixture_count_mismatch"
        )
    if manifest.get("fixture_files_created_in_this_plan") is not False:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "fixture_files_must_not_be_created_in_this_plan"
        )

    vfp = packet["valid_fixture_plan"]
    if len(vfp) != VALID_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "valid_fixture_plan_count_mismatch"
        )
    ifp = packet["invalid_fixture_plan"]
    if len(ifp) != INVALID_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "invalid_fixture_plan_count_mismatch"
        )
    ncfp = packet["not_computable_fixture_plan"]
    if len(ncfp) != NOT_COMPUTABLE_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "not_computable_fixture_plan_count_mismatch"
        )

    all_ids: list[str] = []
    for group in (vfp, ifp, ncfp):
        for item in group:
            fid = item.get("fixture_id")
            if fid in all_ids:
                raise HeavyTailFixtureCorpusCreationPlanValidationError(
                    f"duplicate_fixture_id:{fid}"
                )
            all_ids.append(fid)
            if item.get("fixture_file_created") is not False:
                raise HeavyTailFixtureCorpusCreationPlanValidationError(
                    f"fixture_file_must_not_be_created:{fid}"
                )
            if item.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUS:
                raise HeavyTailFixtureCorpusCreationPlanValidationError(
                    f"unknown_implementation_status:{fid}"
                )

    for f in vfp:
        if f.get("planned_expected_status") != "COMPUTABLE":
            raise HeavyTailFixtureCorpusCreationPlanValidationError(
                "valid_fixture_must_have_computable_status"
            )

    for f in ncfp:
        if f.get("planned_expected_state") != "NOT_COMPUTABLE":
            raise HeavyTailFixtureCorpusCreationPlanValidationError(
                "not_computable_fixture_must_have_not_computable_state"
            )

    fpp = packet["fixture_file_path_plan"]
    if fpp.get("fixture_files_created_in_this_plan") is not False:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "fixture_file_path_plan_must_not_create_files"
        )
    if len(fpp.get("fixture_file_paths", [])) != TOTAL_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationPlanValidationError(
            "fixture_file_paths_count_mismatch"
        )

    auth_lock = packet["authority_lock_review"]
    for flag in LOCKED_TRUE_FLAGS:
        if auth_lock.get(flag) is not True:
            raise HeavyTailFixtureCorpusCreationPlanValidationError(
                f"authority_lock_must_be_true:{flag}"
            )
    for flag in LOCKED_FALSE_FLAGS:
        if auth_lock.get(flag) is not False:
            raise HeavyTailFixtureCorpusCreationPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )

    _prov_safe(packet["provenance"])


def compute_heavy_tail_fixture_corpus_creation_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_heavy_tail_fixture_corpus_creation_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_heavy_tail_fixture_corpus_creation_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "plan_status": PLAN_STATUS,
        "operator_id": OPERATOR_ID,
        "source_authorization_binding": payload.get(
            "source_authorization_binding", default_source_authorization_binding()
        ),
        "schema_plan_binding": payload.get(
            "schema_plan_binding", default_schema_plan_binding()
        ),
        "fixture_manifest_plan": payload.get(
            "fixture_manifest_plan", default_fixture_manifest_plan()
        ),
        "valid_fixture_plan": sorted(
            payload.get("valid_fixture_plan", default_valid_fixture_plan()),
            key=lambda x: x["fixture_id"],
        ),
        "invalid_fixture_plan": sorted(
            payload.get("invalid_fixture_plan", default_invalid_fixture_plan()),
            key=lambda x: x["fixture_id"],
        ),
        "not_computable_fixture_plan": sorted(
            payload.get(
                "not_computable_fixture_plan", default_not_computable_fixture_plan()
            ),
            key=lambda x: x["fixture_id"],
        ),
        "expected_value_derivation_plan": payload.get(
            "expected_value_derivation_plan", default_expected_value_derivation_plan()
        ),
        "fixture_file_path_plan": payload.get(
            "fixture_file_path_plan", default_fixture_file_path_plan()
        ),
        "corpus_creation_scope_review": payload.get(
            "corpus_creation_scope_review", default_corpus_creation_scope_review()
        ),
        "authority_lock_review": payload.get(
            "authority_lock_review", default_authority_lock_review()
        ),
        "blocked_scope_review": payload.get(
            "blocked_scope_review", default_blocked_scope_review()
        ),
        "recommended_next_step": payload.get(
            "recommended_next_step", "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT"
        ),
    }
    base["canonical_hash"] = compute_heavy_tail_fixture_corpus_creation_plan_hash(base)
    validate_heavy_tail_fixture_corpus_creation_plan(base)
    return _finalize(base)
