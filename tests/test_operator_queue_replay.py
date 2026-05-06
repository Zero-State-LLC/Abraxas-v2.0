from core.operator_queue.replay import OperatorQueueReplayPacket

def test_replay_packet():
    h = OperatorQueueReplayPacket.compute_hash("q","q",True,[])
    p = OperatorQueueReplayPacket(replay_id="1", source_queue_hash="q", replay_queue_hash="q", deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=h, status="passed")
    assert p.deterministic_match
