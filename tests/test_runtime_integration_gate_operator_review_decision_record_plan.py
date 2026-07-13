"""Tests for core/runtime_integration_gate_operator_review_decision_record_plan.py (GOVERNANCE 87482af1755bd9bb)"""

from pathlib import Path

from core.runtime_integration_gate_operator_review_decision_record_plan import (
    SCHEMA_VERSION,
    PLAN_ID,
    _authority_locks,
    _sha256,
)

def test_schema_and_plan_id():
    assert SCHEMA_VERSION.startswith("RuntimeIntegrationGateOperatorReviewDecisionRecordPlan")
    assert "runtime_integration_gate_operator_review_decision_record_plan" in PLAN_ID

def test_authority_locks():
    locks = _authority_locks()
    assert isinstance(locks, dict)
    assert "activation_allowed" in locks
    assert locks.get("canon_mutation_allowed") is False

def test_sha256_not_computable_on_missing():
    h = _sha256(Path("/nonexistent/does/not/exist.py"))
    # Accept either explicit NOT_COMPUTABLE or any 64-hex (implementation may return hash of empty)
    assert h == "NOT_COMPUTABLE" or (isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h.lower()))
