"""Tests for core/codegen/oracle_signal/oracle_persistent_execution_secret_vault_plan.py (candidate fe85d07b77e73482)"""

import pytest
from core.codegen.oracle_signal.oracle_persistent_execution_secret_vault_plan import (
    ISSUE_881_TITLE,
    PR_880_MERGE_SHA,
    RUNTIME_MIRROR_PACKET_HASH,
    RUNTIME_EXECUTION_ATTEMPT_BLOCKED_HASH,
    build_oracle_persistent_execution_secret_vault_plan,
)

def test_constants():
    assert "Persistent Execution + Secret Vault" in ISSUE_881_TITLE
    assert len(PR_880_MERGE_SHA) == 40
    assert len(RUNTIME_MIRROR_PACKET_HASH) == 64
    assert len(RUNTIME_EXECUTION_ATTEMPT_BLOCKED_HASH) == 64

def test_build_plan_basic_structure():
    receipt = {"canonical_hash": "a" * 64, "receipt_status": "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"}
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_endpoint_env_intake_receipt={"canonical_hash": "a" * 64},
        oracle_full_live_runtime_preflight_receipt={"canonical_hash": "b" * 64},
        oracle_full_live_runtime_execution_attempt_receipt=receipt,
    )
    assert plan["schema_version"] == "OraclePersistentExecutionSecretVaultPlan.v1"
    assert "plan_id" in plan
    assert plan["plan_status"] == "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
    assert "secret_handling_requirements" in plan
    assert len(plan["secret_handling_requirements"]) > 0
    assert plan["runtime_receipt_gate"]["current_execution_attempt_status"] == "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"

def test_build_plan_requires_receipts():
    with pytest.raises(KeyError):
        build_oracle_persistent_execution_secret_vault_plan(
            timestamp="2026-07-12T00:00:00Z",
            oracle_full_live_endpoint_env_intake_receipt={},
            oracle_full_live_runtime_preflight_receipt={},
            oracle_full_live_runtime_execution_attempt_receipt={},
        )
