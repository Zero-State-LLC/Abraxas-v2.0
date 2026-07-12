"""Tests for core/abraxas_oracle_validation_harness.py (HARDENING candidate 1ab097747ae2fab9)

Covers structural, candidate, regression, replay, governance, and full run.
"""

from unittest.mock import patch, MagicMock
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

from core.abraxas_oracle_validation_harness import (
    structural_validation,
    candidate_tests,
    regression_tests,
    deterministic_replay,
    governance_validation,
    run_full_validation,
)


def test_structural_validation():
    res = structural_validation()
    assert res["layer"] == "A_structural"
    assert "schema_versions_ok" in res["checks"] or res["passed"] is True


@patch("core.abraxas_oracle_validation_harness.run_scrubbed_pytest")
def test_candidate_tests(mock_run):
    mock_run.return_value = "........ [100%]"
    res = candidate_tests()
    assert res["layer"] == "B_candidate"
    assert res["passed"] is True


@patch("core.abraxas_oracle_validation_harness.run_scrubbed_pytest")
def test_regression_tests(mock_run):
    mock_run.return_value = "................ [100%]"
    res = regression_tests()
    assert res["layer"] == "C_regression"
    assert res["passed"] is True


def test_deterministic_replay():
    # The function calls other modules; we check it returns a dict with expected keys
    res = deterministic_replay()
    assert res["layer"] == "D_replay"
    assert "passed" in res


def test_governance_validation():
    # Will use default or mocked boundary
    res = governance_validation()
    assert res["layer"] == "E_governance"
    assert "checks" in res


def test_run_full_validation():
    with patch("core.abraxas_oracle_validation_harness.run_scrubbed_pytest", return_value="........ [100%]"):
        res = run_full_validation()
        assert "overall_passed" in res
        assert isinstance(res["overall_passed"], bool)
