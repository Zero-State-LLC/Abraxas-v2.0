import pytest
from core.state.replay import StateReplayPacket


def test_replay_mismatch_invalidates_state():
    with pytest.raises(ValueError):
        StateReplayPacket(replay_id="r", source_state_hash="a", replayed_state_hash="b", deterministic_match=True, mismatched_transitions=["x"])
