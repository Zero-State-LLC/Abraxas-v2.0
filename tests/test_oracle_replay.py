import pytest

from core.oracle.replay import IntakeReplayPacket


def test_replay_mismatch_invalidates_stabilization() -> None:
    with pytest.raises(ValueError):
        IntakeReplayPacket(replay_id="r", source_intake_hash="a", replay_intake_hash="b", deterministic_match=True, mismatched_normalizations=["m"])
