from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_plan import (
    SOURCE_SCHEMA_PLAN_HASH,
    build_wasserstein_test_vector_fixture_plan,
    compute_wasserstein_test_vector_fixture_plan_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_determinism_requirements,
    default_invalid_fixture_plan,
    default_not_computable_fixture_plan,
    default_numerical_policy_requirements,
    default_valid_fixture_plan,
    serialize_wasserstein_test_vector_fixture_plan,
)


def _payload() -> dict:
    return {
        "fixture_plan_id": "wasserstein_test_vector_fixture_plan_001",
        "intended_lane": "SHADOW",
        "fixture_stage": "FIXTURE_PLAN_ONLY",
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW"
        ),
        "provenance": {
            "source": "P47_WASSERSTEIN_TEST_VECTOR_FIXTURE_PLAN",
            "evidence_refs": [
                "WassersteinTestVectorSchemaPlan.v1:"
                "wasserstein_test_vector_schema_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_test_vector_fixture_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_plan(_payload())
    b = build_wasserstein_test_vector_fixture_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_fixture_plan(
        a
    ) == serialize_wasserstein_test_vector_fixture_plan(b)


def test_default_plans_are_deterministic() -> None:
    assert default_valid_fixture_plan() == default_valid_fixture_plan()
    assert default_invalid_fixture_plan() == default_invalid_fixture_plan()
    assert default_not_computable_fixture_plan() == default_not_computable_fixture_plan()


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    assert packet["schema_version"] == "WassersteinTestVectorFixturePlan.v1"
    assert packet["fixture_plan_type"] == "WASSERSTEIN_TEST_VECTOR_FIXTURE_PLAN"
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_schema_plan_hash"] == SOURCE_SCHEMA_PLAN_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["fixture_stage"] == "FIXTURE_PLAN_ONLY"


# ---------------------------------------------------------------------------
# Schema group coverage
# ---------------------------------------------------------------------------


def test_valid_plan_covers_all_five_groups() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    group_ids = {e["schema_group_id"] for e in packet["valid_fixture_plan"]}
    assert group_ids == {"valid-001", "valid-002", "valid-003", "valid-004", "valid-005"}


def test_invalid_plan_covers_all_five_groups() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    group_ids = {e["schema_group_id"] for e in packet["invalid_fixture_plan"]}
    assert group_ids == {
        "invalid-001",
        "invalid-002",
        "invalid-003",
        "invalid-004",
        "invalid-005",
    }


def test_nc_plan_covers_all_four_groups() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    group_ids = {e["schema_group_id"] for e in packet["not_computable_fixture_plan"]}
    assert group_ids == {"nc-001", "nc-002", "nc-003", "nc-004"}


def test_valid_schema_types_present() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    types = {e["schema_type"] for e in packet["valid_fixture_plan"]}
    assert "DISTRIBUTION_PAIR_SCHEMA" in types
    assert "REFERENCE_VECTOR_SCHEMA" in types
    assert "GROUND_METRIC_SCHEMA" in types
    assert "DEGENERATE_DISTRIBUTION_SCHEMA" in types
    assert "WEIGHTED_HISTOGRAM_SCHEMA" in types


def test_invalid_reasons_present() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    reasons = {e["invalid_reason"] for e in packet["invalid_fixture_plan"]}
    assert "MISSING_REQUIRED_FIELD" in reasons
    assert "EMPTY_DISTRIBUTION" in reasons
    assert "INVALID_WEIGHT_SUM" in reasons
    assert "DIMENSION_MISMATCH" in reasons
    assert "GROUND_METRIC_UNDECLARED" in reasons


def test_nc_reasons_present() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    reasons = {e["not_computable_reason"] for e in packet["not_computable_fixture_plan"]}
    assert "EMPTY_INPUT" in reasons
    assert "GROUND_METRIC_UNDECLARED" in reasons
    assert "NUMERICAL_POLICY_MISSING" in reasons
    assert "DIMENSIONALITY_UNDECLARED" in reasons


def test_all_entries_planned_only() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    for entry in (
        packet["valid_fixture_plan"]
        + packet["invalid_fixture_plan"]
        + packet["not_computable_fixture_plan"]
    ):
        assert entry["implementation_status"] == "PLANNED_ONLY", (
            f"{entry['fixture_plan_id']} has wrong implementation_status"
        )


def test_blocked_outputs_sorted() -> None:
    p = _payload()
    plan = default_valid_fixture_plan()
    plan[0]["blocked_outputs"] = ["z_out", "a_out"]
    p["valid_fixture_plan"] = plan
    packet = build_wasserstein_test_vector_fixture_plan(p)
    assert packet["valid_fixture_plan"][0]["blocked_outputs"] == ["a_out", "z_out"]


# ---------------------------------------------------------------------------
# Locked maps
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k}] must be False"


def test_authority_locks_governance() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["fixture_plan_only"] is True
    assert locks["wasserstein_computation_authorized"] is False
    assert locks["fixture_files_generated"] is False
    assert locks["emits_metric_values"] is False
    assert locks["expected_wasserstein_distances_added"] is False
    assert locks["forecast_influence"] is False
    assert locks["p43_surface_lanes_authorized"] is False
    assert locks["production_activation"] is False
    assert locks["canon_promotion"] is False
    assert locks["runtime_mutation"] is False
    assert locks["execution_authority"] is False
    assert locks["inference_authority"] is False


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["wasserstein_computation"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["wasserstein_computation_authorized"] = True
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_determinism_requirements_mutation_raises() -> None:
    p = _payload()
    p["determinism_requirements"] = default_determinism_requirements()
    p["determinism_requirements"]["nondeterministic_ordering_allowed"] = True
    with pytest.raises(ValueError, match="invalid_determinism_requirements"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_numerical_policy_mutation_raises() -> None:
    p = _payload()
    p["numerical_policy_requirements"] = default_numerical_policy_requirements()
    p["numerical_policy_requirements"]["metric_value_computation_allowed"] = True
    with pytest.raises(ValueError, match="invalid_numerical_policy_requirements"):
        build_wasserstein_test_vector_fixture_plan(p)


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("fixture_stage", "ACTIVE", "unknown_fixture_stage"),
    ],
)
def test_top_level_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_plan(p)


def test_unknown_valid_schema_group_id_raises() -> None:
    p = _payload()
    plan = default_valid_fixture_plan()
    plan[0] = dict(plan[0])
    plan[0]["schema_group_id"] = "valid-999"
    p["valid_fixture_plan"] = plan
    with pytest.raises(ValueError, match="unknown_valid_schema_group_id"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_unknown_invalid_reason_raises() -> None:
    p = _payload()
    plan = default_invalid_fixture_plan()
    plan[0] = dict(plan[0])
    plan[0]["invalid_reason"] = "BAD_REASON"
    p["invalid_fixture_plan"] = plan
    with pytest.raises(ValueError, match="unknown_invalid_reason"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_unknown_nc_reason_raises() -> None:
    p = _payload()
    plan = default_not_computable_fixture_plan()
    plan[0] = dict(plan[0])
    plan[0]["not_computable_reason"] = "BAD_REASON"
    p["not_computable_fixture_plan"] = plan
    with pytest.raises(ValueError, match="unknown_nc_reason"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_duplicate_valid_fixture_plan_id_raises() -> None:
    p = _payload()
    plan = default_valid_fixture_plan()
    plan.append(dict(plan[0]))
    p["valid_fixture_plan"] = plan
    with pytest.raises(ValueError, match="duplicate_valid_fixture_plan_id"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_duplicate_invalid_fixture_plan_id_raises() -> None:
    p = _payload()
    plan = default_invalid_fixture_plan()
    plan.append(dict(plan[0]))
    p["invalid_fixture_plan"] = plan
    with pytest.raises(ValueError, match="duplicate_invalid_fixture_plan_id"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_duplicate_nc_fixture_plan_id_raises() -> None:
    p = _payload()
    plan = default_not_computable_fixture_plan()
    plan.append(dict(plan[0]))
    p["not_computable_fixture_plan"] = plan
    with pytest.raises(ValueError, match="duplicate_nc_fixture_plan_id"):
        build_wasserstein_test_vector_fixture_plan(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_test_vector_fixture_plan_hash(
        packet
    ) == compute_wasserstein_test_vector_fixture_plan_hash(altered)


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_plan(_payload())
    b = build_wasserstein_test_vector_fixture_plan(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler metric-value"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_plan(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["fixture_plan_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_plan(p)
