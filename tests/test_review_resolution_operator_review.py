from core.review_resolution.operator_review import ReviewResolutionOperatorReviewPacket

def test_operator_review_packet():
    p = ReviewResolutionOperatorReviewPacket(review_id='1', pending_reviews=1, unresolved_blockers=1, critical_diagnostics=1, pending_actions=['x'], status='blocked')
    assert p.status == 'blocked'
