"""Tests for core/metric_operator_rank5_candidate_audit.py (HARDENING candidate c16b1e864491b757)"""

from core.metric_operator_rank5_candidate_audit import (
    build_metric_operator_rank5_candidate_audit,
    validate_metric_operator_rank5_candidate_audit,
    default_candidate_entries,
    default_output_contract,
    LOCKED_FALSE_FLAGS,
    MetricOperatorRank5CandidateAuditValidationError,
)

def test_build_and_validate():
    payload = {
        "audit_id": "audit-001",
        "created_at_utc": "2026-07-12T00:00:00Z",
        "candidate_entries": default_candidate_entries(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {"source": "test"},
        "audit_level": "MEDIUM",
        "selection_status": "RANK5_CANDIDATE_SELECTED",
        "audit_status": "RANK5_CANDIDATE_SELECTED",
        "recommended_rank5": "TRANSPORT",
        "completed_operators": ["NORM_GEOMETRY"],
    }
    audit = build_metric_operator_rank5_candidate_audit(payload)
    assert isinstance(audit, dict)
    assert "schema_version" in audit
    validate_metric_operator_rank5_candidate_audit(audit)

def test_validation_error():
    bad = {"audit_id": "bad", "candidate_entries": [], "governance_flags": {}, "provenance": {}, "output_contract": {}, "audit_level": "LOW", "selection_status": "RANK5_CANDIDATE_SELECTED"}
    try:
        build_metric_operator_rank5_candidate_audit(bad)
        assert False
    except MetricOperatorRank5CandidateAuditValidationError:
        pass
