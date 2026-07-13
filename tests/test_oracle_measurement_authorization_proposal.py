"""Tests for core/codegen/oracle_signal/oracle_measurement_authorization_proposal.py (HARDENING candidate e279f9e36d45f43b)"""

from core.codegen.oracle_signal.oracle_measurement_authorization_proposal import build_oracle_measurement_authorization_proposal

def test_build_proposal_structure():
    ts = "2026-07-12T00:00:00Z"
    proposal = {"canonical_hash": "hash_prop"}
    proposal_receipt = {"canonical_hash": "hash_prop_rec"}
    shadow = {"canonical_hash": "hash_shadow"}
    readiness = {"canonical_hash": "hash_ready"}
    schema = {"canonical_hash": "hash_schema"}

    rec = build_oracle_measurement_authorization_proposal(
        timestamp=ts,
        oracle_measurement_proposal=proposal,
        oracle_measurement_proposal_receipt=proposal_receipt,
        oracle_shadow_measurement=shadow,
        oracle_measurement_readiness=readiness,
        oracle_schema_validation_receipt=schema,
    )
    assert rec["schema_version"] == "OracleMeasurementAuthorizationProposal.v1"
    assert rec["proposal_status"] == "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    assert rec["timestamp"] == ts
    assert "authorization_proposal_id" in rec
    assert rec["source_packet_hashes"]["oracle_shadow_measurement"] == "hash_shadow"
    assert rec["authorization_scope"]["grants_measurement_authorization"] is False

def test_authorization_scope_advisory():
    ts = "2026-07-12T00:00:00Z"
    proposal = {"canonical_hash": "h1"}
    proposal_receipt = {"canonical_hash": "h2"}
    shadow = {"canonical_hash": "h3"}
    readiness = {"canonical_hash": "h4"}
    schema = {"canonical_hash": "h5"}

    rec = build_oracle_measurement_authorization_proposal(
        timestamp=ts,
        oracle_measurement_proposal=proposal,
        oracle_measurement_proposal_receipt=proposal_receipt,
        oracle_shadow_measurement=shadow,
        oracle_measurement_readiness=readiness,
        oracle_schema_validation_receipt=schema,
    )
    assert rec["authorization_scope"]["operator_gate_required"] is True
    assert rec["authorization_scope"]["grants_measurement_authorization"] is False
    assert rec["operator_gate_template"]["exact_confirmation_required"] == "yes"
