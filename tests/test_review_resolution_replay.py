from core.review_resolution.replay import ReviewResolutionReplayPacket

def test_replay_packet():
    h = ReviewResolutionReplayPacket.compute_hash('a','a',True,[])
    r = ReviewResolutionReplayPacket(replay_id='1', source_resolution_hash='a', replay_resolution_hash='a', deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=h, status='passed')
    assert r.deterministic_match
