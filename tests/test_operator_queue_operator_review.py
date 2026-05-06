from core.operator_queue.operator_review import OperatorQueueReviewPacket

def test_review_hash():
    h = OperatorQueueReviewPacket.compute_hash("q",1,0,0,1,0)
    p = OperatorQueueReviewPacket(review_id="1", queue_hash="q", pending_requests=1, deferred_requests=0, denied_requests=0, review_only_approved_requests=1, unresolved_diagnostics=0, deterministic_review_hash=h, status="passed")
    assert p.pending_requests == 1
