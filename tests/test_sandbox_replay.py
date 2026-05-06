import pytest

from core.sandbox.replay import SandboxReplayPacket


def test_replay_mismatch_invalid_state() -> None:
    with pytest.raises(ValueError):
        SandboxReplayPacket(replay_id="r", branch_hash="b", deterministic_match=True, replayed_mutations=[], mismatched_mutations=["x"])
