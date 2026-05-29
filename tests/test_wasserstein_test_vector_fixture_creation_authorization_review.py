from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_creation_authorization_review import (
    SOURCE_PR_PLAN_HASH,
    SOURCE_READINESS_REVIEW_HASH,
    build_wasserstein_test_vector_fixture_creation_authorization_review,
    compute_wasserstein_test_vector_fixture_creation_authorization_review_hash,
    default_authority_lock_review,
    default_authority_locks,
    default_authorization_recommendation,
    default_batch_review,
    default_blocked_scopes,
    default_manifest_review,
    default_operator_authorization_requirement,
    serialize_wasserstein_test_vector_fixture_creation_authorization_review,
)


def _payload() -> dict:
    return {
        "authorization_review_id": (
            "wasserstein_test_vector_fixture_creation_authorization_review_001"
        ),
        "intended_lane": "SHADOW",
        "review_stage": "FIXTURE_CREATION_AUTHORIZATION_REVIEW_ONLY",
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_OPERATOR_DECISION"
        ),
        "provenance": {
            "source": (
                "P50_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureCreationPRPlan.v1:"
                "wasserstein_test_vector_fixture_creation_pr_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_creation_authorization_review"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_creation_authorization_review(_payload())
    b = build_wasserstein_test_vector_fixture_creation_authorization_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_fixture_creation_authorization_review(
        a
    ) == serialize_wasserstein_test_vector_fixture_creation_authorization_review(b)


def test_default_sub_structures_deterministic() -> None:
    assert default_manifest_review() == default_manifest_review()
    assert default_batch_review() == default_batch_review()
    assert default_authority_lock_review() == default_authority_lock_review()
    assert (
        default_operator_authorization_requirement()
        == default_operator_authorization_requirement()
    )
    assert default_authorization_recommendation() == default_authorization_recommendation()


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureCreationAuthorizationReview.v1"
    )
    assert (
        packet["review_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_pr_plan_hash"] == SOURCE_PR_PLAN_HASH
    assert packet["source_readiness_review_hash"] == SOURCE_READINESS_REVIEW_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["review_stage"] == "FIXTURE_CREATION_AUTHORIZATION_REVIEW_ONLY"


# ---------------------------------------------------------------------------
# Manifest review
# ---------------------------------------------------------------------------


def test_manifest_review_counts() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    mr = packet["manifest_review"]
    assert mr["total_entries_reviewed"] == 14
    assert mr["valid_entries"] == 5
    assert mr["invalid_entries"] == 5
    assert mr["not_computable_entries"] == 4
    assert mr["all_entries_planned"] is True
    assert mr["all_creation_unauthorized"] is True
    assert mr["duplicate_ids_detected"] is False
    assert mr["duplicate_paths_detected"] is False
    assert mr["manifest_status"] == "ALL_ENTRIES_PLANNED"
    assert mr["finding_status"] == "SATISFIED"


def test_manifest_review_mutation_raises() -> None:
    p = _payload()
    mr = default_manifest_review()
    mr["all_creation_unauthorized"] = False
    p["manifest_review"] = mr
    with pytest.raises(ValueError, match="invalid_manifest_review"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_unknown_manifest_status_raises() -> None:
    p = _payload()
    mr = default_manifest_review()
    mr["manifest_status"] = "UNKNOWN"
    p["manifest_review"] = mr
    with pytest.raises(ValueError, match="unknown_manifest_status"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Batch review
# ---------------------------------------------------------------------------


def test_batch_review_counts() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    br = packet["batch_review"]
    assert br["total_batches_reviewed"] == 3
    assert br["batch_01_valid_count"] == 5
    assert br["batch_02_invalid_count"] == 5
    assert br["batch_03_not_computable_count"] == 4
    assert br["all_batches_planned"] is True
    assert br["all_batches_creation_unauthorized"] is True
    assert br["batch_status"] == "ALL_BATCHES_PLANNED"
    assert br["finding_status"] == "SATISFIED"


def test_batch_review_mutation_raises() -> None:
    p = _payload()
    br = default_batch_review()
    br["all_batches_creation_unauthorized"] = False
    p["batch_review"] = br
    with pytest.raises(ValueError, match="invalid_batch_review"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_unknown_batch_status_raises() -> None:
    p = _payload()
    br = default_batch_review()
    br["batch_status"] = "UNKNOWN"
    p["batch_review"] = br
    with pytest.raises(ValueError, match="unknown_batch_status"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Authority lock review
# ---------------------------------------------------------------------------


def test_authority_lock_review_all_satisfied() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    alr = packet["authority_lock_review"]
    assert alr["all_locks_satisfied"] is True
    assert alr["lock_status"] == "ALL_LOCKS_SATISFIED"
    assert alr["finding_status"] == "SATISFIED"
    for key, val in alr.items():
        if key.endswith("_locked_false"):
            assert val is True, f"lock review field {key!r} must be True"


def test_authority_lock_review_mutation_raises() -> None:
    p = _payload()
    alr = default_authority_lock_review()
    alr["all_locks_satisfied"] = False
    p["authority_lock_review"] = alr
    with pytest.raises(ValueError, match="invalid_authority_lock_review"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_unknown_lock_status_raises() -> None:
    p = _payload()
    alr = default_authority_lock_review()
    alr["lock_status"] = "UNKNOWN"
    p["authority_lock_review"] = alr
    with pytest.raises(ValueError, match="unknown_lock_status"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Operator authorization requirement
# ---------------------------------------------------------------------------


def test_operator_authorization_requirement() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    oar = packet["operator_authorization_requirement"]
    assert oar["operator_decision_required"] is True
    assert oar["fixture_file_creation_authorized"] is False
    assert oar["operator_status"] == "REQUIRED"
    assert oar["finding_status"] == "HELD_FOR_REVIEW"


def test_fixture_file_creation_must_be_unauthorized() -> None:
    p = _payload()
    oar = default_operator_authorization_requirement()
    oar["fixture_file_creation_authorized"] = True
    p["operator_authorization_requirement"] = oar
    with pytest.raises(ValueError, match="fixture_file_creation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_operator_decision_must_be_required() -> None:
    p = _payload()
    oar = default_operator_authorization_requirement()
    oar["operator_decision_required"] = False
    p["operator_authorization_requirement"] = oar
    with pytest.raises(ValueError, match="operator_decision_must_be_required"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Authorization recommendation
# ---------------------------------------------------------------------------


def test_authorization_recommendation() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    rec = packet["authorization_recommendation"]
    assert rec["authorize_fixture_file_creation"] is True
    assert rec["fixture_file_creation_authorized"] is False
    assert rec["recommendation_status"] == "HELD_PENDING_OPERATOR_DECISION"
    assert "manifest_review:SATISFIED" in rec["basis"]
    assert "batch_review:SATISFIED" in rec["basis"]
    assert "authority_lock_review:SATISFIED" in rec["basis"]
    assert rec["blocking_conditions"] == []


def test_recommendation_fixture_file_creation_must_be_false() -> None:
    p = _payload()
    rec = default_authorization_recommendation()
    rec["fixture_file_creation_authorized"] = True
    p["authorization_recommendation"] = rec
    with pytest.raises(
        ValueError, match="recommendation_fixture_file_creation_must_be_false"
    ):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_authorization_recommendation_mutation_raises() -> None:
    p = _payload()
    rec = default_authorization_recommendation()
    rec["authorize_fixture_file_creation"] = False
    p["authorization_recommendation"] = rec
    with pytest.raises(ValueError, match="invalid_authorization_recommendation"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Authority locks / blocked scopes
# ---------------------------------------------------------------------------


def test_authority_locks_governance() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["fixture_creation_authorization_review_only"] is True
    assert locks["fixture_files_created"] is False
    assert locks["fixture_file_creation_authorized"] is False
    assert locks["wasserstein_computation_authorized"] is False
    assert locks["emits_metric_values"] is False
    assert locks["expected_wasserstein_distances_added"] is False
    assert locks["forecast_influence"] is False
    assert locks["p43_surface_lanes_authorized"] is False
    assert locks["production_activation"] is False
    assert locks["canon_promotion"] is False
    assert locks["runtime_mutation"] is False
    assert locks["execution_authority"] is False
    assert locks["inference_authority"] is False


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["fixture_file_creation_authorized"] = True
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["wasserstein_computation"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("review_stage", "ACTIVE", "unknown_review_stage"),
    ],
)
def test_top_level_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_unknown_recommendation_status_raises() -> None:
    p = _payload()
    rec = default_authorization_recommendation()
    rec["recommendation_status"] = "UNKNOWN"
    p["authorization_recommendation"] = rec
    with pytest.raises(ValueError, match="unknown_recommendation_status"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_authorization_review(
        _payload()
    )
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_test_vector_fixture_creation_authorization_review_hash(
        packet
    ) == compute_wasserstein_test_vector_fixture_creation_authorization_review_hash(
        altered
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_creation_authorization_review(_payload())
    b = build_wasserstein_test_vector_fixture_creation_authorization_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler cache"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["authorization_review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_creation_authorization_review(p)
