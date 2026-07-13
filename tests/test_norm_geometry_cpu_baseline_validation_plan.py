"""Tests for core/norm_geometry_cpu_baseline_validation_plan.py (HARDENING candidate f21233ea2ec8da03)"""

from core.norm_geometry_cpu_baseline_validation_plan import (
    LOCKED_FALSE_FLAGS,
    FORBIDDEN,
    default_fixture_validation_scope,
    default_tolerance_policy,
    default_invalid_fixture_rejection_scope,
)

def test_locked_false_flags():
    assert "production_activation" in LOCKED_FALSE_FLAGS
    assert "runtime_mutation" in LOCKED_FALSE_FLAGS
    assert "execution_authority" in LOCKED_FALSE_FLAGS
    assert len(LOCKED_FALSE_FLAGS) >= 10

def test_forbidden_items():
    assert "executable" in FORBIDDEN
    assert "numpy" in FORBIDDEN
    assert "geodesic-distance" in FORBIDDEN
    assert "scoring" in FORBIDDEN

def test_default_scopes():
    fix = default_fixture_validation_scope()
    assert fix["valid_fixture_count"] == 6
    assert fix["determinism_required"] is True
    assert fix["execution_enabled"] is False

    tol = default_tolerance_policy()
    assert tol["float64_required"] is True
    assert tol["zero_tolerance_for_integer_inputs_declared"] is True

    inv = default_invalid_fixture_rejection_scope()
    assert inv["invalid_fixture_count"] == 4
    assert inv["rejection_policy_declared"] is True