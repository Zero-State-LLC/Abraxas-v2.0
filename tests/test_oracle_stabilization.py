import pytest

from core.oracle.stabilization import IntakeStabilizationPacket


def test_conflicts_block_stable_state() -> None:
    with pytest.raises(ValueError):
        IntakeStabilizationPacket(stabilization_id="s", intake_hash="h", replay_match_count=1, replay_failure_count=0, conflict_count=1, stabilization_window=3, stabilization_state="stable")
