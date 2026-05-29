from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_schema_validation_complete_review import (
    SOURCE_GATE_HASH,
    SOURCE_VALIDATION_EXECUTION_HASH,
    SOURCE_VALIDATION_PLAN_HASH,
    build_wasserstein_test_vector_fixture_schema_validation_complete_review,
    compute_wasserstein_test_vector_fixture_schema_validation_complete_review_hash,
    default_authority_lock_review,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_count_review,
    default_no_expected_distance_review,
    default_no_metric_value_review,
    default_schema_group_review,
    default_validation_completion_summary,
    default_validation_coverage_review,
    serialize_wasserstein_test_vector_fixture_schema_validation_complete_review,
)


def _payload() -> dict:
    return {
        "review_id": (
            "wasserstein_test_vector_fixture_schema_validation_complete_review_001"
        ),
        "intended_lane": "SHADOW",
        "review_stage": "FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_ONLY",
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_COMPUTATION_AUTHORIZATION_REVIEW"
        ),
        "provenance": {
            "source": (
                "P56_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureSchemaValidationExecution.v1:"
                "wasserstein_test_vector_fixture_schema_validation_execution_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_schema_validation_complete_review"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    b = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    b = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    assert serialize_wasserstein_test_vector_fixture_schema_validation_complete_review(
        a
    ) == serialize_wasserstein_test_vector_fixture_schema_validation_complete_review(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureSchemaValidationCompleteReview.v1"
    )
    assert (
        packet["review_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_validation_execution_hash"] == SOURCE_VALIDATION_EXECUTION_HASH
    assert packet["source_validation_plan_hash"] == SOURCE_VALIDATION_PLAN_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["review_stage"] == "FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_ONLY"


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_fixture_schema_validation_executed_true() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    assert packet["authority_locks"]["fixture_schema_validation_executed"] is True


def test_wasserstein_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is False


def test_complete_review_only_lock() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    assert (
        packet["authority_locks"]["fixture_schema_validation_complete_review_only"]
        is True
    )


def test_executed_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["fixture_schema_validation_executed"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="fixture_schema_validation_executed_must_be_true"
    ):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


def test_computation_authorized_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["wasserstein_computation_authorized"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="wasserstein_computation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["advisory_only"] = False
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["emits_metric_values"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Fixture count review
# ---------------------------------------------------------------------------


def test_fixture_count_review_values() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    fcr = packet["fixture_count_review"]
    assert fcr["total_fixtures_reviewed"] == 14
    assert fcr["total_fixtures_validated"] == 14
    assert fcr["valid_fixtures_confirmed"] == 5
    assert fcr["invalid_fixtures_confirmed"] == 5
    assert fcr["not_computable_fixtures_confirmed"] == 4
    assert fcr["count_review_status"] == "PASS"


def test_fixture_count_review_total_mismatch_raises() -> None:
    p = _payload()
    fcr = default_fixture_count_review()
    fcr["total_fixtures_reviewed"] = 10
    p["fixture_count_review"] = fcr
    with pytest.raises(ValueError, match="fixture_count_review_total_mismatch"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


def test_fixture_count_review_mutation_raises() -> None:
    p = _payload()
    fcr = default_fixture_count_review()
    fcr["count_review_status"] = "FAIL"
    p["fixture_count_review"] = fcr
    with pytest.raises(ValueError, match="fixture_count_review_not_pass"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Validation coverage review
# ---------------------------------------------------------------------------


def test_coverage_review_pass() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    vcr = packet["validation_coverage_review"]
    assert vcr["all_plan_checks_executed"] is True
    assert vcr["coverage_review_status"] == "PASS"


def test_coverage_review_mutation_raises() -> None:
    p = _payload()
    vcr = default_validation_coverage_review()
    vcr["all_plan_checks_executed"] = False
    p["validation_coverage_review"] = vcr
    with pytest.raises(ValueError, match="not_all_plan_checks_executed"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Schema group review
# ---------------------------------------------------------------------------


def test_schema_group_review_all_groups() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    sgr = packet["schema_group_review"]
    assert len(sgr["valid_groups_covered"]) == 5
    assert len(sgr["invalid_groups_covered"]) == 5
    assert len(sgr["not_computable_groups_covered"]) == 4
    assert sgr["all_declared_groups_covered"] is True
    assert sgr["schema_group_review_status"] == "PASS"


def test_schema_group_review_mutation_raises() -> None:
    p = _payload()
    sgr = default_schema_group_review()
    sgr["all_declared_groups_covered"] = False
    p["schema_group_review"] = sgr
    with pytest.raises(ValueError, match="not_all_schema_groups_covered"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# No metric value / no expected distance reviews
# ---------------------------------------------------------------------------


def test_no_metric_value_review() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    nmvr = packet["no_metric_value_review"]
    assert nmvr["violations_found"] == 0
    assert nmvr["all_false_confirmed"] is True
    assert nmvr["total_fixtures_scanned"] == 14


def test_no_expected_distance_review() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    nedr = packet["no_expected_distance_review"]
    assert nedr["violations_found"] == 0
    assert nedr["all_false_confirmed"] is True


def test_metric_violation_raises() -> None:
    p = _payload()
    nmvr = default_no_metric_value_review()
    nmvr["violations_found"] = 1
    nmvr["all_false_confirmed"] = False
    p["no_metric_value_review"] = nmvr
    with pytest.raises(ValueError, match="metric_value_violation_in_review"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


def test_distance_violation_raises() -> None:
    p = _payload()
    nedr = default_no_expected_distance_review()
    nedr["violations_found"] = 1
    nedr["all_false_confirmed"] = False
    p["no_expected_distance_review"] = nedr
    with pytest.raises(ValueError, match="expected_distance_violation_in_review"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Authority lock review
# ---------------------------------------------------------------------------


def test_authority_lock_review_gate_hash() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    alr = packet["authority_lock_review"]
    assert alr["gate_hash_all_pinned"] is True
    assert alr["source_gate_hash_verified"] == SOURCE_GATE_HASH
    assert alr["authority_lock_review_status"] == "PASS"


def test_authority_lock_review_mutation_raises() -> None:
    p = _payload()
    alr = default_authority_lock_review()
    alr["gate_hash_all_pinned"] = False
    p["authority_lock_review"] = alr
    with pytest.raises(ValueError, match="gate_hash_not_all_pinned_in_review"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Validation completion summary
# ---------------------------------------------------------------------------


def test_completion_summary_status() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    vcs = packet["validation_completion_summary"]
    assert vcs["total_fixtures"] == 14
    assert vcs["total_passed"] == 14
    assert vcs["total_failed"] == 0
    assert vcs["all_obligations_satisfied"] is True
    assert vcs["schema_validation_complete"] is True
    assert (
        vcs["review_status"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW_READY"
    )


def test_completion_summary_mutation_raises() -> None:
    p = _payload()
    vcs = default_validation_completion_summary()
    vcs["all_obligations_satisfied"] = False
    p["validation_completion_summary"] = vcs
    with pytest.raises(ValueError, match="not_all_obligations_satisfied"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_fixture_schema_validation_complete_review_hash(
            packet
        )
        == compute_wasserstein_test_vector_fixture_schema_validation_complete_review_hash(
            altered
        )
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_schema_validation_complete_review(
        _payload()
    )
    b = build_wasserstein_test_vector_fixture_schema_validation_complete_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)


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
        build_wasserstein_test_vector_fixture_schema_validation_complete_review(p)
