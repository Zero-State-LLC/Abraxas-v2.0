import pytest

from core.brier.replay import BrierReplayPacket


def test_replay_mismatch_invalidates_stabilization() -> None:
    with pytest.raises(ValueError):
        BrierReplayPacket(replay_id="r", ledger_hash="l", deterministic_match=True, replayed_scores=[], mismatched_scores=["m"])
