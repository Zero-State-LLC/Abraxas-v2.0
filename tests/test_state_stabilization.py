from core.state.stabilization import StateStabilizationPacket


def test_stabilization_valid():
    p = StateStabilizationPacket(stabilization_id="s", state_hash="h", replay_match_count=1, replay_failure_count=0, stabilization_window=3, stabilization_state="stable")
    assert p.stabilization_state == "stable"
