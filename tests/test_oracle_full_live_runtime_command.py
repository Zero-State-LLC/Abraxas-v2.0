"""Tests for core/codegen/oracle_signal/oracle_full_live_runtime_command.py (HARDENING candidate 87810b9eb279ee9f)"""

from core.codegen.oracle_signal.oracle_full_live_runtime_command import (
    build_oracle_full_live_runtime_command,
    FULL_LIVE_RUN_CONTROL_RECEIPT_HASH,
)

def test_schema_and_constants():
    assert FULL_LIVE_RUN_CONTROL_RECEIPT_HASH
    assert isinstance(FULL_LIVE_RUN_CONTROL_RECEIPT_HASH, str)

def test_build_oracle_full_live_runtime_command_minimal():
    run_control = {"canonical_hash": "runctrl-abc123"}
    run_control_receipt = {"canonical_hash": "runrec-xyz789"}
    schema_receipt = {"canonical_hash": "schrec-111222"}

    cmd = build_oracle_full_live_runtime_command(
        timestamp="2026-07-12T00:00:00Z",
        oracle_full_live_run_control=run_control,
        oracle_full_live_run_control_receipt=run_control_receipt,
        oracle_schema_validation_receipt=schema_receipt,
    )

    assert isinstance(cmd, dict)
    assert cmd["schema_version"] == "OracleFullLiveRuntimeCommand.v1"
    assert cmd["runtime_command_status"] == "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY"
    assert "runtime_command_id" in cmd
    assert "source_packet_hashes" in cmd
    assert cmd["operator_monitoring_gate"]["operator_console_required"] is True
    assert isinstance(cmd.get("runtime_command_manifest"), list)
    assert len(cmd["runtime_command_manifest"]) >= 1
