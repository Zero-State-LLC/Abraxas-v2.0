from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorComputationAuthorizationReview.v1"
REVIEW_TYPE = "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_REVIEW"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH = (
    "6efad6ecfbfc4ff186496d4f49871a52adbce5015b7222fa1dbacf6e88d92eea"
)
SOURCE_FIXTURE_CREATION_RECEIPT_HASH = (
    "7625ddf00c136783a6501f9250ad30cee4f7930c07bbf520ad1a073197898c04"
)
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_REVIEW_STAGE = (
    "COMPUTATION_AUTHORIZATION_REVIEW_ONLY",
    "BLOCKED_PENDING_AUTHORIZATION_REVIEW",
)

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


class WassersteinTestVectorComputationAuthorizationReviewError(ValueError):
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


def default_fixture_corpus_readiness_review() -> dict[str, Any]:
    return {
        "total_fixtures_verified": 14,
        "valid_fixtures": 5,
        "invalid_fixtures": 5,
        "not_computable_fixtures": 4,
        "all_fixture_files_present": True,
        "all_gate_hashes_pinned": True,
        "source_gate_hash": SOURCE_GATE_HASH,
        "corpus_readiness_status": "READY",
    }


def default_schema_validation_completion_review() -> dict[str, Any]:
    return {
        "schema_validation_executed": True,
        "all_14_fixtures_passed": True,
        "no_metric_values_present": True,
        "no_expected_distances_present": True,
        "complete_review_sealed": True,
        "operator_approval_on_record": True,
        "source_schema_validation_complete_review_hash": (
            SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
        ),
        "schema_validation_completion_status": "COMPLETE",
    }


def default_computation_scope_review() -> dict[str, Any]:
    return {
        "computation_scope": "BOUNDED_FIXTURE_ONLY",
        "scope_restricted_to": [
            "valid_fixture_inputs_only",
            "shadow_lane_only",
            "no_production_data",
            "no_runtime_mutation",
            "no_forecast_influence",
        ],
        "excluded_scopes": [
            "p43_surface_lanes",
            "production_activation",
            "canon_promotion",
            "metric_value_emission",
            "expected_distance_addition",
            "execution_authority",
            "inference_authority",
        ],
        "computation_scope_status": "ELIGIBLE_FOR_BOUNDED_AUTHORIZATION",
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "all_authority_locks_preserved": True,
        "advisory_only_confirmed": True,
        "shadow_lane_only_confirmed": True,
        "no_execution_authority": True,
        "no_runtime_mutation": True,
        "no_forecast_influence": True,
        "no_production_activation": True,
        "source_gate_hash_verified": SOURCE_GATE_HASH,
        "authority_lock_review_status": "PASS",
    }


def default_operator_authorization_requirement() -> dict[str, Any]:
    return {
        "operator_decision_required": True,
        "operator_decision_artifact_required": True,
        "required_artifact_type": (
            "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_OPERATOR_DECISION"
        ),
        "authorization_cannot_self_activate": True,
        "current_authorization_state": "PENDING_OPERATOR_DECISION",
    }


def default_authorization_recommendation() -> dict[str, Any]:
    return {
        "recommend_wasserstein_computation_authorization": True,
        "recommendation_basis": [
            "fixture_corpus_verified_14_of_14",
            "schema_validation_complete_review_sealed",
            "no_metric_values_in_corpus",
            "no_expected_distances_in_corpus",
            "all_authority_locks_preserved",
            "operator_approval_on_record",
            "computation_scope_bounded_to_fixture_only",
        ],
        "wasserstein_computation_authorized": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
        "forecast_influence": False,
        "authorization_recommendation_status": "RECOMMEND_PENDING_OPERATOR_DECISION",
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
        "computation_authorization_review_only": True,
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
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_computation_authorization_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "authorization_review_id",
        "review_type",
        "operator_id",
        "source_schema_validation_complete_review_hash",
        "source_fixture_creation_receipt_hash",
        "intended_lane",
        "review_stage",
        "fixture_corpus_readiness_review",
        "schema_validation_completion_review",
        "computation_scope_review",
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
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_review_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "unknown_operator_id"
        )
    if (
        packet["source_schema_validation_complete_review_hash"]
        != SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_source_schema_validation_complete_review_hash"
        )
    if (
        packet["source_fixture_creation_receipt_hash"]
        != SOURCE_FIXTURE_CREATION_RECEIPT_HASH
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_source_fixture_creation_receipt_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "unknown_intended_lane"
        )
    if packet["review_stage"] not in ALLOWED_REVIEW_STAGE:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "unknown_review_stage"
        )

    fcrr = packet["fixture_corpus_readiness_review"]
    if fcrr.get("total_fixtures_verified") != 14:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "fixture_corpus_total_mismatch"
        )
    if fcrr.get("corpus_readiness_status") != "READY":
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "fixture_corpus_not_ready"
        )
    if fcrr.get("source_gate_hash") != SOURCE_GATE_HASH:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "fixture_corpus_gate_hash_mismatch"
        )

    svcr = packet["schema_validation_completion_review"]
    if not svcr.get("schema_validation_executed"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "schema_validation_not_executed"
        )
    if not svcr.get("all_14_fixtures_passed"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "not_all_14_fixtures_passed"
        )
    if not svcr.get("no_metric_values_present"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "metric_values_present_in_corpus"
        )
    if not svcr.get("no_expected_distances_present"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "expected_distances_present_in_corpus"
        )
    if not svcr.get("complete_review_sealed"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "complete_review_not_sealed"
        )
    if (
        svcr.get("source_schema_validation_complete_review_hash")
        != SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "schema_validation_completion_review_hash_mismatch"
        )

    csr = packet["computation_scope_review"]
    if csr.get("computation_scope_status") != "ELIGIBLE_FOR_BOUNDED_AUTHORIZATION":
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "computation_scope_not_eligible"
        )

    alr = packet["authority_lock_review"]
    if not alr.get("all_authority_locks_preserved"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "authority_locks_not_preserved"
        )
    if alr.get("source_gate_hash_verified") != SOURCE_GATE_HASH:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "authority_lock_gate_hash_mismatch"
        )
    if alr.get("authority_lock_review_status") != "PASS":
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "authority_lock_review_not_pass"
        )

    oar = packet["operator_authorization_requirement"]
    if not oar.get("operator_decision_required"):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "operator_decision_not_marked_required"
        )
    if oar.get("authorization_cannot_self_activate") is not True:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "authorization_self_activate_guard_missing"
        )

    ar = packet["authorization_recommendation"]
    if ar.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "wasserstein_computation_must_remain_unauthorized"
        )
    if ar.get("emits_metric_values") is not False:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "emits_metric_values_must_be_false"
        )
    if ar.get("expected_wasserstein_distances_added") is not False:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "expected_distances_must_be_false"
        )
    if ar.get("forecast_influence") is not False:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "forecast_influence_must_be_false"
        )

    al = packet["authority_locks"]
    if al.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "wasserstein_computation_authorized_must_be_false"
        )
    if al.get("computation_authorization_review_only") is not True:
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "computation_authorization_review_only_must_be_true"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_authority_locks"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_blocked_scopes"
        )

    if (
        packet["fixture_corpus_readiness_review"]
        != default_fixture_corpus_readiness_review()
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_fixture_corpus_readiness_review"
        )
    if (
        packet["schema_validation_completion_review"]
        != default_schema_validation_completion_review()
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_schema_validation_completion_review"
        )
    if packet["computation_scope_review"] != default_computation_scope_review():
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_computation_scope_review"
        )
    if packet["authority_lock_review"] != default_authority_lock_review():
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_authority_lock_review"
        )
    if (
        packet["operator_authorization_requirement"]
        != default_operator_authorization_requirement()
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_operator_authorization_requirement"
        )
    if (
        packet["authorization_recommendation"]
        != default_authorization_recommendation()
    ):
        raise WassersteinTestVectorComputationAuthorizationReviewError(
            "invalid_authorization_recommendation"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_computation_authorization_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_computation_authorization_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_computation_authorization_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_schema_validation_complete_review_hash": (
            SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
        ),
        "source_fixture_creation_receipt_hash": SOURCE_FIXTURE_CREATION_RECEIPT_HASH,
        "fixture_corpus_readiness_review": payload.get(
            "fixture_corpus_readiness_review",
            default_fixture_corpus_readiness_review(),
        ),
        "schema_validation_completion_review": payload.get(
            "schema_validation_completion_review",
            default_schema_validation_completion_review(),
        ),
        "computation_scope_review": payload.get(
            "computation_scope_review", default_computation_scope_review()
        ),
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
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_computation_authorization_review_hash(base)
    )
    validate_wasserstein_test_vector_computation_authorization_review(base)
    return _finalize(base)
