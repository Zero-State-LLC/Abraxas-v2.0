"""Tests for core/wasserstein_cpu_baseline_validation_plan.py (candidate fc69544426dcde4f)"""

import pytest
from core.wasserstein_cpu_baseline_validation_plan import (
    SCHEMA_VERSION,
    PLAN_TYPE,
    OPERATOR_ID,
    LOCKED_FALSE_FLAGS,
    FORBIDDEN,
)

def test_schema_and_plan_type():
    assert SCHEMA_VERSION == "WassersteinCpuBaselineValidationPlan.v1"
    assert PLAN_TYPE == "WASSERSTEIN_CPU_BASELINE_VALIDATION_PLAN"
    assert OPERATOR_ID == "WASSERSTEIN"

def test_locked_false_flags():
    assert "production_activation" in LOCKED_FALSE_FLAGS
    assert "canon_promotion" in LOCKED_FALSE_FLAGS
    assert len(LOCKED_FALSE_FLAGS) > 5

def test_forbidden_items():
    assert "executable" in FORBIDDEN
    assert "wasserstein-distance" in FORBIDDEN
    assert "numpy" in FORBIDDEN
    assert len(FORBIDDEN) > 5
