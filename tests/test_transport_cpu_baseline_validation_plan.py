"""Tests for core/transport_cpu_baseline_validation_plan.py (HARDENING candidate d18d2ef0cc4620e0)"""

from core.transport_cpu_baseline_validation_plan import (
    build_transport_cpu_baseline_validation_plan,
    validate_transport_cpu_baseline_validation_plan,
    default_fixture_validation_scope,
    TransportCpuBaselineValidationPlanValidationError,
)

def test_build_and_validate():
    payload = {
        "plan_id": "plan-001",
        "created_at_utc": "2026-07-12T00:00:00Z",
        "fixture_validation_scope": default_fixture_validation_scope(),
        "governance_flags": {k: False for k in ["production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted"]},
        "provenance": {"source": "test"},
        "validation_level": "MEDIUM",
        "selection_status": "SELECTED",
    }
    plan = build_transport_cpu_baseline_validation_plan(payload)
    assert isinstance(plan, dict)
    assert "schema_version" in plan
    validate_transport_cpu_baseline_validation_plan(plan)

def test_validation_error():
    bad = {"plan_id": "bad", "fixture_validation_scope": {}, "governance_flags": {}, "provenance": {}, "validation_level": "LOW", "selection_status": "SELECTED"}
    try:
        build_transport_cpu_baseline_validation_plan(bad)
        assert False
    except TransportCpuBaselineValidationPlanValidationError:
        pass
