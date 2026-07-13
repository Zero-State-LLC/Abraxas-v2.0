"""Tests for core/norm_geometry_cpu_baseline_implementation_plan.py (candidate ffb64b201131eef5)"""

from core.norm_geometry_cpu_baseline_implementation_plan import (
    SCHEMA_VERSION,
    PLAN_TYPE,
    ALLOWED_IMPLEMENTATION_MODE,
    ALLOWED_INTENDED_LANE,
    ALLOWED_TOPOLOGY_STAGE,
)

def test_schema_and_type():
    assert SCHEMA_VERSION == "NormGeometryCpuBaselineImplementationPlan.v1"
    assert PLAN_TYPE == "NORM_GEOMETRY_CPU_BASELINE_IMPLEMENTATION_PLAN"

def test_allowed_modes_and_lanes():
    assert "CPU_REFERENCE_PLAN" in ALLOWED_IMPLEMENTATION_MODE
    assert "SHADOW" in ALLOWED_INTENDED_LANE
    assert "BASELINE_PLAN_ONLY" in ALLOWED_TOPOLOGY_STAGE
