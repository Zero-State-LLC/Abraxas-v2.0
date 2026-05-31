from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_test_vector_schema_plan import (
    LOCKED_FALSE_FLAGS,
    LOCKED_TRUE_FLAGS,
    SOURCE_AUTH_HASH,
    HeavyTailTestVectorSchemaPlanValidationError,
    build_heavy_tail_test_vector_schema_plan,
    default_authority_lock_review,
    default_blocked_scope_review,
    default_closed_form_derivation_policy,
    default_fixture_corpus_strategy,
    default_invalid_fixture_schema_groups,
    default_not_computable_schema_groups,
    default_parameter_bound_policy,
    default_schema_field_definition,
    default_source_authorization_binding,
    default_valid_fixture_schema_groups,
    serialize_heavy_tail_test_vector_schema_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "heavy-tail-schema-plan-test-001",
        "source_authorization_binding": default_source_authorization_binding(),
        "schema_field_definition": default_schema_field_definition(),
        "parameter_bound_policy": default_parameter_bound_policy(),
        "valid_fixture_schema_groups": default_valid_fixture_schema_groups(),
        "invalid_fixture_schema_groups": default_invalid_fixture_schema_groups(),
        "not_computable_schema_groups": default_not_computable_schema_groups(),
        "closed_form_derivation_policy": default_closed_form_derivation_policy(),
        "fixture_corpus_strategy": default_fixture_corpus_strategy(),
        "authority_lock_review": default_authority_lock_review(),
        "blocked_scope_review": default_blocked_scope_review(),
        "recommended_next_step": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN",
        "provenance": {
            "source": "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN_TEST",
            "evidence_refs": [
                f"HeavyTailShadowStubImplementationAuthorization.v1:"
                f"heavy_tail_shadow_stub_implementation_authorization_001:"
                f"{SOURCE_AUTH_HASH}",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/heavy_tail_test_vector_schema_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-31T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_heavy_tail_test_vector_schema_plan(_payload())
    b = build_heavy_tail_test_vector_schema_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["schema_version"] == "HeavyTailTestVectorSchemaPlan.v1"


def test_plan_type_fixed() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["plan_type"] == "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN"


def test_plan_status_fixed() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["plan_status"] == "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN_COMPLETE"


def test_operator_id_fixed() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["operator_id"] == "HEAVY_TAIL"


def test_source_authorization_binding_hash() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["source_authorization_binding"]["authorization_canonical_hash"] == SOURCE_AUTH_HASH
    assert p["source_authorization_binding"]["hash_confirmed"] is True


def test_source_authorization_binding_implementation_flags() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    binding = p["source_authorization_binding"]
    assert binding["implementation_authorized_acknowledged"] is True
    assert binding["fixture_creation_authorized_acknowledged"] is True
    assert binding["fixture_corpus_not_created_in_this_plan"] is True
    assert binding["baseline_pack_update_authorized_acknowledged"] is True
    assert binding["baseline_pack_not_updated_in_this_plan"] is True
    assert binding["computation_not_performed"] is True
    assert binding["metric_values_not_emitted"] is True


def test_default_valid_fixture_schema_groups_count() -> None:
    assert len(default_valid_fixture_schema_groups()) == 6


def test_default_valid_groups_cover_alpha_2_and_alpha_3() -> None:
    labels = [g["group_label"] for g in default_valid_fixture_schema_groups()]
    assert "bounded_power_law_alpha_2" in labels
    assert "bounded_power_law_alpha_3" in labels


def test_default_valid_groups_cover_light_tail_control() -> None:
    labels = [g["group_label"] for g in default_valid_fixture_schema_groups()]
    assert "light_tail_control_sequence" in labels


def test_default_valid_groups_cover_outlier_and_monotone() -> None:
    labels = [g["group_label"] for g in default_valid_fixture_schema_groups()]
    assert "single_large_outlier_sequence" in labels
    assert "monotone_rank_frequency_sequence" in labels
    assert "repeated_equal_values_control" in labels


def test_default_invalid_fixture_schema_groups_count() -> None:
    assert len(default_invalid_fixture_schema_groups()) == 4


def test_default_invalid_groups_cover_missing_fields() -> None:
    labels = [g["group_label"] for g in default_invalid_fixture_schema_groups()]
    assert "missing_alpha" in labels
    assert "missing_sample_count" in labels
    assert "missing_sequence_values" in labels
    assert "invalid_expected_status" in labels


def test_default_not_computable_schema_groups_count() -> None:
    assert len(default_not_computable_schema_groups()) == 6


def test_default_not_computable_groups_cover_all_cases() -> None:
    labels = [g["group_label"] for g in default_not_computable_schema_groups()]
    assert "alpha_lte_zero" in labels
    assert "sample_count_zero" in labels
    assert "empty_sequence" in labels
    assert "non_finite_sequence_value" in labels
    assert "negative_sequence_value" in labels
    assert "sample_count_mismatch" in labels


def test_valid_groups_all_planned_only() -> None:
    for g in default_valid_fixture_schema_groups():
        assert g["implementation_status"] == "PLANNED_ONLY"


def test_not_computable_groups_all_not_computable_state() -> None:
    for g in default_not_computable_schema_groups():
        assert g["expected_state"] == "NOT_COMPUTABLE"


def test_all_locked_true_flags_true() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    for flag in LOCKED_TRUE_FLAGS:
        assert p["authority_lock_review"][flag] is True, f"{flag} must be True"


def test_all_locked_false_flags_false() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["authority_lock_review"][flag] is False, f"{flag} must be False"


def test_no_metric_emission() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["authority_lock_review"]["emits_metric_values"] is False
    assert p["authority_lock_review"]["forecast_influence"] is False
    assert p["authority_lock_review"]["execution_authority"] is False


def test_canonical_hash_64_hex() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_valid_groups_sorted_by_group_id() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    ids = [g["group_id"] for g in p["valid_fixture_schema_groups"]]
    assert ids == sorted(ids)


def test_invalid_groups_sorted_by_group_id() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    ids = [g["group_id"] for g in p["invalid_fixture_schema_groups"]]
    assert ids == sorted(ids)


def test_not_computable_groups_sorted_by_group_id() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    ids = [g["group_id"] for g in p["not_computable_schema_groups"]]
    assert ids == sorted(ids)


def test_schema_field_definition_covers_all_required_fields() -> None:
    sfd = default_schema_field_definition()
    required = {
        "alpha", "sample_count", "expected_tail_threshold",
        "sequence_values", "expected_tail_index",
        "expected_moment_summary", "expected_status", "expected_outcome_reason",
    }
    assert required <= sfd.keys()


def test_parameter_bound_policy_alpha_must_be_positive() -> None:
    policy = default_parameter_bound_policy()
    assert policy["alpha"]["min_exclusive"] == 0.0
    assert policy["sample_count"]["min_inclusive"] == 1


def test_closed_form_derivation_policy_no_computation_in_plan() -> None:
    pol = default_closed_form_derivation_policy()
    assert pol["computation_in_plan"] is False
    assert pol["plan_stage_computation_allowed"] is False
    assert pol["fixture_values_analytically_derived"] is True


def test_fixture_corpus_strategy_not_created_in_this_plan() -> None:
    strat = default_fixture_corpus_strategy()
    assert strat["fixture_corpus_created_in_this_plan"] is False
    assert strat["fixture_creation_authorized"] is True
    assert strat["shadow_stub_only"] is True
    assert strat["metric_emission_in_fixture_corpus"] is False
    assert strat["total_fixture_count_planned"] == 16


def test_recommended_next_step() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    assert p["recommended_next_step"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN"


def test_serialize_is_valid_json() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    raw = serialize_heavy_tail_test_vector_schema_plan(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "HeavyTailTestVectorSchemaPlan.v1"
    assert parsed["operator_id"] == "HEAVY_TAIL"


def test_blocked_scope_review_confirmed() -> None:
    p = build_heavy_tail_test_vector_schema_plan(_payload())
    bsr = p["blocked_scope_review"]
    assert bsr["confirmed"] is True
    assert bsr["computation"] == "BLOCKED"
    assert bsr["metric_emission"] == "BLOCKED"
    assert bsr["execution_authority"] == "BLOCKED"
    assert bsr["fixture_corpus_creation"] == "AUTHORIZED_BUT_NOT_IN_THIS_PLAN"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["source_authorization_binding"].__setitem__(
                "authorization_canonical_hash", "a" * 64
            ),
            "authorization_hash_mismatch",
        ),
        (
            lambda p: p["source_authorization_binding"].__setitem__(
                "hash_confirmed", False
            ),
            "authorization_hash_not_confirmed",
        ),
        (
            lambda p: p.__setitem__("valid_fixture_schema_groups", []),
            "valid_fixture_schema_groups_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("invalid_fixture_schema_groups", []),
            "invalid_fixture_schema_groups_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("not_computable_schema_groups", []),
            "not_computable_schema_groups_must_be_non_empty",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__("advisory_only", False),
            "authority_lock_must_be_true:advisory_only",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-metric-computation-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(HeavyTailTestVectorSchemaPlanValidationError, match=err):
        build_heavy_tail_test_vector_schema_plan(payload)


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/heavy_tail_test_vector_schema_plan_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "HeavyTailTestVectorSchemaPlan.v1"
    assert data["operator_id"] == "HEAVY_TAIL"
    assert data["plan_status"] == "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN_COMPLETE"
    assert len(data["canonical_hash"]) == 64
    assert (
        data["source_authorization_binding"]["authorization_canonical_hash"]
        == SOURCE_AUTH_HASH
    )
