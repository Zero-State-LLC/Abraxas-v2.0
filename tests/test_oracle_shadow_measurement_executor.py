"""Tests for core/codegen/oracle_signal/oracle_shadow_measurement_executor.py (HARDENING candidate 89796f6abb1e401b)"""

from core.codegen.oracle_signal.oracle_shadow_measurement_executor import (
    build_oracle_shadow_measurement,
)

def test_build_oracle_shadow_measurement_minimal():
    readiness = {
        "canonical_hash": "read-111",
        "held_out_fixture_refs": [{"fixture_id": "f1"}, {"fixture_id": "f2"}],
    }
    dryrun = {
        "canonical_hash": "dry-222",
        "replay_fixtures": [{"fixture_id": "f1"}],
    }
    schema_receipt = {"canonical_hash": "sch-333"}
    ingest = {"canonical_hash": "ing-444"}

    meas = build_oracle_shadow_measurement(
        timestamp="2026-07-12T00:00:00Z",
        oracle_measurement_readiness=readiness,
        oracle_shadow_dryrun=dryrun,
        oracle_schema_validation_receipt=schema_receipt,
        oracle_ingest_wiring=ingest,
    )

    assert isinstance(meas, dict)
    assert meas["schema_version"] == "OracleShadowMeasurement.v1"
    assert meas["measurement_status"] == "ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY"
    assert "measurement_id" in meas
    assert "measurement_run_refs" in meas
    assert len(meas["held_out_fixture_bindings"]) == 2
    assert "source_packet_hashes" in meas
