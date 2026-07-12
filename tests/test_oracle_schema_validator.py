"""Comprehensive tests for core/codegen/oracle_signal/oracle_schema_validator.py

GOVERNANCE class candidate. Covers schema loading, packet validation, multi-packet validation,
receipt building, authority locks (all False), advisory-only invariants, and determinism.
"""

import json
from pathlib import Path
from typing import Any, Mapping

import pytest

from core.codegen.oracle_signal.oracle_schema_validator import (
    _authority_locks,
    load_oracle_schema,
    validate_oracle_packet,
    validate_oracle_schema_packets,
    build_oracle_schema_validation_receipt,
)


def test_authority_locks_all_false():
    locks = _authority_locks()
    assert isinstance(locks, dict)
    assert len(locks) > 0
    assert all(v is False for v in locks.values()), "All authority locks must remain False (advisory only)"


def test_load_oracle_schema_smoke():
    # Use a known schema that exists
    schema = load_oracle_schema("contracts/canon/oracle/oracle_signal_envelope.v1.schema.json")
    assert isinstance(schema, dict)
    assert "title" in schema or "$schema" in schema or "properties" in schema


def test_validate_oracle_packet_valid_advisory():
    packet = {
        "packet_key": "test",
        "data": {"foo": "bar"},
        "canonical_hash": "dummyhash123",
    }
    # Note: real validation may depend on schema; we test structure + advisory status
    result = validate_oracle_packet(
        packet_key="oracle_signal_envelope",
        packet=packet,
        schema_path="contracts/canon/oracle/oracle_signal_envelope.v1.schema.json",
        timestamp="2026-07-12T00:00:00Z",
    )
    assert result["schema_version"] == "OracleSchemaValidationResult.v1"
    assert result["advisory_only"] is True
    assert result["canon_mutation"] is False
    assert result["runtime_mutation"] is False
    assert "validation_status" in result
    assert "canonical_hash" in result


def test_validate_oracle_schema_packets_multiple():
    packets = {
        "oracle_signal_envelope": {"packet_key": "env", "data": {}},
        "oracle_holler_intake": {"packet_key": "holler", "data": {}},
    }
    results = validate_oracle_schema_packets(
        packets=packets,
        timestamp="2026-07-12T00:00:00Z",
    )
    assert len(results) == 2
    for key, res in results.items():
        assert res["advisory_only"] is True
        assert "validation_status" in res


def test_build_receipt_all_valid():
    fake_results = {
        "k1": {"validation_status": "VALID_ADVISORY_ONLY", "canonical_hash": "h1"},
        "k2": {"validation_status": "VALID_ADVISORY_ONLY", "canonical_hash": "h2"},
    }
    receipt = build_oracle_schema_validation_receipt(
        timestamp="2026-07-12T00:00:00Z",
        merge_sha="abc123",
        validation_results=fake_results,
    )
    assert receipt["schema_version"] == "OracleSchemaValidationReceipt.v1"
    assert receipt["receipt_status"] == "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    assert receipt["validation_summary"]["all_valid"] is True
    assert receipt["validation_summary"]["valid_result_count"] == 2


def test_deterministic_hash_stable():
    packet = {"packet_key": "env", "data": {"a": 1}, "canonical_hash": "h"}
    r1 = validate_oracle_packet(
        packet_key="oracle_signal_envelope",
        packet=packet,
        schema_path="contracts/canon/oracle/oracle_signal_envelope.v1.schema.json",
        timestamp="2026-07-12T00:00:00Z",
    )
    r2 = validate_oracle_packet(
        packet_key="oracle_signal_envelope",
        packet=packet,
        schema_path="contracts/canon/oracle/oracle_signal_envelope.v1.schema.json",
        timestamp="2026-07-12T00:00:00Z",
    )
    assert r1["canonical_hash"] == r2["canonical_hash"]


if __name__ == "__main__":
    pytest.main([__file__, "-q"])