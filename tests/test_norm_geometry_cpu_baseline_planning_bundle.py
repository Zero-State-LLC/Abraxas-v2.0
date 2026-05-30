from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.norm_geometry_cpu_baseline_implementation_plan import (
    ALLOWED_STEP_TYPE,
    ALLOWED_STABILITY_TYPE,
    build_norm_geometry_cpu_baseline_implementation_plan,
    default_algorithm_plan,
    default_benchmark_plan,
    default_future_acceleration_seams,
    default_implementation_constraints,
    default_input_data_contract,
    default_memory_layout_plan,
    default_numerical_stability_plan,
    default_output_contract as impl_plan_output_contract,
    default_output_data_contract,
    default_validation_plan as impl_validation_plan,
)
from core.norm_geometry_cpu_baseline_validation_plan import (
    build_norm_geometry_cpu_baseline_validation_plan,
    default_fixture_validation_scope,
    default_invalid_fixture_rejection_scope,
    default_no_forecast_scan,
    default_no_p43_scan,
    default_no_runtime_scan,
    default_output_contract as val_plan_output_contract,
    default_tolerance_policy,
)
from core.norm_geometry_cpu_baseline_actual_pr_gate_review import (
    build_norm_geometry_cpu_baseline_actual_pr_gate_review,
    default_gate_conditions,
    default_output_contract as gate_review_output_contract,
)
from core.canonical.json import canonical_hash

_LOCKED_FALSE = {
    "production_activation": False, "canon_promotion": False,
    "scheduler_mutation": False, "runtime_authority": False,
    "runtime_mutation": False, "forecast_influence": False,
    "execution_authority": False, "token_minting_allowed": False,
    "valid_for_execution": False, "activation_approved": False,
    "authorization_granted": False,
}
PATCH_ID = "NORM_GEOMETRY_CPU_BASELINE_PLANNING_BUNDLE_001"


def _impl_plan_payload() -> dict:
    return {
        "plan_id": "norm_geometry_cpu_baseline_implementation_plan_001",
        "implementation_topology": {
            "implementation_mode": "CPU_REFERENCE_PLAN",
            "intended_lane": "SHADOW",
            "topology_stage": "ALGORITHM_TOPOLOGY_ONLY",
        },
        "algorithm_plan": default_algorithm_plan(),
        "numerical_stability_plan": default_numerical_stability_plan(),
        "input_data_contract": default_input_data_contract(),
        "output_data_contract": default_output_data_contract(),
        "memory_layout_plan": default_memory_layout_plan(),
        "benchmark_plan": default_benchmark_plan(),
        "future_acceleration_seams": default_future_acceleration_seams(),
        "implementation_constraints": default_implementation_constraints(),
        "validation_plan": impl_validation_plan(),
        "output_contract": impl_plan_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "NORM_GEOMETRY_CPU_BASELINE_PLANNING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryDistanceImplementationReadinessDossier.v1:"
                "norm_geometry_distance_implementation_readiness_dossier_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/norm_geometry_cpu_baseline_implementation_plan.v1.schema.json",
            ],
        },
        "source_readiness_dossier_refs": [
            "NormGeometryDistanceImplementationReadinessDossier.v1:"
            "norm_geometry_distance_implementation_readiness_dossier_001",
        ],
        "source_metric_registry_refs": [
            "MetricOperatorRegistryStabilization.v1:"
            "metric_operator_registry_stabilization_002",
        ],
        "source_test_vector_pack_refs": [
            "MetricOperatorBaselineTestVectorPack.v1:"
            "metric_operator_baseline_test_vector_pack_001",
        ],
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _val_plan_payload() -> dict:
    return {
        "plan_id": "norm_geometry_cpu_baseline_validation_plan_001",
        "fixture_validation_scope": default_fixture_validation_scope(),
        "tolerance_policy": default_tolerance_policy(),
        "invalid_fixture_rejection_scope": default_invalid_fixture_rejection_scope(),
        "no_runtime_scan": default_no_runtime_scan(),
        "no_forecast_scan": default_no_forecast_scan(),
        "no_p43_scan": default_no_p43_scan(),
        "output_contract": val_plan_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "NORM_GEOMETRY_CPU_BASELINE_PLANNING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryCpuBaselineImplementationPlan.v1:"
                "norm_geometry_cpu_baseline_implementation_plan_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/norm_geometry_cpu_baseline_validation_plan.v1.schema.json",
            ],
        },
        "source_implementation_plan_refs": [
            "NormGeometryCpuBaselineImplementationPlan.v1:"
            "norm_geometry_cpu_baseline_implementation_plan_001",
        ],
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _gate_review_payload() -> dict:
    return {
        "review_id": "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
        "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
        "plans_reviewed": [
            "NormGeometryCpuBaselineImplementationPlan.v1:"
            "norm_geometry_cpu_baseline_implementation_plan_001",
            "NormGeometryCpuBaselineValidationPlan.v1:"
            "norm_geometry_cpu_baseline_validation_plan_001",
        ],
        "gate_conditions": default_gate_conditions(),
        "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
        "stop_boundary_reason": (
            "Operator authorization required before any implementation PR may be "
            "opened. This gate review is advisory-only. gate-cond-005 is not met."
        ),
        "output_contract": gate_review_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "NORM_GEOMETRY_CPU_BASELINE_PLANNING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "NormGeometryCpuBaselineImplementationPlan.v1:"
                "norm_geometry_cpu_baseline_implementation_plan_001",
                "NormGeometryDistanceImplementationReadinessDossier.v1:"
                "norm_geometry_distance_implementation_readiness_dossier_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/norm_geometry_cpu_baseline_actual_pr_gate_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── Algorithm Plan ────────────────────────────────────────────────────────────

def test_algorithm_plan_step_count() -> None:
    steps = default_algorithm_plan()
    assert len(steps) == 8


def test_algorithm_plan_step_ids_unique() -> None:
    steps = default_algorithm_plan()
    ids = [s["step_id"] for s in steps]
    assert len(ids) == len(set(ids))


def test_algorithm_plan_all_step_types_valid() -> None:
    steps = default_algorithm_plan()
    for s in steps:
        assert s["step_type"] in ALLOWED_STEP_TYPE, s["step_id"]


def test_algorithm_plan_has_input_validation_step() -> None:
    steps = default_algorithm_plan()
    types = {s["step_type"] for s in steps}
    assert "INPUT_VALIDATION_STEP" in types


def test_algorithm_plan_has_not_computable_branch() -> None:
    steps = default_algorithm_plan()
    types = {s["step_type"] for s in steps}
    assert "NOT_COMPUTABLE_BRANCH_STEP" in types


def test_algorithm_plan_has_baseline_comparator() -> None:
    steps = default_algorithm_plan()
    types = {s["step_type"] for s in steps}
    assert "BASELINE_COMPARATOR_STEP" in types


def test_algorithm_plan_all_blocked_lp_norm_computation() -> None:
    steps = default_algorithm_plan()
    for s in steps:
        if s["step_type"] != "BASELINE_COMPARATOR_STEP":
            assert "lp_norm_computation" in s.get("blocked_operations", []), s["step_id"]


def test_algorithm_plan_all_planned_only() -> None:
    steps = default_algorithm_plan()
    for s in steps:
        assert s["implementation_status"] == "PLANNED_ONLY", s["step_id"]


# ── Numerical Stability Plan ──────────────────────────────────────────────────

def test_numerical_stability_plan_count() -> None:
    plan = default_numerical_stability_plan()
    assert len(plan) == 6


def test_numerical_stability_plan_all_types_valid() -> None:
    plan = default_numerical_stability_plan()
    for entry in plan:
        assert entry["stability_type"] in ALLOWED_STABILITY_TYPE, entry["stability_id"]


def test_numerical_stability_plan_has_float_precision_policy() -> None:
    plan = default_numerical_stability_plan()
    types = {e["stability_type"] for e in plan}
    assert "FLOAT_PRECISION_POLICY" in types


def test_numerical_stability_plan_has_not_computable_policy() -> None:
    plan = default_numerical_stability_plan()
    types = {e["stability_type"] for e in plan}
    assert "NOT_COMPUTABLE_POLICY" in types


def test_numerical_stability_plan_p_parameter_policy() -> None:
    plan = default_numerical_stability_plan()
    types = {e["stability_type"] for e in plan}
    assert "P_PARAMETER_POLICY" in types


# ── Input / Output Data Contracts ─────────────────────────────────────────────

def test_input_data_contract_runtime_binding_disabled() -> None:
    contract = default_input_data_contract()
    assert contract["runtime_binding_enabled"] is False


def test_input_data_contract_required_fields_declared() -> None:
    contract = default_input_data_contract()
    assert contract["vector_x_required"] is True
    assert contract["vector_y_required"] is True
    assert contract["p_parameter_required"] is True


def test_output_data_contract_no_lp_distance_emission() -> None:
    contract = default_output_data_contract()
    assert contract["emits_lp_distance_value"] is False
    assert contract["runtime_output_binding_enabled"] is False


def test_implementation_constraints_all_false() -> None:
    constraints = default_implementation_constraints()
    for key, val in constraints.items():
        assert val is False, f"implementation_constraints.{key} must be False"


def test_future_acceleration_seams_no_gpu_no_approximation() -> None:
    seams = default_future_acceleration_seams()
    assert seams["gpu_candidate_declared"] is False
    assert seams["approximation_candidate_declared"] is False
    assert seams["acceleration_implemented"] is False
    assert seams["simd_candidate_declared"] is True


# ── Implementation Plan Build ─────────────────────────────────────────────────

def test_impl_plan_builds() -> None:
    plan = build_norm_geometry_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert plan["operator_id"] == "NORM_GEOMETRY"
    assert plan["plan_type"] == "NORM_GEOMETRY_CPU_BASELINE_IMPLEMENTATION_PLAN"
    assert plan["implementation_topology"]["implementation_mode"] == "CPU_REFERENCE_PLAN"


def test_impl_plan_deterministic() -> None:
    a = build_norm_geometry_cpu_baseline_implementation_plan(_impl_plan_payload())
    b = build_norm_geometry_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_impl_plan_hash_valid() -> None:
    plan = build_norm_geometry_cpu_baseline_implementation_plan(_impl_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_impl_plan_governance_all_false() -> None:
    plan = build_norm_geometry_cpu_baseline_implementation_plan(_impl_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_impl_plan_output_contract_advisory_only() -> None:
    plan = build_norm_geometry_cpu_baseline_implementation_plan(_impl_plan_payload())
    oc = plan["output_contract"]
    assert oc["emits_metric_values"] is False
    assert oc["emits_metric_code"] is False
    assert oc["emits_authority_tokens"] is False
    assert oc["emits_baseline_plan"] is True
    assert oc["emits_algorithm_topology"] is True


# ── Validation Plan ───────────────────────────────────────────────────────────

def test_fixture_validation_scope_count() -> None:
    scope = default_fixture_validation_scope()
    assert scope["valid_fixture_count"] == 6
    assert scope["execution_enabled"] is False


def test_invalid_fixture_rejection_scope() -> None:
    scope = default_invalid_fixture_rejection_scope()
    assert scope["invalid_fixture_count"] == 4
    assert scope["not_computable_fixture_count"] == 4
    assert scope["execution_enabled"] is False


def test_tolerance_policy_float64_required() -> None:
    policy = default_tolerance_policy()
    assert policy["float64_required"] is True
    assert policy["tolerance_execution_enabled"] is False


def test_val_plan_scans_declared() -> None:
    assert default_no_runtime_scan()["runtime_mutation_blocked"] is True
    assert default_no_forecast_scan()["forecast_influence_blocked"] is True
    assert default_no_p43_scan()["p43_surface_lanes_blocked"] is True


def test_val_plan_builds() -> None:
    plan = build_norm_geometry_cpu_baseline_validation_plan(_val_plan_payload())
    assert plan["operator_id"] == "NORM_GEOMETRY"
    assert plan["execution_authorized"] is False


def test_val_plan_deterministic() -> None:
    a = build_norm_geometry_cpu_baseline_validation_plan(_val_plan_payload())
    b = build_norm_geometry_cpu_baseline_validation_plan(_val_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_val_plan_hash_valid() -> None:
    plan = build_norm_geometry_cpu_baseline_validation_plan(_val_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_val_plan_governance_all_false() -> None:
    plan = build_norm_geometry_cpu_baseline_validation_plan(_val_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Gate Review ───────────────────────────────────────────────────────────────

def test_gate_conditions_count() -> None:
    conds = default_gate_conditions()
    assert len(conds) == 5


def test_gate_conditions_ids_unique() -> None:
    conds = default_gate_conditions()
    ids = [c["condition_id"] for c in conds]
    assert len(ids) == len(set(ids))


def test_gate_cond_005_not_met() -> None:
    conds = default_gate_conditions()
    cond_005 = next(c for c in conds if c["condition_id"] == "gate-cond-005")
    assert cond_005["condition_met"] is False


def test_gate_conds_001_to_004_met() -> None:
    conds = default_gate_conditions()
    for cond in conds:
        if cond["condition_id"] != "gate-cond-005":
            assert cond["condition_met"] is True, cond["condition_id"]


def test_gate_review_builds() -> None:
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert review["operator_id"] == "NORM_GEOMETRY"
    assert review["review_status"] == "PLANS_COMPLETE_PENDING_OPERATOR_DECISION"
    assert review["implementation_recommendation"] == "ADVISORY_REVIEW_ONLY"
    assert review["required_operator_decision"] is True


def test_gate_review_deterministic() -> None:
    a = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    b = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_gate_review_hash_valid() -> None:
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    h = review["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in review.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_gate_review_governance_all_false() -> None:
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    for flag, val in review["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


def test_gate_review_emits_gate_review_only() -> None:
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    oc = review["output_contract"]
    assert oc["emits_gate_review"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


def test_gate_review_plans_reviewed_non_empty() -> None:
    review = build_norm_geometry_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert len(review["plans_reviewed"]) >= 2


# ── Artifact file presence (post-runner) ─────────────────────────────────────

def test_impl_plan_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "norm_geometry_cpu_baseline_implementation_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "NORM_GEOMETRY"
    assert data["implementation_constraints"]["norm_geometry_computation_added"] is False


def test_val_plan_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "norm_geometry_cpu_baseline_validation_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["execution_authorized"] is False
    assert data["fixture_validation_scope"]["valid_fixture_count"] == 6


def test_gate_review_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "norm_geometry_cpu_baseline_actual_pr_gate_review_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["implementation_recommendation"] == "ADVISORY_REVIEW_ONLY"
    assert data["required_operator_decision"] is True
    cond_005 = next(
        c for c in data["gate_conditions"] if c["condition_id"] == "gate-cond-005"
    )
    assert cond_005["condition_met"] is False
