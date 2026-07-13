"""Tests for core/codegen/oracle_signal/oracle_authorization_decision_record_builder.py (GOVERNANCE candidate d44527dccc1e65b3)"""

from core.codegen.oracle_signal.oracle_authorization_decision_record_builder import build_oracle_authorization_decision_record

def test_build_authorization_decision_record():
    ts = "2026-07-12T00:00:00Z"
    cand = {"canonical_hash": "hash_cand"}
    cand_receipt = {"canonical_hash": "hash_cand_receipt"}
    proposal = {"canonical_hash": "hash_prop"}
    shadow = {"canonical_hash": "hash_shadow"}
    schema = {"canonical_hash": "hash_schema"}

    rec = build_oracle_authorization_decision_record(
        timestamp=ts,
        oracle_measurement_authorization_decision_review_candidate=cand,
        oracle_measurement_authorization_decision_review_candidate_receipt=cand_receipt,
        oracle_measurement_authorization_proposal=proposal,
        oracle_shadow_measurement=shadow,
        oracle_schema_validation_receipt=schema,
    )
    assert rec["schema_version"] == "OracleAuthorizationDecisionRecord.v1"
    assert rec["record_status"] == "ORACLE_AUTHORIZATION_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY"
    assert rec["timestamp"] == ts
    assert "decision_record_id" in rec
    assert rec["source_packet_hashes"]["oracle_shadow_measurement"] == "hash_shadow"
