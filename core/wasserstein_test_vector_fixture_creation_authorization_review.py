from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureCreationAuthorizationReview.v1"
REVIEW_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_PR_PLAN_HASH = (
    "ae92c56aa0bb43c3a2802027e9294a1d33e945f7f510954005709e8d63a7d67c"
)
SOURCE_READINESS_REVIEW_HASH = (
    "1d559371c162d43f0914e651993dfcc3d1f76910f8dced3cf5622072bc84b029"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_REVIEW_STAGE = (
    "FIXTURE_CREATION_AUTHORIZATION_REVIEW_ONLY",
    "BLOCKED_PENDING_OPERATOR_DECISION",
)
ALLOWED_MANIFEST_STATUS = ("ALL_ENTRIES_PLANNED", "ENTRIES_MISSING", "ENTRIES_UNAUTHORIZED")
ALLOWED_BATCH_STATUS = ("ALL_BATCHES_PLANNED", "BATCHES_MISSING", "BATCHES_UNAUTHORIZED")
ALLOWED_LOCK_STATUS = ("ALL_LOCKS_SATISFIED", "LOCK_VIOLATION_DETECTED", "NOT_VERIFIED")
ALLOWED_FINDING_STATUS = ("SATISFIED", "ACTIVE_BLOCKER", "HELD_FOR_REVIEW")
ALLOWED_OPERATOR_STATUS = ("REQUIRED", "SATISFIED", "WAIVED")
ALLOWED_RECOMMENDATION_STATUS = (
    "RECOMMEND_AUTHORIZE",
    "RECOMMEND_BLOCK",
    "HELD_PENDING_OPERATOR_DECISION",
)

EXPECTED_MANIFEST_ENTRY_COUNT = 14
EXPECTED_BATCH_COUNT = 3

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


class WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(ValueError):
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


def default_manifest_review() -> dict[str, Any]:
    return {
        "total_entries_reviewed": 14,
        "valid_entries": 5,
        "invalid_entries": 5,
        "not_computable_entries": 4,
        "all_entries_planned": True,
        "all_creation_unauthorized": True,
        "duplicate_ids_detected": False,
        "duplicate_paths_detected": False,
        "manifest_status": "ALL_ENTRIES_PLANNED",
        "finding_status": "SATISFIED",
    }


def default_batch_review() -> dict[str, Any]:
    return {
        "total_batches_reviewed": 3,
        "batch_01_valid_count": 5,
        "batch_02_invalid_count": 5,
        "batch_03_not_computable_count": 4,
        "all_batches_planned": True,
        "all_batches_creation_unauthorized": True,
        "batch_status": "ALL_BATCHES_PLANNED",
        "finding_status": "SATISFIED",
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "fixture_files_created_locked_false": True,
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


def default_operator_authorization_requirement() -> dict[str, Any]:
    return {
        "operator_decision_required": True,
        "fixture_file_creation_authorized": False,
        "operator_status": "REQUIRED",
        "reason": (
            "Manifest review, batch review, and authority lock review all passed. "
            "Fixture file creation is recommended for authorization. A separate "
            "operator decision artifact must be provided to set "
            "fixture_file_creation_authorized=true before any files are written."
        ),
        "finding_status": "HELD_FOR_REVIEW",
    }


def default_authorization_recommendation() -> dict[str, Any]:
    return {
        "authorize_fixture_file_creation": True,
        "fixture_file_creation_authorized": False,
        "recommendation_status": "HELD_PENDING_OPERATOR_DECISION",
        "basis": [
            "manifest_review:SATISFIED",
            "batch_review:SATISFIED",
            "authority_lock_review:SATISFIED",
        ],
        "blocking_conditions": [],
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
        "fixture_creation_authorization_review_only": True,
        "fixture_files_created": False,
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
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_fixture_creation_authorization_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "authorization_review_id",
        "review_type",
        "operator_id",
        "source_pr_plan_hash",
        "source_readiness_review_hash",
        "intended_lane",
        "review_stage",
        "manifest_review",
        "batch_review",
        "authority_lock_review",
        "operator_authorization_requirement",
        "authorization_recommendation",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_review_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_operator_id"
        )
    if packet["source_pr_plan_hash"] != SOURCE_PR_PLAN_HASH:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_source_pr_plan_hash"
        )
    if packet["source_readiness_review_hash"] != SOURCE_READINESS_REVIEW_HASH:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_source_readiness_review_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_intended_lane"
        )
    if packet["review_stage"] not in ALLOWED_REVIEW_STAGE:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_review_stage"
        )

    mr = packet["manifest_review"]
    if mr.get("manifest_status") not in ALLOWED_MANIFEST_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_manifest_status"
        )
    if mr.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_manifest_finding_status"
        )

    br = packet["batch_review"]
    if br.get("batch_status") not in ALLOWED_BATCH_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_batch_status"
        )
    if br.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_batch_finding_status"
        )

    alr = packet["authority_lock_review"]
    if alr.get("lock_status") not in ALLOWED_LOCK_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_lock_status"
        )
    if alr.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_lock_finding_status"
        )

    oar = packet["operator_authorization_requirement"]
    if oar.get("operator_status") not in ALLOWED_OPERATOR_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_operator_status"
        )
    if oar.get("finding_status") not in ALLOWED_FINDING_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_operator_finding_status"
        )
    if oar.get("fixture_file_creation_authorized") is not False:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "fixture_file_creation_must_be_unauthorized"
        )
    if oar.get("operator_decision_required") is not True:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "operator_decision_must_be_required"
        )

    rec = packet["authorization_recommendation"]
    if rec.get("recommendation_status") not in ALLOWED_RECOMMENDATION_STATUS:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "unknown_recommendation_status"
        )
    if rec.get("fixture_file_creation_authorized") is not False:
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "recommendation_fixture_file_creation_must_be_false"
        )

    if packet["manifest_review"] != default_manifest_review():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_manifest_review"
        )
    if packet["batch_review"] != default_batch_review():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_batch_review"
        )
    if packet["authority_lock_review"] != default_authority_lock_review():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_authority_lock_review"
        )
    if packet["operator_authorization_requirement"] != default_operator_authorization_requirement():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_operator_authorization_requirement"
        )
    if packet["authorization_recommendation"] != default_authorization_recommendation():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_authorization_recommendation"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_blocked_scopes"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureCreationAuthorizationReviewValidationError(
            "invalid_authority_locks"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_creation_authorization_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_creation_authorization_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_creation_authorization_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_pr_plan_hash": SOURCE_PR_PLAN_HASH,
        "source_readiness_review_hash": SOURCE_READINESS_REVIEW_HASH,
        "manifest_review": payload.get("manifest_review", default_manifest_review()),
        "batch_review": payload.get("batch_review", default_batch_review()),
        "authority_lock_review": payload.get(
            "authority_lock_review", default_authority_lock_review()
        ),
        "operator_authorization_requirement": payload.get(
            "operator_authorization_requirement",
            default_operator_authorization_requirement(),
        ),
        "authorization_recommendation": payload.get(
            "authorization_recommendation", default_authorization_recommendation()
        ),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_creation_authorization_review_hash(base)
    )
    validate_wasserstein_test_vector_fixture_creation_authorization_review(base)
    return _finalize(base)
