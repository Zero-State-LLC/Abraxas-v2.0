"""Tests for core/codegen/oracle_signal/oracle_signal_intake_builder.py (HARDENING candidate ecceff7bfb6f41c6)"""

from core.codegen.oracle_signal.oracle_signal_intake_builder import (
    build_oracle_signal_envelope,
    build_oracle_holler_intake,
    build_oracle_signal_layer_completion_receipt,
    ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
    _authority_locks,
)

def test_schema_paths_present():
    assert len(ORACLE_CANON_EXTENSION_SCHEMA_PATHS) >= 10
    assert any("oracle_signal_envelope" in p for p in ORACLE_CANON_EXTENSION_SCHEMA_PATHS)

def test_authority_locks_all_false():
    locks = _authority_locks()
    assert all(v is False for v in locks.values())
    assert "canon_mutation" in locks
    assert "runtime_mutation" in locks

def test_build_oracle_signal_envelope():
    source_ref = {"ref": "test_source"}
    payload_ref = {"ref": "test_payload"}
    env = build_oracle_signal_envelope(
        timestamp="2026-07-12T00:00:00Z",
        source_ref=source_ref,
        payload_ref=payload_ref,
    )
    assert env["schema_version"] == "OracleSignalEnvelope.v1"
    assert "authority_locks" in env
    assert env["authority_locks"]["canon_mutation"] is False
    assert env["canon_mutation"] is False

def test_build_oracle_holler_intake():
    intake = build_oracle_holler_intake(
        timestamp="2026-07-12T00:00:00Z",
        batch_id="b1",
        sport="football",
        market_count=5,
        calibration_policy="default",
        adversarial_fixture_count=2,
    )
    assert "intake_id" in intake
    assert intake.get("holler_batch", {}).get("batch_id") == "b1"
    assert intake["holler_batch"]["market_count"] == 5

def test_completion_receipt_minimal():
    # Build minimal dependents
    source_ref = {"ref": "s"}
    payload_ref = {"ref": "p"}
    env = build_oracle_signal_envelope(timestamp="2026-07-12T00:00:00Z", source_ref=source_ref, payload_ref=payload_ref)
    holler = build_oracle_holler_intake(
        timestamp="2026-07-12T00:00:00Z",
        batch_id="b1",
        sport="football",
        market_count=1,
        calibration_policy="default",
        adversarial_fixture_count=0,
    )
    # Minimal stubs for other required args
    cal = {"canonical_hash": "calhash", "report_id": "r"}
    adv = {"canonical_hash": "advhash"}
    ingest = {"canonical_hash": "ingest"}
    obs = {"canonical_hash": "obs"}
    rec = build_oracle_signal_layer_completion_receipt(
        timestamp="2026-07-12T00:00:00Z",
        merge_sha="abc123",
        signal_envelope=env,
        holler_intake=holler,
        calibration_report=cal,
        adversarial_fixture=adv,
        ingest_stub=ingest,
        observability_hook=obs,
    )
    assert "receipt_id" in rec
    assert rec.get("canon_extension_only") is True or "canon_extension" in str(rec.get("provenance", {}))