from core.review_continuity.operator_review import ReviewContinuityReviewPacket

def test_operator_review_hash():
    h=ReviewContinuityReviewPacket.compute_hash('c',1,1,1,0)
    p=ReviewContinuityReviewPacket(review_id='1',continuity_hash='c',continuity_chains=1,deferred_sequences=1,denied_sequences=1,unresolved_diagnostics=0,deterministic_review_hash=h,status='passed')
    assert p.continuity_chains==1
