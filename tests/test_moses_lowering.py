import pytest
from core.moses.contracts import MeaningPacket, MeaningStatus
from core.moses.grounding import compose_grounding_receipt
from core.moses.lowering import build_architecture_packet

def _inputs():
    m=MeaningPacket(meaning_id="m-1",observations=({"claim_id":"c-1","statement":"signal"},),semantic_invariants=("preserve-intent",),status=MeaningStatus.provisional)
    g=compose_grounding_receipt(m,grounding_receipt_id="g-1",evidence_refs=("e-1",),grounding_assertions=({"id":"a-1","status":"SUPPORTED"},))
    return m,g,dict(architecture_id="a-1",domain={"id":"d-1"},requirements=({"id":"r-1","meaning_refs":["c-1"]},),journeys=({"id":"j-1","requirement_refs":["r-1"]},),workflows=({"id":"w-1","journey_refs":["j-1"]},),state_transitions=({"id":"s-1","workflow_refs":["w-1"]},),contracts=({"id":"ct-1","state_transition_refs":["s-1"]},),acceptance_tests=({"id":"at-1","contract_refs":["ct-1"]},),implementation_tasks=({"id":"t-1","acceptance_test_refs":["at-1"]},))

def test_full_chain_emits_architecture_packet():
    m,g,k=_inputs(); p=build_architecture_packet(m,g,**k)
    assert len(p.lowering_trace)==9
    assert p.implementation_tasks[0]["id"]=="t-1"
    assert all("preserve-intent" in s.preserved_invariants for s in p.lowering_trace)

def test_broken_trace_fails_closed():
    m,g,k=_inputs(); k["workflows"]=({"id":"w-1","journey_refs":["missing"]},)
    with pytest.raises(ValueError): build_architecture_packet(m,g,**k)

def test_wrong_grounding_binding_fails_closed():
    m,g,k=_inputs(); other=MeaningPacket(meaning_id="m-2",observations=({"claim_id":"c-2"},),status=MeaningStatus.provisional)
    with pytest.raises(ValueError): build_architecture_packet(other,g,**k)