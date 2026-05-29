from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_creation_readiness_review import (
    SOURCE_DOSSIER_HASH,
    SOURCE_FIXTURE_PLAN_HASH,
    SOURCE_SCHEMA_PLAN_HASH,
    build_wasserstein_test_vector_fixture_creation_readiness_review,
    compute_wasserstein_test_vector_fixture_creation_readiness_review_hash,
    default_authority_lock_check,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_coverage_check,
    default_operator_review_requirement,
    default_plan_triad_presence_check,
    serialize_wasserstein_test_vector_fixture_creation_readiness_review,
)


def _payload() -> dict:
    return {
        "review_id": "wasserstein_test_vector_fixture_creation_readiness_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "FIXTURE_CREATION_READINESS_REVIEW_ONLY",
        "recommended_next_step": "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN",
        "provenance": {
            "source": "P48_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW",
            "evidence_refs": [
                "WassersteinTestVectorFixturePlan.v1:"
                "wasserstein_test_vector_fixture_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_creation_readiness_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    b = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_fixture_creation_readiness_review(
        a
    ) == serialize_wasserstein_test_vector_fixture_creation_readiness_review(b)


def test_default_sub_structures_deterministic() -> None:
    assert default_plan_triad_presence_check() == default_plan_triad_presence_check()
    assert default_fixture_coverage_check() == default_fixture_coverage_check()
    assert default_authority_lock_check() == default_authority_lock_check()
    assert default_operator_review_requirement() == default_operator_review_requirement()


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureCreationReadinessReview.v1"
    )
    assert (
        packet["review_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH
    assert packet["source_schema_plan_hash"] == SOURCE_SCHEMA_PLAN_HASH
    assert packet["source_dossier_hash"] == SOURCE_DOSSIER_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["review_stage"] == "FIXTURE_CREATION_READINESS_REVIEW_ONLY"


# ---------------------------------------------------------------------------
# Plan triad presence
# ---------------------------------------------------------------------------


def test_triad_all_present_and_validated() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    triad = packet["plan_triad_presence_check"]
    assert triad["valid_fixture_plan_present"] is True
    assert triad["invalid_fixture_plan_present"] is True
    assert triad["not_computable_fixture_plan_present"] is True
    assert triad["triad_complete"] is True
    assert triad["valid_fixture_plan_status"] == "PRESENT_AND_VALIDATED"
    assert triad["invalid_fixture_plan_status"] == "PRESENT_AND_VALIDATED"
    assert triad["not_computable_fixture_plan_status"] == "PRESENT_AND_VALIDATED"
    assert triad["source_fixture_plan_hash_verified"] is True
    assert triad["finding_status"] == "SATISFIED"


# ---------------------------------------------------------------------------
# Coverage check
# ---------------------------------------------------------------------------


def test_fixture_coverage_complete() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    cov = packet["fixture_coverage_check"]
    assert cov["valid_groups_covered"] == 5
    assert cov["invalid_groups_covered"] == 5
    assert cov["not_computable_groups_covered"] == 4
    assert cov["total_groups_covered"] == 14
    assert cov["coverage_complete"] is True
    assert cov["coverage_status"] == "COMPLETE"
    assert cov["finding_status"] == "SATISFIED"


# ---------------------------------------------------------------------------
# Authority lock check
# ---------------------------------------------------------------------------


def test_all_authority_locks_satisfied() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    lock = packet["authority_lock_check"]
    assert lock["all_locks_satisfied"] is True
    assert lock["lock_status"] == "ALL_LOCKS_SATISFIED"
    assert lock["finding_status"] == "SATISFIED"
    for key, val in lock.items():
        if key.endswith("_locked_false"):
            assert val is True, f"lock check field {key!r} must be True"


# ---------------------------------------------------------------------------
# Operator review requirement
# ---------------------------------------------------------------------------


def test_operator_review_required() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    op = packet["operator_review_requirement"]
    assert op["operator_review_required"] is True
    assert op["fixture_file_creation_authorized"] is False
    assert op["review_status"] == "REQUIRED"
    assert op["finding_status"] == "HELD_FOR_REVIEW"


def test_fixture_file_creation_must_be_unauthorized() -> None:
    p = _payload()
    req = default_operator_review_requirement()
    req["fixture_file_creation_authorized"] = True
    p["operator_review_requirement"] = req
    with pytest.raises(
        ValueError, match="fixture_file_creation_must_be_unauthorized"
    ):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_operator_review_must_be_required() -> None:
    p = _payload()
    req = default_operator_review_requirement()
    req["operator_review_required"] = False
    p["operator_review_requirement"] = req
    with pytest.raises(ValueError, match="operator_review_must_be_required"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_authority_locks_governance() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["fixture_creation_readiness_review_only"] is True
    assert locks["fixture_files_generated"] is False
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
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


# ---------------------------------------------------------------------------
# Locked map mutation guards
# ---------------------------------------------------------------------------


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["fixture_file_creation_authorized"] = True
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["fixture_files_generated"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_triad_check_mutation_raises() -> None:
    p = _payload()
    triad = default_plan_triad_presence_check()
    triad["triad_complete"] = False
    p["plan_triad_presence_check"] = triad
    with pytest.raises(ValueError, match="invalid_plan_triad_presence_check"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_coverage_check_mutation_raises() -> None:
    p = _payload()
    cov = default_fixture_coverage_check()
    cov["total_groups_covered"] = 10
    p["fixture_coverage_check"] = cov
    with pytest.raises(ValueError, match="invalid_fixture_coverage_check"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_lock_check_mutation_raises() -> None:
    p = _payload()
    lock = default_authority_lock_check()
    lock["all_locks_satisfied"] = False
    p["authority_lock_check"] = lock
    with pytest.raises(ValueError, match="invalid_authority_lock_check"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


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
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_unknown_triad_presence_status_raises() -> None:
    p = _payload()
    triad = default_plan_triad_presence_check()
    triad["valid_fixture_plan_status"] = "UNKNOWN"
    p["plan_triad_presence_check"] = triad
    with pytest.raises(ValueError, match="unknown_valid_fixture_plan_status"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_unknown_coverage_status_raises() -> None:
    p = _payload()
    cov = default_fixture_coverage_check()
    cov["coverage_status"] = "UNKNOWN"
    p["fixture_coverage_check"] = cov
    with pytest.raises(ValueError, match="unknown_coverage_status"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_unknown_lock_status_raises() -> None:
    p = _payload()
    lock = default_authority_lock_check()
    lock["lock_status"] = "UNKNOWN"
    p["authority_lock_check"] = lock
    with pytest.raises(ValueError, match="unknown_lock_status"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_test_vector_fixture_creation_readiness_review_hash(
        packet
    ) == compute_wasserstein_test_vector_fixture_creation_readiness_review_hash(altered)


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_creation_readiness_review(_payload())
    b = build_wasserstein_test_vector_fixture_creation_readiness_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler metric-value"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_creation_readiness_review(p)
