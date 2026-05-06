from core.operator_queue.continuity import OperatorQueueContinuityPacket

def test_continuity():
    h = OperatorQueueContinuityPacket.compute_hash("q",1.0,[],True)
    p = OperatorQueueContinuityPacket(continuity_id="1", queue_hash="q", continuity_score=1.0, unresolved_events=[], continuity_safe=True, deterministic_continuity_hash=h, status="passed")
    assert p.continuity_safe
