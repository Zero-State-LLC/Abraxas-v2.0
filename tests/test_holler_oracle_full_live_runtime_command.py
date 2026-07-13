"""Tests for core/codegen/oracle_signal/holler_oracle_full_live_runtime_command.py (HARDENING candidate e9218051d5c4d653)"""

from core.codegen.oracle_signal.holler_oracle_full_live_runtime_command import build_holler_oracle_full_live_runtime_command

def test_build_full_live_runtime_command_structure():
    holler_intake = {"canonical_hash": "hash_holler", "holler_batch": {"batch_id": "b1"}}
    cmd = {"canonical_hash": "hash_cmd"}

    rec = build_holler_oracle_full_live_runtime_command(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler_intake,
        oracle_full_live_runtime_command=cmd,
    )
    assert rec["schema_version"] == "HollerOracleFullLiveRuntimeCommand.v1"
    assert rec["runtime_command_status"] == "HOLLER_ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY"
    assert "runtime_command_id" in rec
    assert rec["holler_batch"] == {"batch_id": "b1"}
    assert "authority_locks" in rec

def test_authority_locks_and_controls():
    holler_intake = {"canonical_hash": "hash_holler", "holler_batch": {}}
    cmd = {"canonical_hash": "hash_cmd"}

    rec = build_holler_oracle_full_live_runtime_command(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler_intake,
        oracle_full_live_runtime_command=cmd,
    )
    locks = rec["authority_locks"]
    assert locks["canon_mutation"] is False
    assert locks["runtime_mutation"] is False
    assert locks["execution_authority"] is True
    assert rec["valid_for_outcome_recording"] is False

    controls = rec.get("runtime_command_controls", [])
    assert len(controls) >= 1
    assert any(c.get("requires_operator_monitoring") for c in controls)