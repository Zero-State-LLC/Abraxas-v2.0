"""Tests for core/codegen/oracle_signal/oracle_measurement_authorization_decision_review_candidate.py (GOVERNANCE candidate b5a2cb48f8ba2fe4)"""

from core.codegen.oracle_signal.oracle_measurement_authorization_decision_review_candidate import (
    build_oracle_measurement_authorization_decision_review_candidate,
)

def test_build_oracle_measurement_authorization_decision_review_candidate():
    proposal = {"canonical_hash": "prop123"}
    proposal_receipt = {"canonical_hash": "rec456"}
    measurement = {"canonical_hash": "meas789"}
    shadow = {"canonical_hash": "shad012"}
    schema = {"canonical_hash": "sch345"}

    result = build_oracle_measurement_authorization_decision_review_candidate(
        timestamp="2026-07-12T00:00:00Z",
        oracle_measurement_authorization_proposal=proposal,
        oracle_measurement_authorization_proposal_receipt=proposal_receipt,
        oracle_measurement_proposal=measurement,
        oracle_shadow_measurement=shadow,
        oracle_schema_validation_receipt=schema,
    )
    assert isinstance(result, dict)
    assert "decision_review_candidate_id" in result
    assert result.get("candidate_status") == "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_READY_ADVISORY_ONLY"
    assert "decision_review_scope" in result
    assert result["decision_review_scope"]["operator_gate_required"] is True
    assert result["decision_review_scope"]["records_authorization_decision"] is False
