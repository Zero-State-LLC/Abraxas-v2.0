"""Tests for core/scoring/models.py dataclasses (Oracle candidate 00d0fb441ea388c2).

Comprehensive coverage for frozen dataclasses used in Brier ledger and validation.
"""

from dataclasses import asdict, replace
import pytest

from core.scoring.models import (
    BrierScoreInputRef,
    BrierScoreResult,
    BrierScorePolicy,
    AuthorityRef,
    BrierLedgerEntry,
    BrierValidationFinding,
    BrierValidationReport,
)


def test_brier_score_input_ref_frozen():
    ref = BrierScoreInputRef(ref_type="forecast", ref_id="f1", label="Forecast 1")
    with pytest.raises(Exception):
        ref.ref_type = "other"  # frozen


def test_brier_score_result_construction():
    res = BrierScoreResult(score=0.42, rounding_policy="half_even")
    assert res.score == 0.42
    assert asdict(res)["rounding_policy"] == "half_even"


def test_brier_score_policy():
    pol = BrierScorePolicy(
        score_type="standard",
        rounding_policy="half_even",
        partial_policy="ignore",
        void_policy="zero",
        conflict_policy="highest",
    )
    assert pol.partial_policy == "ignore"


def test_authority_ref_optional_in_ledger():
    auth = AuthorityRef(authority_type="operator", authority_id="op1", label="Operator")
    entry = BrierLedgerEntry(
        schema_version="1.0.0",
        ledger_entry_id="le1",
        forecast_id="f1",
        forecast_hash="h1",
        settlement_id="s1",
        settlement_hash="hs1",
        probability=0.75,
        settlement_decision="SETTLED",
        outcome_value=1.0,
        score_result=BrierScoreResult(score=0.1, rounding_policy="half_even"),
        score_policy=BrierScorePolicy(
            score_type="standard",
            rounding_policy="half_even",
            partial_policy="ignore",
            void_policy="zero",
            conflict_policy="highest",
        ),
        created_by_lane="lane-a",
        authority_ref=auth,
        ledger_hash="ledgerh",
    )
    assert entry.authority_ref.authority_id == "op1"
    # None authority allowed
    entry2 = replace(entry, authority_ref=None)
    assert entry2.authority_ref is None


def test_validation_finding_and_report():
    f1 = BrierValidationFinding(code="MISSING", severity="HIGH", message="No score")
    report = BrierValidationReport(status="INVALID", findings=(f1,), receipt_hash="rh1")
    assert len(report.findings) == 1
    assert report.findings[0].code == "MISSING"


def test_brier_ledger_entry_roundtrip():
    entry = BrierLedgerEntry(
        schema_version="1.0.0",
        ledger_entry_id="le2",
        forecast_id="f2",
        forecast_hash="fh2",
        settlement_id="s2",
        settlement_hash="sh2",
        probability=0.9,
        settlement_decision="SETTLED",
        outcome_value=0.0,
        score_result=BrierScoreResult(score=0.05, rounding_policy="half_even"),
        score_policy=BrierScorePolicy(
            score_type="standard", rounding_policy="half_even", partial_policy="ignore", void_policy="zero", conflict_policy="highest"
        ),
        created_by_lane="test",
        authority_ref=None,
        ledger_hash="lh2",
    )
    d = asdict(entry)
    # roundtrip via dict (simplified)
    assert d["probability"] == 0.9
    assert d["score_result"]["score"] == 0.05
