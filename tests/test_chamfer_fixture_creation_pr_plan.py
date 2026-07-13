"""Tests for core/chamfer_fixture_creation_pr_plan.py (candidate fbe707eebd7070a4)"""

import pytest
from core.chamfer_fixture_creation_pr_plan import (
    SCHEMA_VERSION,
    PLAN_TYPE,
    OPERATOR_ID,
    ALLOWED_FAMILY,
    ALLOWED_LANE,
    ALLOWED_STAGE,
    ChamferFixtureCreationPRPlanValidationError,
)

def test_schema_and_plan_type():
    assert SCHEMA_VERSION == "ChamferFixtureCreationPRPlan.v1"
    assert PLAN_TYPE == "CHAMFER_FIXTURE_CREATION_PR_PLAN"
    assert OPERATOR_ID == "CHAMFER_DISTANCE"

def test_allowed_families_lanes_stages():
    assert "FIXTURE_CREATION_PR_PLANNING_ONLY" in ALLOWED_FAMILY
    assert "SHADOW" in ALLOWED_LANE
    assert "PR_PLAN_ONLY" in ALLOWED_STAGE

def test_validation_error_is_value_error():
    assert issubclass(ChamferFixtureCreationPRPlanValidationError, ValueError)
