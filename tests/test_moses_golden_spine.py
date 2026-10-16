"""Golden end-to-end fixture for the Moses contract spine.

This test proves deterministic binding across interpretation, grounding,
lowering, forecast/settlement, and outcome evidence. It grants no authority.
"""
from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.signal_graph import SignalGraph
from core.forecasting.models import ForecastClaim, ForecastObject, ForecastProbability, OutcomeBindingStatus
from core.moses.adapters import meaning_packet_from_belief_graph
from core.moses.grounding import compose_grounding_receipt
from core.moses.lowering import build_architecture_packet
from core.moses.outcomes import build_outcome_receipt
from core.settlement.models import SettlementConflictSummary, SettlementDecision, SettlementReason, SettlementStatus
from core.settlement.verdict import build_settlement_verdict

def _run_spine():
    bg=BeliefGraphPacket(claims=(ClaimObject(id="claim-1",statement="Observed operator need",provenance={"source":"golden"},confidence=0.9,status="OBSERVED"),),theories=(),signal_graph=SignalGraph(relationships=()),provenance={"fixture":"moses-golden"})
    meaning=meaning_packet_from_belief_graph(bg,meaning_id="meaning-golden",semantic_invariants=("operator-intent-preserved",))
    grounding=compose_grounding_receipt(meaning,grounding_receipt_id="grounding-golden",evidence_refs=("evidence-golden",),grounding_assertions=({"id":"assertion-golden","status":"SUPPORTED"},))
    architecture=build_architecture_packet(meaning,grounding,architecture_id="architecture-golden",domain={"id":"domain-golden"},requirements=({"id":"req-1","meaning_refs":["claim-1"]},),journeys=({"id":"journey-1","requirement_refs":["req-1"]},),workflows=({"id":"wf-1","journey_refs":["journey-1"]},),state_transitions=({"id":"state-1","workflow_refs":["wf-1"]},),contracts=({"id":"contract-1","state_transition_refs":["state-1"]},),acceptance_tests=({"id":"acceptance-1","contract_refs":["contract-1"]},),implementation_tasks=({"id":"task-1","acceptance_test_refs":["acceptance-1"]},))
    forecast=ForecastObject("ForecastObject.v1","forecast-golden",ForecastClaim("Acceptance condition will be observed"),ForecastProbability(0.8),"moses-golden","P7D","FORECAST","ADVISORY",None,(),OutcomeBindingStatus.BOUND,True,"f"*64)
    settlement=build_settlement_verdict("settlement-golden",forecast.forecast_id,forecast.forecast_hash,"binding-golden","b"*64,"evidence-packet-golden","e"*64,SettlementDecision.TRUE,(SettlementReason("reason-1","GOLDEN","Fixture evidence supports outcome",("evidence-packet-golden",),"GOLDEN_TEST"),),SettlementConflictSummary(False,(),"NO_CONFLICT","CLEAR"),SettlementStatus.SETTLED,"OPERATOR",None)
    outcome=build_outcome_receipt(architecture,outcome_receipt_id="outcome-golden",forecasts=(forecast,),settlements=(settlement,),observed_outcomes=({"id":"observed-1","result":"acceptance-observed"},))
    return meaning,grounding,architecture,outcome

def test_golden_spine_is_deterministic_and_semantically_bound():
    first=_run_spine(); second=_run_spine()
    assert tuple(x.canonical_hash for x in first)==tuple(x.canonical_hash for x in second)
    meaning,grounding,architecture,outcome=first
    assert grounding.meaning_packet_hash==meaning.canonical_hash
    assert architecture.meaning_packet_hash==meaning.canonical_hash
    assert architecture.grounding_receipt_hash==grounding.canonical_hash
    assert outcome.architecture_packet_hash==architecture.canonical_hash
    assert all("operator-intent-preserved" in step.preserved_invariants for step in architecture.lowering_trace)
    assert outcome.evidence_only is True