"""Tests for core/codegen/oracle_signal/oracle_persistent_execution_secret_vault_plan.py (HARDENING candidate fe85d07b77e73482)"""

from core.codegen.oracle_signal.oracle_persistent_execution_secret_vault_plan import (
    build_oracle_persistent_execution_secret_vault_plan,
    build_oracle_persistent_execution_secret_vault_plan_receipt,
)

def test_build_plan_basic_structure():
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_endpoint_env_intake_receipt={"canonical_hash": "hash1"},
        oracle_full_live_runtime_preflight_receipt={"canonical_hash": "hash2"},
        oracle_full_live_runtime_execution_attempt_receipt={
            "canonical_hash": "hash3",
            "receipt_status": "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED",
        },
    )
    assert plan["schema_version"] == "OraclePersistentExecutionSecretVaultPlan.v1"
    assert plan["plan_status"] == "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
    assert plan["persistent_execution_boundaries"]["persistent_execution_enabled"] is False
    assert plan["persistent_execution_boundaries"]["runtime_mode"] == "SANDBOX_GATED_PLANNING_ONLY"
    assert "canonical_hash" in plan

def test_plan_has_authority_locks():
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_endpoint_env_intake_receipt={"canonical_hash": "h1"},
        oracle_full_live_runtime_preflight_receipt={"canonical_hash": "h2"},
        oracle_full_live_runtime_execution_attempt_receipt={"canonical_hash": "h3", "receipt_status": "BLOCKED"},
    )
    locks = plan.get("authority_locks", {})
    assert locks.get("persistent_production_runtime_activation") is False
    assert locks.get("canon_mutation") is False

def test_plan_secret_handling_requirements():
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_endpoint_env_intake_receipt={"canonical_hash": "h1"},
        oracle_full_live_runtime_preflight_receipt={"canonical_hash": "h2"},
        oracle_full_live_runtime_execution_attempt_receipt={"canonical_hash": "h3", "receipt_status": "BLOCKED"},
    )
    reqs = plan.get("secret_handling_requirements", [])
    assert any("SECRET_MATERIAL_NEVER_IN_REPO" in str(r) for r in reqs)

def test_receipt_builder():
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_endpoint_env_intake_receipt={"canonical_hash": "h1"},
        oracle_full_live_runtime_preflight_receipt={"canonical_hash": "h2"},
        oracle_full_live_runtime_execution_attempt_receipt={"canonical_hash": "h3", "receipt_status": "BLOCKED"},
    )
    receipt = build_oracle_persistent_execution_secret_vault_plan_receipt(
        timestamp="2026-07-12T00:00:00Z",
        merge_sha="testsha",
        oracle_persistent_execution_secret_vault_plan=plan,
        observability_hook={"canonical_hash": "obs_hash"},
    )
    assert "canonical_hash" in receipt or "plan_id" in receipt
