from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureCreationReadinessReview.v1"
REVIEW_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_FIXTURE_PLAN_HASH = (
    "21513971f031d40214fb0534c8258f41ebfff0c4d3d5bfaf14005af1719fa049"
)
SOURCE_SCHEMA_PLAN_HASH = (
    "77e06b11f427973e478076464db2055c1baae555f88f7d32be5cfb7b877088b3"
)
SOURCE_DOSSIER_HASH = (
    "b6890c0a3aa92a63cd5798724e032b712846b51f70e38de503e3a179d55a8f4c"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_REVIEW_STAGE = (
    "FIXTURE_CREATION_READINESS_REVIEW_ONLY",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_PRESENCE_STATUS = ("PRESENT_AND_VALIDATED", "MISSING", "INCOMPLETE")
ALLOWED_COVERAGE_STATUS = ("COMPLETE", "INCOMPLETE", "NOT_VERIFIED")
ALLOWED_LOCK_STATUS = ("ALL_LOCKS_SATISFIED", "LOCK_VIOLATION_DETECTED", "NOT_VERIFIED")
ALLOWED_REVIEW_STATUS = ("REQUIRED", "SATISFIED", "WAIVED")
ALLOWED_FINDING_STATUS = ("SATISFIED", "ACTIVE_BLOCKER", "HELD_FOR_REVIEW")

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


class WassersteinTestVectorFixtureCreationReadinessReviewValidationError(ValueError):
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


def default_plan_triad_presence_check() -> dict[str, Any]:
    return {
        "valid_fixture_plan_present": True,
        "invalid_fixture_plan_present": True,
        "not_computable_fixture_plan_present": True,
        "triad_complete": True,
        "valid_fixture_plan_status": "PRESENT_AND_VALIDATED",
        "invalid_fixture_plan_status": "PRESENT_AND_VALIDATED",
        "not_computable_fixture_plan_status": "PRESENT_AND_VALIDATED",
        "source_fixture_plan_hash_verified": True,
        "finding_status": "SATISFIED",
    }


def default_fixture_coverage_check() -> dict[str, Any]:
    return {
        "valid_groups_covered": 5,
        "invalid_groups_covered": 5,
        "not_computable_groups_covered": 4,
        "total_groups_covered": 14,
        "expected_valid_groups": 5,
        "expected_invalid_groups": 5,
        "expected_not_computable_groups": 4,
        "expected_total_groups": 14,
        "coverage_complete": True,
        "coverage_status": "COMPLETE",
        "finding_status": "SATISFIED",
    }


def default_authority_lock_check() -> dict[str, Any]:
    return {
        "fixture_files_generated_locked_false": True,
        "wasserstein_computation_locked_false": True,
        "emits_metric_values_locked_false": True,
        "expected_wasserstein_distances_locked_false": True,
        "forecast_influence_locked_false": True,
        "p43_surface_lanes_locked_false": True,
        "production_activation_locked_false": True,
        "canon_promotion_locked_false": True,
        "runtime_mutation_locked_false": True,
        "execution_authority_locked_false": True,
        "inference_authority_locked_false": True,
        "all_locks_satisfied": True,
        "lock_status": "ALL_LOCKS_SATISFIED",
        "finding_status": "SATISFIED",
    }


def default_operator_review_requirement() -> dict[str, Any]:
    return {
        "operator_review_required": True,
        "fixture_file_creation_authorized": False,
        "review_status": "REQUIRED",
        "reason": (
            "Operator must explicitly authorize fixture file creation before "
            "any files are generated. No fixture files may be written until "
            "operator review is complete and fixture_file_creation_authorized "
            "is set to true by operator action."
        ),
        "finding_status": "HELD_FOR_REVIEW",
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "fixture_files_generated": False,
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
        "fixture_creation_readiness_review_only": True,
        "fixture_files_generated": False,
        "fixture_file_creation_authorized": False,
        "wasserstein_computation_authorized": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
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
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_fixture_creation_readiness_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "review_id",
        "review_type",
        "operator_id",
        "source_fixture_plan_hash",
        "source_schema_plan_hash",
        "source_dossier_hash",
        "intended_lane",
        "review_stage",
        "plan_triad_presence_check",
        "fixture_coverage_check",
        "authority_lock_check",
        "operator_review_requirement",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_review_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_operator_id"
        )
    if packet["source_fixture_plan_hash"] != SOURCE_FIXTURE_PLAN_HASH:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_source_fixture_plan_hash"
        )
    if packet["source_schema_plan_hash"] != SOURCE_SCHEMA_PLAN_HASH:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_source_schema_plan_hash"
        )
    if packet["source_dossier_hash"] != SOURCE_DOSSIER_HASH:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_source_dossier_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_intended_lane"
        )
    if packet["review_stage"] not in ALLOWED_REVIEW_STAGE:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_review_stage"
        )

    triad = packet["plan_triad_presence_check"]
    if triad.get("valid_fixture_plan_status") not in ALLOWED_PRESENCE_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_valid_fixture_plan_status"
        )
    if triad.get("invalid_fixture_plan_status") not in ALLOWED_PRESENCE_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_invalid_fixture_plan_status"
        )
    if triad.get("not_computable_fixture_plan_status") not in ALLOWED_PRESENCE_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_nc_fixture_plan_status"
        )
    if triad.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_triad_finding_status"
        )

    cov = packet["fixture_coverage_check"]
    if cov.get("coverage_status") not in ALLOWED_COVERAGE_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_coverage_status"
        )
    if cov.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_coverage_finding_status"
        )

    lock = packet["authority_lock_check"]
    if lock.get("lock_status") not in ALLOWED_LOCK_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_lock_status"
        )
    if lock.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_lock_finding_status"
        )

    op = packet["operator_review_requirement"]
    if op.get("review_status") not in ALLOWED_REVIEW_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_review_status"
        )
    if op.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "unknown_operator_finding_status"
        )
    if op.get("fixture_file_creation_authorized") is not False:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "fixture_file_creation_must_be_unauthorized"
        )
    if op.get("operator_review_required") is not True:
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "operator_review_must_be_required"
        )

    if packet["plan_triad_presence_check"] != default_plan_triad_presence_check():
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_plan_triad_presence_check"
        )
    if packet["fixture_coverage_check"] != default_fixture_coverage_check():
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_fixture_coverage_check"
        )
    if packet["authority_lock_check"] != default_authority_lock_check():
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_authority_lock_check"
        )
    if packet["operator_review_requirement"] != default_operator_review_requirement():
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_operator_review_requirement"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_blocked_scopes"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureCreationReadinessReviewValidationError(
            "invalid_authority_locks"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_creation_readiness_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_creation_readiness_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_creation_readiness_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "source_schema_plan_hash": SOURCE_SCHEMA_PLAN_HASH,
        "source_dossier_hash": SOURCE_DOSSIER_HASH,
        "plan_triad_presence_check": payload.get(
            "plan_triad_presence_check", default_plan_triad_presence_check()
        ),
        "fixture_coverage_check": payload.get(
            "fixture_coverage_check", default_fixture_coverage_check()
        ),
        "authority_lock_check": payload.get(
            "authority_lock_check", default_authority_lock_check()
        ),
        "operator_review_requirement": payload.get(
            "operator_review_requirement", default_operator_review_requirement()
        ),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_creation_readiness_review_hash(base)
    )
    validate_wasserstein_test_vector_fixture_creation_readiness_review(base)
    return _finalize(base)
