from core.review_resolution.closure import ReviewResolutionClosurePacket

def test_closure_blocked_by_critical():
    h = ReviewResolutionClosurePacket.compute_hash('p','o',1,1,False)
    c = ReviewResolutionClosurePacket(closure_id='1', posture_hash='p', outcome_hash='o', unresolved_blocker_count=1, critical_blocker_count=1, closure_ready=False, deterministic_closure_hash=h, status='passed')
    assert c.closure_ready is False
