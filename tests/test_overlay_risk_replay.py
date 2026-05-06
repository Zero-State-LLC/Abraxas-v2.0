from core.overlay_risk.replay import OverlayRiskReplayPacket


def test_replay_packet() -> None:
    p = OverlayRiskReplayPacket(replay_id='1', source_risk_hash='a', replay_risk_hash='a', deterministic_match=True, mismatched_packets=[], status='passed')
    assert p.deterministic_match
