from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_computation_implementation_plan import (
    IMPLEMENTATION_STAGE,
    OPERATOR_ID,
    PLAN_ID,
    PLAN_STATUS,
    SCHEMA_VERSION,
    SOURCE_AUTHORIZATION_REVIEW_HASH,
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    GeodesicComputationImplementationPlanValidationError,
    build_computation_implementation_plan,
    validate_computation_implementation_plan,
)


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_computation_implementation_plan(), dict)


def test_schema_version():
    assert build_computation_implementation_plan()["schema_version"] == SCHEMA_VERSION


def test_plan_id():
    assert build_computation_implementation_plan()["plan_id"] == PLAN_ID


def test_operator_id():
    assert build_computation_implementation_plan()["operator_id"] == OPERATOR_ID


def test_plan_status():
    assert build_computation_implementation_plan()["plan_status"] == PLAN_STATUS


def test_implementation_stage():
    assert build_computation_implementation_plan()["implementation_stage"] == IMPLEMENTATION_STAGE


def test_intended_lane():
    assert build_computation_implementation_plan()["intended_lane"] == "SHADOW"


def test_source_operator_decision_hash():
    assert (
        build_computation_implementation_plan()["source_operator_decision_hash"]
        == SOURCE_OPERATOR_DECISION_HASH
    )


def test_source_authorization_review_hash():
    assert (
        build_computation_implementation_plan()["source_computation_authorization_review_hash"]
        == SOURCE_AUTHORIZATION_REVIEW_HASH
    )


def test_source_complete_review_hash():
    assert (
        build_computation_implementation_plan()["source_expected_values_complete_review_hash"]
        == SOURCE_COMPLETE_REVIEW_HASH
    )


def test_canonical_hash_64_chars():
    h = build_computation_implementation_plan()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    plan = build_computation_implementation_plan()
    pre = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == plan["canonical_hash"]


def test_validate_passes():
    validate_computation_implementation_plan(build_computation_implementation_plan())


def test_replay_stable():
    assert build_computation_implementation_plan() == build_computation_implementation_plan()


def test_recommended_next_step():
    assert (
        build_computation_implementation_plan()["recommended_next_step"]
        == "GEODESIC_COMPUTATION_IMPLEMENTATION_GATE"
    )


# ── algorithm plan ─────────────────────────────────────────────────────────────


def test_algorithm_cpu_only():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["algorithm_family"] == "CPU_REFERENCE_SHORTEST_PATH"
    assert alg["implementation_constraint"] == "CPU_ONLY_NO_GPU"


def test_algorithm_no_gpu():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["gpu_kernel_authorized"] is False


def test_algorithm_no_external_library():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["external_library_authorized"] is False


def test_algorithm_no_metric_emission():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["runtime_metric_emission"] is False


def test_algorithm_shadow_stub_only():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["shadow_stub_only"] is True


def test_algorithm_negative_weight_policy():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["negative_weight_policy"] == "REJECT_AS_INVALID_INPUT"


def test_algorithm_self_loop():
    alg = build_computation_implementation_plan()["algorithm_plan"]
    assert alg["self_loop_handling"] == "ZERO_DISTANCE_IF_SOURCE_EQUALS_TARGET"


# ── supported fixture scope ────────────────────────────────────────────────────


def test_scope_total_count():
    assert build_computation_implementation_plan()["supported_fixture_scope"]["total_fixture_count"] == 13


def test_scope_valid_count():
    assert build_computation_implementation_plan()["supported_fixture_scope"]["valid_fixture_count"] == 5


def test_scope_invalid_count():
    assert build_computation_implementation_plan()["supported_fixture_scope"]["invalid_fixture_count"] == 4


def test_scope_nc_count():
    assert build_computation_implementation_plan()["supported_fixture_scope"]["not_computable_fixture_count"] == 4


def test_scope_computation_applies_to_valid_only():
    assert (
        build_computation_implementation_plan()["supported_fixture_scope"]["computation_applies_to"]
        == "VALID_FIXTURES_ONLY"
    )


def test_scope_invalid_rejected_before_computation():
    assert (
        build_computation_implementation_plan()["supported_fixture_scope"][
            "invalid_fixtures_rejected_before_computation"
        ]
        is True
    )


def test_scope_nc_rejected_before_computation():
    assert (
        build_computation_implementation_plan()["supported_fixture_scope"][
            "not_computable_fixtures_rejected_before_computation"
        ]
        is True
    )


# ── valid fixture computation plan ────────────────────────────────────────────


def test_valid_fixture_ids_count():
    vcp = build_computation_implementation_plan()["valid_fixture_computation_plan"]
    assert len(vcp["fixture_ids"]) == 5


def test_valid_fixture_no_metric_emission():
    vcp = build_computation_implementation_plan()["valid_fixture_computation_plan"]
    assert vcp["metric_emission_applies"] is False


def test_valid_fixture_no_forecast_influence():
    vcp = build_computation_implementation_plan()["valid_fixture_computation_plan"]
    assert vcp["forecast_influence_applies"] is False


def test_valid_fixture_comparison_applies():
    vcp = build_computation_implementation_plan()["valid_fixture_computation_plan"]
    assert vcp["comparison_applies"] is True


def test_valid_fixture_output_field():
    vcp = build_computation_implementation_plan()["valid_fixture_computation_plan"]
    assert vcp["output_field"] == "computed_geodesic_distance"


def test_valid_fixture_expected_field():
    vcp = build_computation_implementation_plan()["valid_fixture_computation_plan"]
    assert vcp["expected_field"] == "expected_geodesic_distance"


# ── invalid fixture rejection plan ────────────────────────────────────────────


def test_invalid_fixture_ids_count():
    irp = build_computation_implementation_plan()["invalid_fixture_rejection_plan"]
    assert len(irp["fixture_ids"]) == 4


def test_invalid_fixture_not_computed():
    irp = build_computation_implementation_plan()["invalid_fixture_rejection_plan"]
    assert irp["computation_attempted"] is False


def test_invalid_fixture_outcome():
    irp = build_computation_implementation_plan()["invalid_fixture_rejection_plan"]
    assert irp["rejection_outcome"] == "INVALID_INPUT"


# ── not_computable fixture rejection plan ─────────────────────────────────────


def test_nc_fixture_ids_count():
    ncrp = build_computation_implementation_plan()["not_computable_fixture_rejection_plan"]
    assert len(ncrp["fixture_ids"]) == 4


def test_nc_fixture_not_computed():
    ncrp = build_computation_implementation_plan()["not_computable_fixture_rejection_plan"]
    assert ncrp["computation_attempted"] is False


def test_nc_fixture_outcome():
    ncrp = build_computation_implementation_plan()["not_computable_fixture_rejection_plan"]
    assert ncrp["not_computable_outcome"] == "NOT_COMPUTABLE"


# ── deterministic ordering policy ─────────────────────────────────────────────


def test_determinism_guarantee():
    assert (
        build_computation_implementation_plan()["deterministic_ordering_policy"][
            "determinism_guarantee"
        ]
        is True
    )


# ── numerical policy ───────────────────────────────────────────────────────────


def test_numerical_float64():
    np_ = build_computation_implementation_plan()["numerical_policy"]
    assert np_["distance_type"] == "FLOAT64"


def test_numerical_no_emission():
    np_ = build_computation_implementation_plan()["numerical_policy"]
    assert np_["emission_policy"] == "NO_METRIC_EMISSION"


def test_numerical_zero_distance():
    np_ = build_computation_implementation_plan()["numerical_policy"]
    assert np_["zero_distance_representation"] == 0.0


# ── comparison policy ──────────────────────────────────────────────────────────


def test_comparison_target_field():
    cp = build_computation_implementation_plan()["comparison_policy"]
    assert cp["comparison_target_field"] == "expected_geodesic_distance"


def test_comparison_no_metric_emission():
    cp = build_computation_implementation_plan()["comparison_policy"]
    assert cp["metric_emission_on_comparison"] is False


def test_comparison_valid_only():
    cp = build_computation_implementation_plan()["comparison_policy"]
    assert cp["comparison_applies_to"] == "VALID_FIXTURES_ONLY"


def test_comparison_exact_equality():
    cp = build_computation_implementation_plan()["comparison_policy"]
    assert cp["comparison_method"] == "EXACT_FLOAT64_EQUALITY"


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_implementation_plan()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_computation_implementation_plan()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_computation_implementation_plan()["authority_locks"]["shadow_lane_only"] is True


def test_lock_implementation_plan_only():
    assert (
        build_computation_implementation_plan()["authority_locks"]["implementation_plan_only"] is True
    )


def test_lock_emits_metric_values_false():
    assert (
        build_computation_implementation_plan()["authority_locks"]["emits_metric_values"] is False
    )


def test_lock_execution_authority_false():
    assert (
        build_computation_implementation_plan()["authority_locks"]["execution_authority"] is False
    )


def test_lock_geodesic_computation_impl_authorized_false():
    assert (
        build_computation_implementation_plan()["authority_locks"][
            "geodesic_computation_implementation_authorized"
        ]
        is False
    )


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    plan = build_computation_implementation_plan()
    plan["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicComputationImplementationPlanValidationError):
        validate_computation_implementation_plan(plan)


def test_validate_rejects_wrong_status():
    plan = build_computation_implementation_plan()
    plan["plan_status"] = "WRONG"
    with pytest.raises(GeodesicComputationImplementationPlanValidationError):
        validate_computation_implementation_plan(plan)


def test_validate_rejects_hash_mismatch():
    plan = build_computation_implementation_plan()
    plan["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicComputationImplementationPlanValidationError):
        validate_computation_implementation_plan(plan)


def test_validate_rejects_impl_authorized_true():
    plan = build_computation_implementation_plan()
    plan["authority_locks"]["geodesic_computation_implementation_authorized"] = True
    plan["canonical_hash"] = canonical_hash(
        {k: v for k, v in plan.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationImplementationPlanValidationError):
        validate_computation_implementation_plan(plan)


def test_validate_rejects_wrong_decision_hash():
    plan = build_computation_implementation_plan()
    plan["source_operator_decision_hash"] = "b" * 64
    plan["canonical_hash"] = canonical_hash(
        {k: v for k, v in plan.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationImplementationPlanValidationError):
        validate_computation_implementation_plan(plan)
