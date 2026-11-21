from dataclasses import replace

import pytest

from core.forecasting.models import (
    ForecastClaim,
    ForecastObject,
    ForecastProbability,
    OutcomeBindingStatus,
)
from core.moses.contracts import ArchitecturePacket, GroundingDisposition, LoweringStep
from core.moses.outcomes import build_outcome_receipt
from core.settlement.models import (
    AuthorityRef,
    SettlementConflictSummary,
    SettlementDecision,
    SettlementReason,
    SettlementStatus,
)
from core.settlement.verdict import build_settlement_verdict, settlement_verdict_hash


def _arch():
    return ArchitecturePacket(
        architecture_id="a-1",
        meaning_id="m-1",
        meaning_packet_hash="a" * 64,
        grounding_receipt_id="g-1",
        grounding_receipt_hash="b" * 64,
        grounding_disposition=GroundingDisposition.resolved,
        lowering_trace=(
            LoweringStep(stage="DOMAIN", input_refs=("c-1",), output_refs=("d-1",)),
        ),
    )


def _forecast(fid="f-1", h="f" * 64):
    return ForecastObject(
        "ForecastObject.v1",
        fid,
        ForecastClaim("Expected result"),
        ForecastProbability(0.7),
        "test",
        "P7D",
        "FORECAST",
        "ADVISORY",
        None,
        (),
        OutcomeBindingStatus.BOUND,
        True,
        h,
    )


def _settlement(f):
    return build_settlement_verdict(
        "s-1",
        f.forecast_id,
        f.forecast_hash,
        "bind-1",
        "b" * 64,
        "ev-1",
        "e" * 64,
        SettlementDecision.TRUE,
        (SettlementReason("r-1", "test", "supported", ("ev-1",), "test"),),
        SettlementConflictSummary(False, (), "none", "clear"),
        SettlementStatus.SETTLED,
        "OPERATOR",
        AuthorityRef(
            "TEST_FIXTURE",
            "fixture://settlement-authority",
            "Synthetic test authority only",
        ),
    )


def test_outcome_binds_forecast_and_settlement_as_evidence_only():
    a = _arch()
    f = _forecast()
    s = _settlement(f)
    r = build_outcome_receipt(
        a, outcome_receipt_id="o-1", forecasts=(f,), settlements=(s,)
    )
    assert r.evidence_only is True
    assert r.expected_outcomes[0]["forecast_id"] == "f-1"
    assert r.settlements["settlement_count"] == 1


def test_unknown_forecast_settlement_fails_closed():
    a = _arch()
    f = _forecast()
    other = _forecast("f-2", "d" * 64)
    s = _settlement(other)
    with pytest.raises(ValueError, match="unknown forecast"):
        build_outcome_receipt(
            a, outcome_receipt_id="o-1", forecasts=(f,), settlements=(s,)
        )


def test_forecast_hash_mismatch_fails_closed():
    a = _arch()
    f = _forecast()
    s = _settlement(f)
    bad = replace(s, forecast_hash="0" * 64)
    bad = replace(bad, settlement_hash=settlement_verdict_hash(bad))
    with pytest.raises(ValueError, match="forecast hash mismatch"):
        build_outcome_receipt(
            a, outcome_receipt_id="o-1", forecasts=(f,), settlements=(bad,)
        )


def test_settled_fixture_without_authority_still_fails_closed():
    f = _forecast()
    missing = replace(_settlement(f), authority_ref=None)
    missing = replace(missing, settlement_hash=settlement_verdict_hash(missing))
    with pytest.raises(ValueError, match="invalid settlement verdict"):
        build_outcome_receipt(
            _arch(),
            outcome_receipt_id="o-no-authority",
            forecasts=(f,),
            settlements=(missing,),
        )
