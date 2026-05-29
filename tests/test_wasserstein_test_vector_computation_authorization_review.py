from __future__ import annotations

import pytest

from core.wasserstein_test_vector_computation_authorization_review import (
    SOURCE_FIXTURE_CREATION_RECEIPT_HASH,
    SOURCE_GATE_HASH,
    SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH,
    build_wasserstein_test_vector_computation_authorization_review,
    compute_wasserstein_test_vector_computation_authorization_review_hash,
    default_authority_lock_review,
    default_authority_locks,
    default_authorization_recommendation,
    default_blocked_scopes,
    default_computation_scope_review,
    default_fixture_corpus_readiness_review,
    default_operator_authorization_requirement,
    default_schema_validation_completion_review,
    serialize_wasserstein_test_vector_computation_authorization_review,
)


def _payload() -> dict:
    return {
        "authorization_review_id": (
            "wasserstein_test_vector_computation_authorization_review_001"
        ),
        "intended_lane": "SHADOW",
        "review_stage": "COMPUTATION_AUTHORIZATION_REVIEW_ONLY",
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_OPERATOR_DECISION"
        ),
        "provenance": {
            "source": (
                "P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_REVIEW"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureSchemaValidationCompleteReview.v1:"
                "wasserstein_test_vector_fixture_schema_validation_complete_review_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_computation_authorization_review"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_computation_authorization_review(_payload())
    b = build_wasserstein_test_vector_computation_authorization_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_computation_authorization_review(_payload())
    b = build_wasserstein_test_vector_computation_authorization_review(_payload())
    assert serialize_wasserstein_test_vector_computation_authorization_review(
        a
    ) == serialize_wasserstein_test_vector_computation_authorization_review(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorComputationAuthorizationReview.v1"
    )
    assert (
        packet["review_type"]
        == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_REVIEW"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert (
        packet["source_schema_validation_complete_review_hash"]
        == SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
    )
    assert (
        packet["source_fixture_creation_receipt_hash"]
        == SOURCE_FIXTURE_CREATION_RECEIPT_HASH
    )
    assert packet["intended_lane"] == "SHADOW"
    assert packet["review_stage"] == "COMPUTATION_AUTHORIZATION_REVIEW_ONLY"


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is False


def test_review_only_lock_true() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    assert packet["authority_locks"]["computation_authorization_review_only"] is True


def test_computation_authorized_true_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["wasserstein_computation_authorized"] = True
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="wasserstein_computation_authorized_must_be_false"
    ):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["advisory_only"] = False
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["wasserstein_computation"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Fixture corpus readiness review
# ---------------------------------------------------------------------------


def test_fixture_corpus_readiness() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    fcrr = packet["fixture_corpus_readiness_review"]
    assert fcrr["total_fixtures_verified"] == 14
    assert fcrr["corpus_readiness_status"] == "READY"
    assert fcrr["all_gate_hashes_pinned"] is True
    assert fcrr["source_gate_hash"] == SOURCE_GATE_HASH


def test_corpus_total_mismatch_raises() -> None:
    p = _payload()
    fcrr = default_fixture_corpus_readiness_review()
    fcrr["total_fixtures_verified"] = 10
    p["fixture_corpus_readiness_review"] = fcrr
    with pytest.raises(ValueError, match="fixture_corpus_total_mismatch"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_corpus_not_ready_raises() -> None:
    p = _payload()
    fcrr = default_fixture_corpus_readiness_review()
    fcrr["corpus_readiness_status"] = "BLOCKED"
    p["fixture_corpus_readiness_review"] = fcrr
    with pytest.raises(ValueError, match="fixture_corpus_not_ready"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_corpus_review_mutation_raises() -> None:
    p = _payload()
    fcrr = default_fixture_corpus_readiness_review()
    fcrr["all_fixture_files_present"] = False
    p["fixture_corpus_readiness_review"] = fcrr
    with pytest.raises(ValueError, match="invalid_fixture_corpus_readiness_review"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Schema validation completion review
# ---------------------------------------------------------------------------


def test_schema_validation_completion_review() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    svcr = packet["schema_validation_completion_review"]
    assert svcr["schema_validation_executed"] is True
    assert svcr["all_14_fixtures_passed"] is True
    assert svcr["no_metric_values_present"] is True
    assert svcr["no_expected_distances_present"] is True
    assert svcr["complete_review_sealed"] is True
    assert svcr["operator_approval_on_record"] is True
    assert (
        svcr["source_schema_validation_complete_review_hash"]
        == SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
    )


def test_schema_validation_not_executed_raises() -> None:
    p = _payload()
    svcr = default_schema_validation_completion_review()
    svcr["schema_validation_executed"] = False
    p["schema_validation_completion_review"] = svcr
    with pytest.raises(ValueError, match="schema_validation_not_executed"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_metric_values_present_raises() -> None:
    p = _payload()
    svcr = default_schema_validation_completion_review()
    svcr["no_metric_values_present"] = False
    p["schema_validation_completion_review"] = svcr
    with pytest.raises(ValueError, match="metric_values_present_in_corpus"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_expected_distances_present_raises() -> None:
    p = _payload()
    svcr = default_schema_validation_completion_review()
    svcr["no_expected_distances_present"] = False
    p["schema_validation_completion_review"] = svcr
    with pytest.raises(ValueError, match="expected_distances_present_in_corpus"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Computation scope review
# ---------------------------------------------------------------------------


def test_computation_scope_eligible() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    csr = packet["computation_scope_review"]
    assert csr["computation_scope"] == "BOUNDED_FIXTURE_ONLY"
    assert csr["computation_scope_status"] == "ELIGIBLE_FOR_BOUNDED_AUTHORIZATION"
    assert "p43_surface_lanes" in csr["excluded_scopes"]
    assert "metric_value_emission" in csr["excluded_scopes"]


def test_scope_not_eligible_raises() -> None:
    p = _payload()
    csr = default_computation_scope_review()
    csr["computation_scope_status"] = "BLOCKED"
    p["computation_scope_review"] = csr
    with pytest.raises(ValueError, match="computation_scope_not_eligible"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Authority lock review
# ---------------------------------------------------------------------------


def test_authority_lock_review_pass() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    alr = packet["authority_lock_review"]
    assert alr["all_authority_locks_preserved"] is True
    assert alr["no_execution_authority"] is True
    assert alr["no_runtime_mutation"] is True
    assert alr["source_gate_hash_verified"] == SOURCE_GATE_HASH


def test_authority_locks_not_preserved_raises() -> None:
    p = _payload()
    alr = default_authority_lock_review()
    alr["all_authority_locks_preserved"] = False
    p["authority_lock_review"] = alr
    with pytest.raises(ValueError, match="authority_locks_not_preserved"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Operator authorization requirement
# ---------------------------------------------------------------------------


def test_operator_decision_required() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    oar = packet["operator_authorization_requirement"]
    assert oar["operator_decision_required"] is True
    assert oar["authorization_cannot_self_activate"] is True
    assert oar["current_authorization_state"] == "PENDING_OPERATOR_DECISION"
    assert (
        oar["required_artifact_type"]
        == "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_OPERATOR_DECISION"
    )


def test_operator_decision_not_required_raises() -> None:
    p = _payload()
    oar = default_operator_authorization_requirement()
    oar["operator_decision_required"] = False
    p["operator_authorization_requirement"] = oar
    with pytest.raises(ValueError, match="operator_decision_not_marked_required"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_self_activate_guard_missing_raises() -> None:
    p = _payload()
    oar = default_operator_authorization_requirement()
    oar["authorization_cannot_self_activate"] = False
    p["operator_authorization_requirement"] = oar
    with pytest.raises(ValueError, match="authorization_self_activate_guard_missing"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Authorization recommendation
# ---------------------------------------------------------------------------


def test_recommendation_recommends_authorization() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    ar = packet["authorization_recommendation"]
    assert ar["recommend_wasserstein_computation_authorization"] is True
    assert ar["wasserstein_computation_authorized"] is False
    assert ar["emits_metric_values"] is False
    assert ar["expected_wasserstein_distances_added"] is False
    assert ar["forecast_influence"] is False
    assert (
        ar["authorization_recommendation_status"]
        == "RECOMMEND_PENDING_OPERATOR_DECISION"
    )


def test_recommendation_computation_authorized_raises() -> None:
    p = _payload()
    ar = default_authorization_recommendation()
    ar["wasserstein_computation_authorized"] = True
    p["authorization_recommendation"] = ar
    with pytest.raises(
        ValueError, match="wasserstein_computation_must_remain_unauthorized"
    ):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_recommendation_metric_value_raises() -> None:
    p = _payload()
    ar = default_authorization_recommendation()
    ar["emits_metric_values"] = True
    p["authorization_recommendation"] = ar
    with pytest.raises(ValueError, match="emits_metric_values_must_be_false"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_recommendation_mutation_raises() -> None:
    p = _payload()
    ar = default_authorization_recommendation()
    ar["recommend_wasserstein_computation_authorization"] = False
    p["authorization_recommendation"] = ar
    with pytest.raises(ValueError, match="invalid_authorization_recommendation"):
        build_wasserstein_test_vector_computation_authorization_review(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_computation_authorization_review(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_computation_authorization_review_hash(packet)
        == compute_wasserstein_test_vector_computation_authorization_review_hash(
            altered
        )
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_computation_authorization_review(_payload())
    b = build_wasserstein_test_vector_computation_authorization_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_computation_authorization_review(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["authorization_review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_computation_authorization_review(p)


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("review_stage", "ACTIVE", "unknown_review_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_computation_authorization_review(p)
