"""Outcome composition bridge for the Moses contract spine."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from core.forecasting.models import ForecastObject
from core.moses.contracts import ArchitecturePacket, OutcomeReceipt
from core.settlement.models import SettlementStatus, SettlementVerdict
from core.settlement.verdict import validate_settlement_verdict

def build_outcome_receipt(architecture: ArchitecturePacket, *, outcome_receipt_id: str, forecasts: tuple[ForecastObject,...], settlements: tuple[SettlementVerdict,...], observed_outcomes: tuple[dict[str,Any],...]=(), deviations: tuple[dict[str,Any],...]=(), evidence_refs: tuple[str,...]=()) -> OutcomeReceipt:
    """Bind declared expectations to existing settlement evidence without promotion."""
    forecast_by_id={f.forecast_id:f for f in forecasts}
    if len(forecast_by_id)!=len(forecasts): raise ValueError("forecast ids must be unique")
    settled=[]
    settlement_evidence=set(evidence_refs)
    for verdict in settlements:
        report=validate_settlement_verdict(verdict)
        if report.status not in {"PASS","VALID"}: raise ValueError(f"invalid settlement verdict: {verdict.settlement_id}")
        forecast=forecast_by_id.get(verdict.forecast_id)
        if forecast is None: raise ValueError(f"settlement references unknown forecast: {verdict.forecast_id}")
        if verdict.forecast_hash != forecast.forecast_hash: raise ValueError(f"settlement forecast hash mismatch: {verdict.settlement_id}")
        if verdict.settlement_status == SettlementStatus.DRAFT: raise ValueError("draft settlement cannot enter OutcomeReceipt")
        settlement_evidence.add(verdict.evidence_hash)
        settled.append({"settlement_id":verdict.settlement_id,"settlement_hash":verdict.settlement_hash,"forecast_id":verdict.forecast_id,"decision":verdict.decision.value,"status":verdict.settlement_status.value,"evidence_hash":verdict.evidence_hash})
    expected=tuple({"forecast_id":f.forecast_id,"forecast_hash":f.forecast_hash,"claim":f.claim.statement,"probability":f.probability.value,"domain":f.domain,"horizon":f.horizon,"outcome_binding_status":f.outcome_binding_status.value} for f in forecasts)
    return OutcomeReceipt(outcome_receipt_id=outcome_receipt_id,architecture_id=architecture.architecture_id,architecture_packet_hash=architecture.canonical_hash or architecture.computed_canonical_hash(),expected_outcomes=expected,observed_outcomes=observed_outcomes,settlements={"verdicts":settled,"settlement_count":len(settled),"three_settlement_doctrine_preserved":True},deviations=deviations,evidence_refs=tuple(sorted(settlement_evidence)),provenance=({"source":"MosesOutcomeBridge.v1","authority":"EVIDENCE_ONLY","architecture_packet_hash":architecture.canonical_hash},))