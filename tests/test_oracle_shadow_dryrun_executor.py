"""Tests for core/codegen/oracle_signal/oracle_shadow_dryrun_executor.py (HARDENING candidate a803dcea6b9b3795)"""

from core.codegen.oracle_signal.oracle_shadow_dryrun_executor import (
    build_oracle_shadow_dryrun,
    _authority_locks,
)

def test_build_oracle_shadow_dryrun():
    wiring = {"canonical_hash": "wire123"}
    schema = {"canonical_hash": "schema456"}
    adv = {
        "canonical_hash": "adv789",
        "fixture_rows": [{"case_id": "case1"}]
    }
    result = build_oracle_shadow_dryrun(
        timestamp="2026-07-12T00:00:00Z",
        oracle_ingest_wiring=wiring,
        oracle_schema_validation_receipt=schema,
        oracle_adversarial_fixture=adv,
    )
    assert isinstance(result, dict)
    assert "dryrun_id" in result or "dryrun_status" in result

def test_authority_locks_are_all_false():
    locks = _authority_locks()
    assert all(v is False for v in locks.values())
    assert "canon_mutation" in locks
    assert "live_oracle_execution" in locks
