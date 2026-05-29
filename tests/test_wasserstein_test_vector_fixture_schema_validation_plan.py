from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_schema_validation_plan import (
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_GATE_HASH,
    build_wasserstein_test_vector_fixture_schema_validation_plan,
    compute_wasserstein_test_vector_fixture_schema_validation_plan_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_schema_validation_scope,
    default_invalid_fixture_validation_plan,
    default_no_expected_distance_scan_plan,
    default_no_metric_value_scan_plan,
    default_not_computable_fixture_validation_plan,
    default_valid_fixture_validation_plan,
    serialize_wasserstein_test_vector_fixture_schema_validation_plan,
)


def _payload() -> dict:
    return {
        "validation_plan_id": (
            "wasserstein_test_vector_fixture_schema_validation_plan_001"
        ),
        "intended_lane": "SHADOW",
        "validation_stage": "FIXTURE_SCHEMA_VALIDATION_PLAN_ONLY",
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION"
        ),
        "provenance": {
            "source": (
                "P54_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureFileCreationCompleteReview.v1:"
                "wasserstein_test_vector_fixture_file_creation_complete_review_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_schema_validation_plan"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    b = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    b = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert serialize_wasserstein_test_vector_fixture_schema_validation_plan(
        a
    ) == serialize_wasserstein_test_vector_fixture_schema_validation_plan(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureSchemaValidationPlan.v1"
    )
    assert (
        packet["plan_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_complete_review_hash"] == SOURCE_COMPLETE_REVIEW_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["validation_stage"] == "FIXTURE_SCHEMA_VALIDATION_PLAN_ONLY"


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_fixture_schema_validation_executed_false() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert packet["authority_locks"]["fixture_schema_validation_executed"] is False


def test_wasserstein_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is False


def test_plan_only_lock_true() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert packet["authority_locks"]["fixture_schema_validation_plan_only"] is True


def test_validation_executed_true_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["fixture_schema_validation_executed"] = True
    with pytest.raises(
        ValueError, match="fixture_schema_validation_executed_must_be_false"
    ):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


def test_computation_authorized_true_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["wasserstein_computation_authorized"] = True
    with pytest.raises(ValueError, match="wasserstein_computation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["advisory_only"] = False
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["emits_metric_values"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Validation scope
# ---------------------------------------------------------------------------


def test_scope_total_fixtures() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert packet["fixture_schema_validation_scope"]["total_fixtures"] == 14


def test_scope_total_mismatch_raises() -> None:
    p = _payload()
    scope = default_fixture_schema_validation_scope()
    scope["total_fixtures"] = 10
    p["fixture_schema_validation_scope"] = scope
    with pytest.raises(ValueError, match="scope_total_fixtures_mismatch"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Valid fixture validation plan
# ---------------------------------------------------------------------------


def test_valid_plan_has_five_entries() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert len(packet["valid_fixture_validation_plan"]) == 5


def test_valid_plan_all_valid_ids() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    for entry in packet["valid_fixture_validation_plan"]:
        assert entry["fixture_id"].startswith("valid-")


def test_valid_plan_wrong_count_raises() -> None:
    p = _payload()
    p["valid_fixture_validation_plan"] = default_valid_fixture_validation_plan()[:3]
    with pytest.raises(ValueError, match="valid_plan_count_mismatch"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


def test_valid_plan_mutation_raises() -> None:
    p = _payload()
    plan = default_valid_fixture_validation_plan()
    plan[0]["fixture_group"] = "TAMPERED"
    p["valid_fixture_validation_plan"] = plan
    with pytest.raises(ValueError, match="invalid_valid_fixture_validation_plan"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Invalid fixture validation plan
# ---------------------------------------------------------------------------


def test_invalid_plan_has_five_entries() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert len(packet["invalid_fixture_validation_plan"]) == 5


def test_invalid_plan_all_invalid_ids() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    for entry in packet["invalid_fixture_validation_plan"]:
        assert entry["fixture_id"].startswith("invalid-")


def test_invalid_plan_mutation_raises() -> None:
    p = _payload()
    plan = default_invalid_fixture_validation_plan()
    plan[0]["fixture_group"] = "TAMPERED"
    p["invalid_fixture_validation_plan"] = plan
    with pytest.raises(ValueError, match="invalid_invalid_fixture_validation_plan"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Not-computable fixture validation plan
# ---------------------------------------------------------------------------


def test_nc_plan_has_four_entries() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    assert len(packet["not_computable_fixture_validation_plan"]) == 4


def test_nc_plan_all_nc_ids() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    for entry in packet["not_computable_fixture_validation_plan"]:
        assert entry["fixture_id"].startswith("nc-")


def test_nc_plan_mutation_raises() -> None:
    p = _payload()
    plan = default_not_computable_fixture_validation_plan()
    plan[0]["fixture_group"] = "TAMPERED"
    p["not_computable_fixture_validation_plan"] = plan
    with pytest.raises(ValueError, match="invalid_not_computable_fixture_validation_plan"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Scan plans
# ---------------------------------------------------------------------------


def test_no_metric_value_scan_plan_fields() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    plan = packet["no_metric_value_scan_plan"]
    assert plan["field"] == "metric_value_emitted"
    assert plan["expected_value"] is False
    assert plan["failure_action"] == "BLOCK_VALIDATION"


def test_no_expected_distance_scan_plan_fields() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    plan = packet["no_expected_distance_scan_plan"]
    assert plan["field"] == "expected_wasserstein_distance_included"
    assert plan["expected_value"] is False
    assert plan["failure_action"] == "BLOCK_VALIDATION"


def test_authority_lock_scan_plan_gate_hash() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    alsp = packet["authority_lock_scan_plan"]
    gate_hash_check = next(
        c for c in alsp["checks"] if c["name"] == "source_gate_hash_pinned"
    )
    assert gate_hash_check["expected_value"] == SOURCE_GATE_HASH


def test_metric_scan_plan_mutation_raises() -> None:
    p = _payload()
    plan = default_no_metric_value_scan_plan()
    plan["expected_value"] = True
    p["no_metric_value_scan_plan"] = plan
    with pytest.raises(ValueError, match="invalid_no_metric_value_scan_plan"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


def test_expected_distance_scan_plan_mutation_raises() -> None:
    p = _payload()
    plan = default_no_expected_distance_scan_plan()
    plan["expected_value"] = True
    p["no_expected_distance_scan_plan"] = plan
    with pytest.raises(ValueError, match="invalid_no_expected_distance_scan_plan"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("validation_stage", "ACTIVE", "unknown_validation_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_fixture_schema_validation_plan_hash(packet)
        == compute_wasserstein_test_vector_fixture_schema_validation_plan_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_schema_validation_plan(_payload())
    b = build_wasserstein_test_vector_fixture_schema_validation_plan(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["validation_plan_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_schema_validation_plan(p)
