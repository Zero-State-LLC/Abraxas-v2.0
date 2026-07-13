"""Tests for core/metric_operator_rank5_selection_plan.py (HARDENING candidate bc912a043f64d835)"""

from core.metric_operator_rank5_selection_plan import (
    build_metric_operator_rank5_selection_plan,
    validate_metric_operator_rank5_selection_plan,
    compute_metric_operator_rank5_selection_plan_hash,
    default_implementation_gates,
    default_output_contract,
    LOCKED_FALSE_FLAGS,
    MetricOperatorRank5SelectionPlanValidationError,
)

def test_build_and_validate():
    payload = {
        "plan_id": "plan-test-001",
        "created_at_utc": "2026-07-12T00:00:00Z",
        "source_audit_refs": ["audit1", "audit2"],
        "source_registry_stabilization_refs": [],
        "source_frontier_recommendation_refs": [],
        "implementation_gates": default_implementation_gates(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {"source": "test", "timestamp": "2026-07-12"},
        "selection_scope": {
            "intended_lane": "SHADOW",
            "selection_family": "RANK5_OPERATOR_SELECTION",
            "selection_stage": "SELECTION_PLAN_ONLY",
        },
    }
    plan = build_metric_operator_rank5_selection_plan(payload)
    assert isinstance(plan, dict)
    assert plan["schema_version"] == "MetricOperatorRank5SelectionPlan.v1"
    assert "canonical_hash" in plan
    validate_metric_operator_rank5_selection_plan(plan)

def test_hash_deterministic():
    payload = {
        "plan_id": "plan-test-002",
        "created_at_utc": "2026-07-12T00:00:00Z",
        "source_audit_refs": ["a"],
        "source_registry_stabilization_refs": [],
        "source_frontier_recommendation_refs": [],
        "implementation_gates": default_implementation_gates(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {"source": "t"},
        "selection_scope": {"intended_lane": "SHADOW", "selection_family": "RANK5_OPERATOR_SELECTION", "selection_stage": "SELECTION_PLAN_ONLY"},
    }
    p1 = build_metric_operator_rank5_selection_plan(payload)
    p2 = build_metric_operator_rank5_selection_plan(payload)
    assert p1["canonical_hash"] == p2["canonical_hash"]

def test_validation_errors():
    bad = {"source_audit_refs": [], "selection_scope": {"intended_lane": "BAD"}, "governance_flags": {}, "provenance": {}, "implementation_gates": default_implementation_gates(), "output_contract": default_output_contract()}
    try:
        build_metric_operator_rank5_selection_plan(bad)
        assert False, "should raise"
    except MetricOperatorRank5SelectionPlanValidationError:
        pass
