"""Tests for core/codegen/oracle_signal/oracle_full_live_endpoint_env_intake.py (HARDENING candidate f06c520be31781cf)"""

from core.codegen.oracle_signal.oracle_full_live_endpoint_env_intake import (
    build_oracle_full_live_endpoint_env_intake,
    REQUIRED_ENDPOINT_ENV_VARS,
)

def test_required_env_vars():
    assert "ORACLE_SIGNAL_ENDPOINT_URL" in REQUIRED_ENDPOINT_ENV_VARS
    assert "HOLLERSPORTS_BATCH_ENDPOINT_URL" in REQUIRED_ENDPOINT_ENV_VARS

def test_build_endpoint_env_intake():
    preflight = {
        "canonical_hash": "preflighthash123",
        "missing_endpoint_env_vars": ["ORACLE_SIGNAL_ENDPOINT_URL"],
    }
    intake = build_oracle_full_live_endpoint_env_intake(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_runtime_preflight_receipt=preflight,
    )
    assert intake["schema_version"] == "OracleFullLiveEndpointEnvIntake.v1"
    assert intake["intake_status"] == "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_READY"
    assert "intake_id" in intake
    assert len(intake["endpoint_env_requirements"]) == 2
    reqs = intake["endpoint_env_requirements"]
    assert any(r["endpoint_env_var"] == "ORACLE_SIGNAL_ENDPOINT_URL" for r in reqs)
    assert any(r["observed_preflight_state"] == "missing" for r in reqs)

def test_missing_env_handling():
    preflight = {
        "canonical_hash": "preflighthash456",
        "missing_endpoint_env_vars": [],
    }
    intake = build_oracle_full_live_endpoint_env_intake(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_runtime_preflight_receipt=preflight,
    )
    statuses = [req["observed_preflight_state"] for req in intake["endpoint_env_requirements"]]
    assert all(s == "present" for s in statuses)