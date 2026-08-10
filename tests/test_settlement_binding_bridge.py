import pytest

from core.brier.runtime import build_brier_ledger
from core.settlement import (
    is_score_ready,
    observed_outcome_from_verdict,
    settlement_verdict_from_outcome_binding,
    validate_settlement_verdict,
)
from core.settlement.models import AuthorityRef, SettlementDecision, SettlementStatus

AUTHORITY = AuthorityRef("MANUAL_RECEIPT", "receipt://settlement/approval", "Operator settlement receipt")


def _binding(status: str = "matched") -> dict:
    return {
        "schema_version": "ForecastOutcomeBindingPacket.v1",
        "binding_id": "ob-1",
        "forecast_hash": "fhash",
        "expected_outcome_hash": "ehash-expected",
        "observed_outcome_hash": "ehash-observed" if status in {"matched", "mismatched"} else None,
        "binding_status": status,
        "status": "open",
    }


def _verdict(binding_status: str = "matched", authority=AUTHORITY):
    return settlement_verdict_from_outcome_binding(
        _binding(binding_status),
        settlement_id="sv-1",
        forecast_id="fc-1",
        evidence_packet_id="ep-1",
        evidence_hash="ehash",
        created_by_lane="OPERATOR",
        authority_ref=authority,
    )


def test_matched_with_authority_settled_true_score_ready():
    v = _verdict("matched")
    assert v.settlement_status == SettlementStatus.SETTLED
    assert v.decision == SettlementDecision.TRUE
    assert validate_settlement_verdict(v).status == "PASS"
    assert is_score_ready(v)
    assert observed_outcome_from_verdict(v) == 1


def test_mismatched_with_authority_settled_false_outcome_zero():
    v = _verdict("mismatched")
    assert v.decision == SettlementDecision.FALSE
    assert is_score_ready(v)
    assert observed_outcome_from_verdict(v) == 0


def test_matched_without_authority_stays_draft_not_score_ready():
    v = _verdict("matched", authority=None)
    assert v.settlement_status == SettlementStatus.DRAFT
    assert not is_score_ready(v)
    with pytest.raises(ValueError):
        observed_outcome_from_verdict(v)


def test_unresolved_maps_to_draft_not_computable():
    v = _verdict("unresolved")
    assert v.settlement_status == SettlementStatus.DRAFT
    assert v.decision == SettlementDecision.NOT_COMPUTABLE
    assert not is_score_ready(v)


def test_expired_maps_to_void_not_score_ready():
    v = _verdict("expired")
    assert v.settlement_status == SettlementStatus.VOID
    assert v.decision == SettlementDecision.VOID
    assert not is_score_ready(v)
    with pytest.raises(ValueError):
        observed_outcome_from_verdict(v)


def test_unknown_binding_status_raises():
    with pytest.raises(ValueError):
        _verdict("garbage")


def test_deterministic_settlement_hash():
    assert _verdict("matched").settlement_hash == _verdict("matched").settlement_hash
    assert _verdict("matched").settlement_hash != _verdict("mismatched").settlement_hash


def _forecast_packets() -> dict:
    return {
        "candidate": {"candidate_hash": "fhash"},
        "probability": {"probability": 0.75},
        "calibration": {"calibration_score": 0.9, "deterministic_calibration_hash": "chash"},
    }


def test_brier_ledger_uses_settlement_verdict_outcome():
    result = build_brier_ledger(_forecast_packets(), {}, settlement_verdict=_verdict("matched"))
    assert result["score"]["observed_outcome"] == 1
    result = build_brier_ledger(_forecast_packets(), {}, settlement_verdict=_verdict("mismatched"))
    assert result["score"]["observed_outcome"] == 0


def test_brier_ledger_fails_closed_on_non_score_ready_verdict():
    with pytest.raises(ValueError):
        build_brier_ledger(_forecast_packets(), {}, settlement_verdict=_verdict("matched", authority=None))


def test_brier_ledger_legacy_binding_status_path_unchanged():
    assert build_brier_ledger(_forecast_packets(), {"binding_status": "matched"})["score"]["observed_outcome"] == 1
    assert build_brier_ledger(_forecast_packets(), {"binding_status": "mismatched"})["score"]["observed_outcome"] == 0
