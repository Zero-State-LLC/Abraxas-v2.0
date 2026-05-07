from core.review_resolution.posture import ReviewResolutionPosturePacket

def test_posture_hash_deterministic():
    h = ReviewResolutionPosturePacket.compute_hash('a','b','c','d','blocked',['x'])
    p = ReviewResolutionPosturePacket(posture_id='1', request_hash='a', queue_hash='b', continuity_hash='c', firewall_hash='d', resolution_posture='blocked', unresolved_blockers=['x'], deterministic_posture_hash=h, status='passed')
    assert p.deterministic_posture_hash == h
