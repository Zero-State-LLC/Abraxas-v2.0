from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.transport_cpu_baseline_implementation_plan import (
    ALLOWED_STEP_TYPE,
    ALLOWED_STABILITY_TYPE,
    build_transport_cpu_baseline_implementation_plan,
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
from core.transport_cpu_baseline_validation_plan import (
    build_transport_cpu_baseline_validation_plan,
    default_fixture_validation_scope,
    default_invalid_fixture_rejection_scope,
    default_no_forecast_scan,
    default_no_lp_solver_scan,
    default_no_p43_scan,
    default_no_runtime_scan,
    default_output_contract as val_plan_output_contract,
    default_tolerance_policy,
)
from core.transport_cpu_baseline_actual_pr_gate_review import (
    build_transport_cpu_baseline_actual_pr_gate_review,
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
PATCH_ID = "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_001"


def _impl_plan_payload() -> dict:
    return {
        "plan_id": "transport_cpu_baseline_implementation_plan_001",
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
            "source": "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "TransportDistanceImplementationReadinessDossier.v1:"
                "transport_distance_implementation_readiness_dossier_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/transport_cpu_baseline_implementation_plan.v1.schema.json",
            ],
        },
        "source_readiness_dossier_refs": [
            "TransportDistanceImplementationReadinessDossier.v1:"
            "transport_distance_implementation_readiness_dossier_001",
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
        "plan_id": "transport_cpu_baseline_validation_plan_001",
        "fixture_validation_scope": default_fixture_validation_scope(),
        "tolerance_policy": default_tolerance_policy(),
        "invalid_fixture_rejection_scope": default_invalid_fixture_rejection_scope(),
        "no_runtime_scan": default_no_runtime_scan(),
        "no_forecast_scan": default_no_forecast_scan(),
        "no_p43_scan": default_no_p43_scan(),
        "no_lp_solver_scan": default_no_lp_solver_scan(),
        "output_contract": val_plan_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "TransportCpuBaselineImplementationPlan.v1:"
                "transport_cpu_baseline_implementation_plan_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/transport_cpu_baseline_validation_plan.v1.schema.json",
            ],
        },
        "source_implementation_plan_refs": [
            "TransportCpuBaselineImplementationPlan.v1:"
            "transport_cpu_baseline_implementation_plan_001",
        ],
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def _gate_review_payload() -> dict:
    return {
        "review_id": "transport_cpu_baseline_actual_pr_gate_review_001",
        "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
        "plans_reviewed": [
            "TransportCpuBaselineImplementationPlan.v1:"
            "transport_cpu_baseline_implementation_plan_001",
            "TransportCpuBaselineValidationPlan.v1:"
            "transport_cpu_baseline_validation_plan_001",
        ],
        "gate_conditions": default_gate_conditions(),
        "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
        "stop_boundary_reason": (
            "Operator authorization required before any implementation PR may be "
            "opened. gate-cond-005 is not met."
        ),
        "output_contract": gate_review_output_contract(),
        "governance_flags": dict(_LOCKED_FALSE),
        "provenance": {
            "source": "TRANSPORT_CPU_BASELINE_PLANNING_BUNDLE_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "evidence_refs": [
                "TransportCpuBaselineImplementationPlan.v1:"
                "transport_cpu_baseline_implementation_plan_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/transport_cpu_baseline_actual_pr_gate_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ── Implementation Plan ───────────────────────────────────────────────────────

def test_impl_plan_builds() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert plan["operator_id"] == "TRANSPORT"
    assert plan["implementation_topology"]["implementation_mode"] == "CPU_REFERENCE_PLAN"
    assert plan["implementation_topology"]["intended_lane"] == "SHADOW"
    assert plan["implementation_topology"]["topology_stage"] == "ALGORITHM_TOPOLOGY_ONLY"


def test_impl_plan_algorithm_steps_non_empty() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert len(plan["algorithm_plan"]) >= 5


def test_impl_plan_has_balance_check_step() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    types = {s["step_type"] for s in plan["algorithm_plan"]}
    assert "BALANCE_CHECK_TOPOLOGY_STEP" in types


def test_impl_plan_has_degenerate_path_step() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    types = {s["step_type"] for s in plan["algorithm_plan"]}
    assert "DEGENERATE_PATH_TOPOLOGY_STEP" in types


def test_impl_plan_has_lp_topology_declaration_step() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    types = {s["step_type"] for s in plan["algorithm_plan"]}
    assert "LP_TOPOLOGY_DECLARATION_STEP" in types


def test_impl_plan_has_not_computable_branch() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    types = {s["step_type"] for s in plan["algorithm_plan"]}
    assert "NOT_COMPUTABLE_BRANCH_STEP" in types


def test_impl_plan_all_steps_planned_only() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    for step in plan["algorithm_plan"]:
        assert step["implementation_status"] == "PLANNED_ONLY", step["step_id"]


def test_impl_plan_all_steps_block_lp_solver() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    for step in plan["algorithm_plan"]:
        assert "lp_solver_invocation" in step["blocked_operations"], step["step_id"]


def test_impl_plan_step_ids_unique() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    ids = [s["step_id"] for s in plan["algorithm_plan"]]
    assert len(ids) == len(set(ids))


def test_impl_plan_step_types_all_valid() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    for step in plan["algorithm_plan"]:
        assert step["step_type"] in ALLOWED_STEP_TYPE, step["step_id"]


def test_impl_plan_numerical_stability_non_empty() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert len(plan["numerical_stability_plan"]) >= 4


def test_impl_plan_has_balance_tolerance_stability() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    types = {s["stability_type"] for s in plan["numerical_stability_plan"]}
    assert "BALANCE_TOLERANCE_POLICY" in types


def test_impl_plan_has_lp_solver_stability() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    types = {s["stability_type"] for s in plan["numerical_stability_plan"]}
    assert "LP_SOLVER_POLICY" in types


def test_impl_plan_stability_types_all_valid() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    for entry in plan["numerical_stability_plan"]:
        assert entry["stability_type"] in ALLOWED_STABILITY_TYPE, entry["stability_id"]


def test_impl_plan_stability_ids_unique() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    ids = [s["stability_id"] for s in plan["numerical_stability_plan"]]
    assert len(ids) == len(set(ids))


def test_impl_plan_input_data_contract_runtime_disabled() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert plan["input_data_contract"]["runtime_binding_enabled"] is False
    assert plan["input_data_contract"]["balance_tolerance_policy_declared"] is True
    assert plan["input_data_contract"]["cost_matrix_shape_policy_declared"] is True


def test_impl_plan_output_data_contract_no_transport_distance() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert plan["output_data_contract"]["emits_transport_distance_value"] is False
    assert plan["output_data_contract"]["runtime_output_binding_enabled"] is False


def test_impl_plan_constraints_all_blocked() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    c = plan["implementation_constraints"]
    assert c["transport_computation_added"] is False
    assert c["lp_solver_invoked"] is False
    assert c["transport_distance_values_emitted"] is False
    assert c["forecast_influence_added"] is False


def test_impl_plan_approximation_seam_declared() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    seams = plan["future_acceleration_seams"]
    assert seams["approximation_candidate_declared"] is True
    assert seams["acceleration_implemented"] is False
    assert seams["simd_candidate_declared"] is False


def test_impl_plan_validation_plan_requires_lp_scan() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert plan["validation_plan"]["requires_no_lp_solver_invocation_scan"] is True


def test_impl_plan_output_contract_emits_topology() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    oc = plan["output_contract"]
    assert oc["emits_baseline_plan"] is True
    assert oc["emits_algorithm_topology"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


def test_impl_plan_deterministic() -> None:
    a = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    b = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_impl_plan_hash_valid() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_impl_plan_governance_all_false() -> None:
    plan = build_transport_cpu_baseline_implementation_plan(_impl_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Validation Plan ───────────────────────────────────────────────────────────

def test_val_plan_builds() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    assert plan["operator_id"] == "TRANSPORT"
    assert plan["execution_authorized"] is False


def test_val_plan_fixture_scope_valid() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    fvs = plan["fixture_validation_scope"]
    assert fvs["valid_fixture_count"] == 6
    assert fvs["execution_enabled"] is False
    assert fvs["determinism_required"] is True


def test_val_plan_tolerance_policy_no_execution() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    tp = plan["tolerance_policy"]
    assert tp["float64_required"] is True
    assert tp["balance_tolerance_declared"] is True
    assert tp["lp_solver_execution_enabled"] is False
    assert tp["tolerance_execution_enabled"] is False


def test_val_plan_rejection_scope_counts() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    ifrs = plan["invalid_fixture_rejection_scope"]
    assert ifrs["invalid_fixture_count"] == 4
    assert ifrs["not_computable_fixture_count"] == 5
    assert ifrs["execution_enabled"] is False


def test_val_plan_no_lp_solver_scan_declared() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    lp = plan["no_lp_solver_scan"]
    assert lp["scan_declared"] is True
    assert lp["lp_solver_invocation_blocked"] is True
    assert lp["transport_computation_blocked"] is True


def test_val_plan_no_runtime_scan_declared() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    assert plan["no_runtime_scan"]["runtime_mutation_blocked"] is True


def test_val_plan_no_forecast_scan_declared() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    assert plan["no_forecast_scan"]["forecast_influence_blocked"] is True


def test_val_plan_no_p43_scan_declared() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    assert plan["no_p43_scan"]["p43_surface_lanes_blocked"] is True


def test_val_plan_output_contract_emits_plan_only() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    oc = plan["output_contract"]
    assert oc["emits_validation_plan"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


def test_val_plan_deterministic() -> None:
    a = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    b = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_val_plan_hash_valid() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_val_plan_governance_all_false() -> None:
    plan = build_transport_cpu_baseline_validation_plan(_val_plan_payload())
    for flag, val in plan["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Gate Review ───────────────────────────────────────────────────────────────

def test_gate_review_builds() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert review["operator_id"] == "TRANSPORT"
    assert review["review_status"] == "PLANS_COMPLETE_PENDING_OPERATOR_DECISION"
    assert review["implementation_recommendation"] == "ADVISORY_REVIEW_ONLY"
    assert review["required_operator_decision"] is True


def test_gate_review_conditions_count() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert len(review["gate_conditions"]) == 5


def test_gate_review_gate_cond_001_to_004_met() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    conds = {c["condition_id"]: c for c in review["gate_conditions"]}
    for cid in ("gate-cond-001", "gate-cond-002", "gate-cond-003", "gate-cond-004"):
        assert conds[cid]["condition_met"] is True, f"{cid} must be met"


def test_gate_review_gate_cond_005_unmet() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    conds = {c["condition_id"]: c for c in review["gate_conditions"]}
    assert conds["gate-cond-005"]["condition_met"] is False


def test_gate_review_gate_cond_005_mentions_lp_solver() -> None:
    conds = {c["condition_id"]: c for c in default_gate_conditions()}
    desc = conds["gate-cond-005"]["condition_description"].lower()
    assert "lp solver" in desc or "lp" in desc


def test_gate_review_condition_ids_unique() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    ids = [c["condition_id"] for c in review["gate_conditions"]]
    assert len(ids) == len(set(ids))


def test_gate_review_plans_reviewed_non_empty() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert len(review["plans_reviewed"]) >= 2


def test_gate_review_plans_reviewed_contains_impl_plan() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    combined = " ".join(review["plans_reviewed"])
    assert "TransportCpuBaselineImplementationPlan" in combined


def test_gate_review_plans_reviewed_contains_val_plan() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    combined = " ".join(review["plans_reviewed"])
    assert "TransportCpuBaselineValidationPlan" in combined


def test_gate_review_output_contract_emits_gate_review() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    oc = review["output_contract"]
    assert oc["emits_gate_review"] is True
    assert oc["emits_metric_values"] is False
    assert oc["emits_authority_tokens"] is False


def test_gate_review_deterministic() -> None:
    a = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    b = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_gate_review_hash_valid() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    h = review["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64
    preimage = {k: v for k, v in review.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == h


def test_gate_review_governance_all_false() -> None:
    review = build_transport_cpu_baseline_actual_pr_gate_review(_gate_review_payload())
    for flag, val in review["governance_flags"].items():
        assert val is False, f"governance_flags.{flag} must be False"


# ── Artifact file presence (post-runner) ──────────────────────────────────────

def test_transport_impl_plan_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "transport_cpu_baseline_implementation_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "TRANSPORT"
    assert data["implementation_topology"]["implementation_mode"] == "CPU_REFERENCE_PLAN"
    assert data["implementation_constraints"]["lp_solver_invoked"] is False


def test_transport_val_plan_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "transport_cpu_baseline_validation_plan_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "TRANSPORT"
    assert data["execution_authorized"] is False
    assert data["no_lp_solver_scan"]["lp_solver_invocation_blocked"] is True


def test_transport_gate_review_file_written() -> None:
    p = Path(
        "out/metric_operator/"
        "transport_cpu_baseline_actual_pr_gate_review_001.latest.json"
    )
    if not p.exists():
        pytest.skip("runner not yet executed")
    data = json.loads(p.read_text())
    assert data["operator_id"] == "TRANSPORT"
    assert data["review_status"] == "PLANS_COMPLETE_PENDING_OPERATOR_DECISION"
    conds = {c["condition_id"]: c for c in data["gate_conditions"]}
    assert conds["gate-cond-005"]["condition_met"] is False
