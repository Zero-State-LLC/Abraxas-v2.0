from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureSchemaValidationCompleteReview.v1"
REVIEW_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_VALIDATION_EXECUTION_HASH = (
    "a48385e8eac8b6ea2342ef0b26dd1c1da35716dfcfdade62619b5eed1446c786"
)
SOURCE_VALIDATION_PLAN_HASH = (
    "d11582c8c497c2012b813218be00d4ddd51d17678a8a1512ce490b341f247309"
)
SOURCE_COMPLETE_REVIEW_HASH = (
    "08500a6b86b460b03a8858135de0d3c526e9baf58ec4e2c554dd9e03500ac51e"
)
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_REVIEW_STAGE = (
    "FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_ONLY",
    "BLOCKED_PENDING_REVIEW",
)

EXPECTED_TOTAL = 14
EXPECTED_VALID = 5
EXPECTED_INVALID = 5
EXPECTED_NC = 4

FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "wasserstein-distance",
    "expected-wasserstein",
    "earth-mover",
    "ot-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "sinkhorn-kernel",
    "authority-flag",
)


class WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Default sub-structures
# ---------------------------------------------------------------------------


def default_fixture_count_review() -> dict[str, Any]:
    return {
        "total_fixtures_reviewed": EXPECTED_TOTAL,
        "total_fixtures_validated": EXPECTED_TOTAL,
        "valid_fixtures_confirmed": EXPECTED_VALID,
        "invalid_fixtures_confirmed": EXPECTED_INVALID,
        "not_computable_fixtures_confirmed": EXPECTED_NC,
        "count_review_status": "PASS",
    }


def default_validation_coverage_review() -> dict[str, Any]:
    return {
        "all_plan_checks_executed": True,
        "parse_checks_executed": True,
        "type_group_consistency_checks_executed": True,
        "gate_hash_checks_executed": True,
        "lane_checks_executed": True,
        "authority_checks_executed": True,
        "rejection_reason_checks_executed": True,
        "coverage_review_status": "PASS",
    }


def default_schema_group_review() -> dict[str, Any]:
    return {
        "valid_groups_covered": [
            "DISTRIBUTION_PAIR_SCHEMA",
            "WEIGHTED_HISTOGRAM_SCHEMA",
            "REFERENCE_VECTOR_SCHEMA",
            "GROUND_METRIC_SCHEMA",
            "DEGENERATE_DISTRIBUTION_SCHEMA",
        ],
        "invalid_groups_covered": [
            "MISSING_REQUIRED_FIELD",
            "EMPTY_DISTRIBUTION",
            "INVALID_WEIGHT_SUM",
            "DIMENSION_MISMATCH",
            "GROUND_METRIC_UNDECLARED",
        ],
        "not_computable_groups_covered": [
            "EMPTY_INPUT",
            "GROUND_METRIC_UNDECLARED",
            "NUMERICAL_POLICY_MISSING",
            "DIMENSIONALITY_UNDECLARED",
        ],
        "all_declared_groups_covered": True,
        "schema_group_review_status": "PASS",
    }


def default_no_metric_value_review() -> dict[str, Any]:
    return {
        "field_checked": "metric_value_emitted",
        "total_fixtures_scanned": EXPECTED_TOTAL,
        "violations_found": 0,
        "all_false_confirmed": True,
        "no_metric_value_review_status": "PASS",
    }


def default_no_expected_distance_review() -> dict[str, Any]:
    return {
        "field_checked": "expected_wasserstein_distance_included",
        "total_fixtures_scanned": EXPECTED_TOTAL,
        "violations_found": 0,
        "all_false_confirmed": True,
        "no_expected_distance_review_status": "PASS",
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "gate_hash_all_pinned": True,
        "intended_lane_all_shadow": True,
        "creation_authorized_all": True,
        "no_execution_authority_granted": True,
        "no_computation_fields_present": True,
        "source_gate_hash_verified": SOURCE_GATE_HASH,
        "authority_lock_review_status": "PASS",
    }


def default_validation_completion_summary() -> dict[str, Any]:
    return {
        "total_fixtures": EXPECTED_TOTAL,
        "total_passed": EXPECTED_TOTAL,
        "total_failed": 0,
        "valid_passed": EXPECTED_VALID,
        "invalid_passed": EXPECTED_INVALID,
        "not_computable_passed": EXPECTED_NC,
        "all_obligations_satisfied": True,
        "schema_validation_complete": True,
        "review_status": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_READY"
        ),
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "wasserstein_computation": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
        "forecast_influence": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_schema_validation_complete_review_only": True,
        "fixture_schema_validation_executed": True,
        "wasserstein_computation_authorized": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
        "forecast_influence": False,
        "execution_authority": False,
        "runtime_mutation": False,
        "production_activation": False,
        "canon_promotion": False,
    }


# ---------------------------------------------------------------------------
# Safety scanner
# ---------------------------------------------------------------------------


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_fixture_schema_validation_complete_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "review_id",
        "review_type",
        "operator_id",
        "source_validation_execution_hash",
        "source_validation_plan_hash",
        "intended_lane",
        "review_stage",
        "fixture_count_review",
        "validation_coverage_review",
        "schema_group_review",
        "no_metric_value_review",
        "no_expected_distance_review",
        "authority_lock_review",
        "validation_completion_summary",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_review_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "unknown_operator_id"
        )
    if packet["source_validation_execution_hash"] != SOURCE_VALIDATION_EXECUTION_HASH:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_source_validation_execution_hash"
        )
    if packet["source_validation_plan_hash"] != SOURCE_VALIDATION_PLAN_HASH:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_source_validation_plan_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "unknown_intended_lane"
        )
    if packet["review_stage"] not in ALLOWED_REVIEW_STAGE:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "unknown_review_stage"
        )

    fcr = packet["fixture_count_review"]
    if fcr.get("total_fixtures_reviewed") != EXPECTED_TOTAL:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_count_review_total_mismatch"
        )
    if fcr.get("total_fixtures_validated") != EXPECTED_TOTAL:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_count_review_validated_mismatch"
        )
    if fcr.get("valid_fixtures_confirmed") != EXPECTED_VALID:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_count_review_valid_mismatch"
        )
    if fcr.get("invalid_fixtures_confirmed") != EXPECTED_INVALID:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_count_review_invalid_mismatch"
        )
    if fcr.get("not_computable_fixtures_confirmed") != EXPECTED_NC:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_count_review_nc_mismatch"
        )
    if fcr.get("count_review_status") != "PASS":
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_count_review_not_pass"
        )

    vcr = packet["validation_coverage_review"]
    if not vcr.get("all_plan_checks_executed"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "not_all_plan_checks_executed"
        )
    if vcr.get("coverage_review_status") != "PASS":
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "coverage_review_not_pass"
        )

    sgr = packet["schema_group_review"]
    if not sgr.get("all_declared_groups_covered"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "not_all_schema_groups_covered"
        )
    if sgr.get("schema_group_review_status") != "PASS":
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "schema_group_review_not_pass"
        )

    nmvr = packet["no_metric_value_review"]
    if not nmvr.get("all_false_confirmed"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "metric_value_violation_in_review"
        )
    if nmvr.get("violations_found") != 0:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "metric_value_violations_nonzero"
        )

    nedr = packet["no_expected_distance_review"]
    if not nedr.get("all_false_confirmed"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "expected_distance_violation_in_review"
        )
    if nedr.get("violations_found") != 0:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "expected_distance_violations_nonzero"
        )

    alr = packet["authority_lock_review"]
    if not alr.get("gate_hash_all_pinned"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "gate_hash_not_all_pinned_in_review"
        )
    if alr.get("source_gate_hash_verified") != SOURCE_GATE_HASH:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "source_gate_hash_mismatch_in_review"
        )
    if alr.get("authority_lock_review_status") != "PASS":
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "authority_lock_review_not_pass"
        )

    vcs = packet["validation_completion_summary"]
    if not vcs.get("all_obligations_satisfied"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "not_all_obligations_satisfied"
        )
    if not vcs.get("schema_validation_complete"):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "schema_validation_not_complete"
        )
    expected_status = (
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_READY"
    )
    if vcs.get("review_status") != expected_status:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "validation_completion_summary_status_invalid"
        )

    al = packet["authority_locks"]
    if al.get("fixture_schema_validation_executed") is not True:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_schema_validation_executed_must_be_true"
        )
    if al.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "wasserstein_computation_must_be_unauthorized"
        )
    if al.get("fixture_schema_validation_complete_review_only") is not True:
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "fixture_schema_validation_complete_review_only_must_be_true"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_authority_locks"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_blocked_scopes"
        )
    if packet["fixture_count_review"] != default_fixture_count_review():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_fixture_count_review"
        )
    if packet["validation_coverage_review"] != default_validation_coverage_review():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_validation_coverage_review"
        )
    if packet["schema_group_review"] != default_schema_group_review():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_schema_group_review"
        )
    if packet["no_metric_value_review"] != default_no_metric_value_review():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_no_metric_value_review"
        )
    if packet["no_expected_distance_review"] != default_no_expected_distance_review():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_no_expected_distance_review"
        )
    if packet["authority_lock_review"] != default_authority_lock_review():
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_authority_lock_review"
        )
    if (
        packet["validation_completion_summary"]
        != default_validation_completion_summary()
    ):
        raise WassersteinTestVectorFixtureSchemaValidationCompleteReviewError(
            "invalid_validation_completion_summary"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_schema_validation_complete_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_schema_validation_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_schema_validation_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_validation_execution_hash": SOURCE_VALIDATION_EXECUTION_HASH,
        "source_validation_plan_hash": SOURCE_VALIDATION_PLAN_HASH,
        "fixture_count_review": payload.get(
            "fixture_count_review", default_fixture_count_review()
        ),
        "validation_coverage_review": payload.get(
            "validation_coverage_review", default_validation_coverage_review()
        ),
        "schema_group_review": payload.get(
            "schema_group_review", default_schema_group_review()
        ),
        "no_metric_value_review": payload.get(
            "no_metric_value_review", default_no_metric_value_review()
        ),
        "no_expected_distance_review": payload.get(
            "no_expected_distance_review", default_no_expected_distance_review()
        ),
        "authority_lock_review": payload.get(
            "authority_lock_review", default_authority_lock_review()
        ),
        "validation_completion_summary": payload.get(
            "validation_completion_summary", default_validation_completion_summary()
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_schema_validation_complete_review_hash(
            base
        )
    )
    validate_wasserstein_test_vector_fixture_schema_validation_complete_review(base)
    return _finalize(base)
