from core.review_continuity.replay import ReviewContinuityReplayPacket

def test_replay_hash():
    h=ReviewContinuityReplayPacket.compute_hash('c','c',True,[])
    p=ReviewContinuityReplayPacket(replay_id='1',source_continuity_hash='c',replay_continuity_hash='c',deterministic_match=True,mismatch_reasons=[],deterministic_replay_hash=h,status='passed')
    assert p.deterministic_match
