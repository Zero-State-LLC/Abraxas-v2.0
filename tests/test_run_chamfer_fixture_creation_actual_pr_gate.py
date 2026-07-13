"""Tests for chamfer fixture creation PR plan (candidate fbe707eebd7070a4)"""

from core.chamfer_fixture_creation_pr_plan import (
    SCHEMA_VERSION,
    PLAN_TYPE,
    OPERATOR_ID,
    ALLOWED_FAMILY,
    ALLOWED_LANE,
    ALLOWED_STAGE,
    ChamferFixtureCreationPRPlanValidationError,
)

def test_constants():
    assert "ChamferFixtureCreationPRPlan" in SCHEMA_VERSION
    assert "CHAMFER" in PLAN_TYPE
    assert OPERATOR_ID == "CHAMFER_DISTANCE"

def test_allowed_sets():
    assert len(ALLOWED_FAMILY) > 0
    assert "FIXTURE_CREATION_PR_PLANNING_ONLY" in ALLOWED_FAMILY
    assert "SHADOW" in ALLOWED_LANE
    assert "PR_PLAN_ONLY" in ALLOWED_STAGE

def test_validation_error_exists():
    assert issubclass(ChamferFixtureCreationPRPlanValidationError, ValueError)
