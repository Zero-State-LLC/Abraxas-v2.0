from core.operator_queue.rationale import OperatorRationalePacket

def test_rationale_hash():
    h = OperatorRationalePacket.compute_hash("d", "s", [], [], [])
    p = OperatorRationalePacket(rationale_id="1", decision_hash="d", rationale_summary="s", cited_diagnostics=[], cited_containment_restrictions=[], cited_governance_events=[], deterministic_rationale_hash=h, status="passed")
    assert p.deterministic_rationale_hash == h
