from core.operator_queue.decisions import OperatorDecisionPacket

def test_decision_packet_hash():
    op = OperatorDecisionPacket.hash_operator_id("op")
    h = OperatorDecisionPacket.compute_hash("rq", op, "deny", "x", True)
    p = OperatorDecisionPacket(decision_id="1", request_hash="rq", operator_id_hash=op, decision="deny", decision_reason="x", requires_additional_review=True, deterministic_decision_hash=h, status="passed")
    assert p.operator_id_hash == op
