import pytest

from core.sandbox.stabilization import SandboxStabilizationPacket


def test_replay_mismatch_invalidates_stable() -> None:
    with pytest.raises(ValueError):
        SandboxStabilizationPacket(stabilization_id="s", branch_hash="b", replay_match_count=0, replay_failure_count=1, stabilization_window=3, convergence_score=0.2, stabilization_state="stable")
