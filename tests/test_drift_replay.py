import pytest

from core.drift.replay import DriftReplayPacket


def test_replay_mismatch_invalidates_stabilization() -> None:
    with pytest.raises(ValueError):
        DriftReplayPacket(replay_id="r", overlay_hash="o", deterministic_match=True, replayed_overlays=[], mismatched_overlays=["m"])
