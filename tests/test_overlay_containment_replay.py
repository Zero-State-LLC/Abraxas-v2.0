from core.overlay_containment.replay import OverlayContainmentReplayPacket


def test_replay_match() -> None:
    r = OverlayContainmentReplayPacket(replay_id="x", source_policy_hash="a", replay_policy_hash="a", deterministic_match=True, mismatched_components=[], status="passed")
    assert r.deterministic_match
