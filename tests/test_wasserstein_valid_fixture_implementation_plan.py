from __future__ import annotations

import pytest

from core.wasserstein_valid_fixture_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    build_wasserstein_valid_fixture_implementation_plan,
    compute_wasserstein_valid_fixture_implementation_plan_hash,
    default_fixture_constraints,
    default_fixture_manifest_plan,
    default_output_contract,
    default_valid_fixture_cases,
    default_validation_plan,
    serialize_wasserstein_valid_fixture_implementation_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "wasserstein_valid_fixture_implementation_plan_001",
        "source_schema_plan_refs": [
            "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
        ],
        "source_dossier_refs": [
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "valid_fixture_scope": {
            "fixture_family": "MIXED_VALID_FIXTURE_PLAN",
            "intended_lane": "SHADOW",
            "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "P46_WASSERSTEIN_VALID_FIXTURE_IMPLEMENTATION_PLAN",
            "evidence_refs": [
                "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_valid_fixture_implementation_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_valid_fixture_implementation_plan(_payload())
    b = build_wasserstein_valid_fixture_implementation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_valid_fixture_implementation_plan(
        a
    ) == serialize_wasserstein_valid_fixture_implementation_plan(b)


def test_default_cases_deterministic() -> None:
    assert default_valid_fixture_cases() == default_valid_fixture_cases()


def test_constants_enforced() -> None:
    packet = build_wasserstein_valid_fixture_implementation_plan(_payload())
    assert packet["schema_version"] == "WassersteinValidFixtureImplementationPlan.v1"
    assert packet["plan_type"] == "WASSERSTEIN_VALID_FIXTURE_IMPLEMENTATION_PLAN"
    assert packet["operator_id"] == "WASSERSTEIN"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["valid_fixture_scope"].__setitem__("fixture_family", "BAD"),
            "unknown_fixture_family",
        ),
        (
            lambda p: p["valid_fixture_scope"].__setitem__("intended_lane", "BAD"),
            "unknown_intended_lane",
        ),
        (
            lambda p: p["valid_fixture_scope"].__setitem__("implementation_stage", "BAD"),
            "unknown_implementation_stage",
        ),
        (
            lambda p: p["valid_fixture_cases"].append(dict(p["valid_fixture_cases"][0])),
            "duplicate_case_id",
        ),
        (
            lambda p: p["valid_fixture_cases"][0].__setitem__("case_type", "BAD"),
            "unknown_case_type",
        ),
        (
            lambda p: p["valid_fixture_cases"][0].__setitem__("ground_metric", "BAD"),
            "unknown_ground_metric",
        ),
        (
            lambda p: p["valid_fixture_cases"][0].__setitem__("implementation_status", "BAD"),
            "unknown_implementation_status",
        ),
        (
            lambda p: p["valid_fixture_cases"][0].__setitem__("dimensionality", 0),
            "invalid_dimensionality",
        ),
    ],
)
def test_enum_and_duplicate_failures(mutator, err: str) -> None:
    p = _payload()
    p["valid_fixture_cases"] = default_valid_fixture_cases()
    mutator(p)
    with pytest.raises(ValueError, match=err):
        build_wasserstein_valid_fixture_implementation_plan(p)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["fixture_manifest_plan"] = default_fixture_manifest_plan()
    p["fixture_manifest_plan"]["fixture_files_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_manifest_plan"):
        build_wasserstein_valid_fixture_implementation_plan(p)

    p = _payload()
    p["fixture_constraints"] = default_fixture_constraints()
    p["fixture_constraints"]["wasserstein_math_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_constraints"):
        build_wasserstein_valid_fixture_implementation_plan(p)

    p = _payload()
    p["validation_plan"] = default_validation_plan()
    p["validation_plan"]["requires_schema_validation"] = False
    with pytest.raises(ValueError, match="invalid_validation_plan"):
        build_wasserstein_valid_fixture_implementation_plan(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_wasserstein_outputs"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_wasserstein_valid_fixture_implementation_plan(p)

    p = _payload()
    p["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_wasserstein_valid_fixture_implementation_plan(p)


def test_all_governance_flags_false() -> None:
    packet = build_wasserstein_valid_fixture_implementation_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert packet["governance_flags"][flag] is False, flag


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler metric-value"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_valid_fixture_implementation_plan(p)


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_valid_fixture_implementation_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_valid_fixture_implementation_plan_hash(
        packet
    ) == compute_wasserstein_valid_fixture_implementation_plan_hash(altered)


def test_scope_change_changes_hash() -> None:
    p2 = _payload()
    p2["valid_fixture_scope"]["intended_lane"] = "PROJECTION"
    a = build_wasserstein_valid_fixture_implementation_plan(_payload())
    b = build_wasserstein_valid_fixture_implementation_plan(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_output_contract_emits_valid_plan() -> None:
    packet = build_wasserstein_valid_fixture_implementation_plan(_payload())
    assert packet["output_contract"]["emits_valid_fixture_plan"] is True
    assert packet["output_contract"]["emits_fixture_case_metadata"] is True
    assert packet["output_contract"]["emits_wasserstein_outputs"] is False
    assert packet["output_contract"]["emits_metric_values"] is False


def test_valid_cases_coverage() -> None:
    packet = build_wasserstein_valid_fixture_implementation_plan(_payload())
    case_types = {c["case_type"] for c in packet["valid_fixture_cases"]}
    assert "REFERENCE_VECTOR_CASE" in case_types
    assert "DISTRIBUTION_PAIR_CASE" in case_types
    assert "DEGENERATE_DISTRIBUTION_CASE" in case_types
    assert "EQUAL_DISTRIBUTION_CASE" in case_types


def test_blocked_outputs_sorted() -> None:
    p = _payload()
    cases = default_valid_fixture_cases()
    cases[0]["blocked_outputs"] = ["z_out", "a_out"]
    p["valid_fixture_cases"] = cases
    packet = build_wasserstein_valid_fixture_implementation_plan(p)
    assert packet["valid_fixture_cases"][0]["blocked_outputs"] == ["a_out", "z_out"]


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["plan_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_valid_fixture_implementation_plan(p)
