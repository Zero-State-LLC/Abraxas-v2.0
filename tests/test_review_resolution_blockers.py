from core.review_resolution.blockers import ReviewResolutionBlockerPacket

def test_blocker_packet():
    h = ReviewResolutionBlockerPacket.compute_hash('p','replay_mismatch','m','critical')
    b = ReviewResolutionBlockerPacket(blocker_id='1', posture_hash='p', blocker_type='replay_mismatch', blocker_reason='m', severity='critical', deterministic_blocker_hash=h, status='passed')
    assert b.severity == 'critical'
