from __future__ import annotations

import pytest

from core.wasserstein_not_computable_fixture_implementation_plan import (
    build_wasserstein_not_computable_fixture_implementation_plan,
    compute_wasserstein_not_computable_fixture_implementation_plan_hash,
    default_fixture_constraints,
    default_not_computable_fixture_cases,
    default_not_computable_policy_plan,
    default_output_contract,
    default_validation_plan,
    serialize_wasserstein_not_computable_fixture_implementation_plan,
)
from core.wasserstein_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS


def _payload() -> dict:
    return {
        "plan_id": "wasserstein_not_computable_fixture_implementation_plan_001",
        "source_schema_plan_refs": [
            "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
        ],
        "source_dossier_refs": [
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "source_valid_fixture_plan_refs": [
            "WassersteinValidFixtureImplementationPlan.v1:"
            "wasserstein_valid_fixture_implementation_plan_001",
        ],
        "source_invalid_fixture_plan_refs": [
            "WassersteinInvalidFixtureImplementationPlan.v1:"
            "wasserstein_invalid_fixture_implementation_plan_001",
        ],
        "not_computable_fixture_scope": {
            "fixture_family": "MIXED_NOT_COMPUTABLE_FIXTURE_PLAN",
            "intended_lane": "SHADOW",
            "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "P46_WASSERSTEIN_NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN",
            "evidence_refs": [
                "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_not_computable_fixture_implementation_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    b = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_not_computable_fixture_implementation_plan(
        a
    ) == serialize_wasserstein_not_computable_fixture_implementation_plan(b)


def test_default_cases_deterministic() -> None:
    assert default_not_computable_fixture_cases() == default_not_computable_fixture_cases()


def test_constants_enforced() -> None:
    packet = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    assert (
        packet["schema_version"]
        == "WassersteinNotComputableFixtureImplementationPlan.v1"
    )
    assert (
        packet["plan_type"]
        == "WASSERSTEIN_NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN"
    )
    assert packet["operator_id"] == "WASSERSTEIN"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["not_computable_fixture_scope"].__setitem__(
                "fixture_family", "BAD"
            ),
            "unknown_fixture_family",
        ),
        (
            lambda p: p["not_computable_fixture_scope"].__setitem__(
                "intended_lane", "BAD"
            ),
            "unknown_intended_lane",
        ),
        (
            lambda p: p["not_computable_fixture_scope"].__setitem__(
                "implementation_stage", "BAD"
            ),
            "unknown_implementation_stage",
        ),
        (
            lambda p: p["not_computable_fixture_cases"].append(
                dict(p["not_computable_fixture_cases"][0])
            ),
            "duplicate_case_id",
        ),
        (
            lambda p: p["not_computable_fixture_cases"][0].__setitem__(
                "case_type", "BAD"
            ),
            "unknown_case_type",
        ),
        (
            lambda p: p["not_computable_fixture_cases"][0].__setitem__(
                "not_computable_reason", "BAD"
            ),
            "unknown_not_computable_reason",
        ),
        (
            lambda p: p["not_computable_fixture_cases"][0].__setitem__(
                "expected_state", "BAD"
            ),
            "unknown_expected_state",
        ),
        (
            lambda p: p["not_computable_fixture_cases"][0].__setitem__(
                "implementation_status", "BAD"
            ),
            "unknown_implementation_status",
        ),
    ],
)
def test_enum_and_duplicate_failures(mutator, err: str) -> None:
    p = _payload()
    p["not_computable_fixture_cases"] = default_not_computable_fixture_cases()
    mutator(p)
    with pytest.raises(ValueError, match=err):
        build_wasserstein_not_computable_fixture_implementation_plan(p)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["not_computable_policy_plan"] = default_not_computable_policy_plan()
    p["not_computable_policy_plan"]["runtime_not_computable_enabled"] = True
    with pytest.raises(ValueError, match="invalid_not_computable_policy_plan"):
        build_wasserstein_not_computable_fixture_implementation_plan(p)

    p = _payload()
    p["fixture_constraints"] = default_fixture_constraints()
    p["fixture_constraints"]["wasserstein_math_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_constraints"):
        build_wasserstein_not_computable_fixture_implementation_plan(p)

    p = _payload()
    p["validation_plan"] = default_validation_plan()
    p["validation_plan"]["requires_schema_validation"] = False
    with pytest.raises(ValueError, match="invalid_validation_plan"):
        build_wasserstein_not_computable_fixture_implementation_plan(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_wasserstein_outputs"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_wasserstein_not_computable_fixture_implementation_plan(p)

    p = _payload()
    p["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_wasserstein_not_computable_fixture_implementation_plan(p)


def test_all_governance_flags_false() -> None:
    packet = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert packet["governance_flags"][flag] is False, flag


def test_output_contract_emits_nc_plan() -> None:
    packet = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    assert packet["output_contract"]["emits_not_computable_fixture_plan"] is True
    assert packet["output_contract"]["emits_not_computable_policy_metadata"] is True
    assert packet["output_contract"]["emits_wasserstein_outputs"] is False


def test_nc_cases_coverage() -> None:
    packet = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    reasons = {c["not_computable_reason"] for c in packet["not_computable_fixture_cases"]}
    assert "EMPTY_INPUT" in reasons
    assert "GROUND_METRIC_UNDECLARED" in reasons
    assert "NUMERICAL_POLICY_MISSING" in reasons
    assert "DIMENSIONALITY_UNDECLARED" in reasons


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_not_computable_fixture_implementation_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_not_computable_fixture_implementation_plan_hash(
        packet
    ) == compute_wasserstein_not_computable_fixture_implementation_plan_hash(altered)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["plan_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_not_computable_fixture_implementation_plan(p)
