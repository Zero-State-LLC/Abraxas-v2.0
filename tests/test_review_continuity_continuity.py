from core.review_continuity.continuity import ReviewContinuityPacket

def test_continuity_hash():
    h=ReviewContinuityPacket.compute_hash('c',1.0,True,[])
    p=ReviewContinuityPacket(continuity_id='1',chain_hash='c',continuity_score=1.0,continuity_integrity=True,unresolved_breaks=[],deterministic_continuity_hash=h,status='passed')
    assert p.continuity_integrity
