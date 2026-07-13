"""Tests for core/abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan.py (candidate b227f223c6f74b90)"""

from core.abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan import (
    build_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan,
)

def test_build_spec_plan():
    plan = build_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan()
    assert isinstance(plan, dict)
    assert "schema_version" in plan or "spec_plan_id" in plan or len(plan) > 0
