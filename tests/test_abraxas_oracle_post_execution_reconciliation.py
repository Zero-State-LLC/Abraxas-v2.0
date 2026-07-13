"""Tests for core/abraxas_oracle_post_execution_reconciliation.py (HARDENING candidate 8ba87f3572fedc5c)"""

from core.abraxas_oracle_post_execution_reconciliation import reconcile

def test_reconcile_returns_structure():
    rec = reconcile()
    assert isinstance(rec, dict)
    assert "candidate_id" in rec
    assert rec["status"] == "SATISFIED_ENGINEERING_COMPLETE"
    assert "implementation_evidence" in rec
    assert "authority_unchanged" in rec
    assert rec["authority_unchanged"]["canon"] == "UNCHANGED"
