from core.review_resolution.outcomes import ReviewResolutionOutcomePacket

def test_outcome_packet():
    h = ReviewResolutionOutcomePacket.compute_hash('p','blocked','r',False)
    o = ReviewResolutionOutcomePacket(outcome_id='1', posture_hash='p', outcome_state='blocked', outcome_reason='r', closure_ready=False, deterministic_outcome_hash=h, status='passed')
    assert o.closure_ready is False
