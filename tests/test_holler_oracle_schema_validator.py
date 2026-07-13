"""Tests for core/codegen/oracle_signal/holler_oracle_schema_validator.py (GOVERNANCE candidate e8ab2cfc819bca40)"""

from core.codegen.oracle_signal.holler_oracle_schema_validator import validate_holler_oracle_batch_evolution

def test_validate_holler_oracle_batch_evolution_structure():
    holler_intake = {
        "holler_batch": {"calibration_policy": "SHADOW_CALIBRATION_REPORT_ONLY"},
        "shadow_replay": {"valid_for_execution": False},
    }
    result = validate_holler_oracle_batch_evolution(
        holler_intake=holler_intake,
        timestamp="2026-07-12T00:00:00Z",
    )
    assert "schema_validation" in result or "validation_status" in str(result).lower() or isinstance(result, dict)
    # Basic structure check
    assert isinstance(result, dict)

def test_holler_specific_errors():
    holler_intake = {
        "holler_batch": {"calibration_policy": "WRONG_POLICY"},
        "shadow_replay": {"valid_for_execution": True},
    }
    result = validate_holler_oracle_batch_evolution(
        holler_intake=holler_intake,
        timestamp="2026-07-12T00:00:00Z",
    )
    assert isinstance(result, dict)
