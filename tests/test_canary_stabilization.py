import pytest
from core.canary.stabilization import CanaryStabilizationPacket


def test_replay_failure_blocks_stable() -> None:
    with pytest.raises(ValueError):
        CanaryStabilizationPacket(stabilization_id="s", overlay_hash="o", replay_match_count=0, replay_failure_count=1, calibration_score=0.8, rollback_readiness=True, stabilization_window=2, stabilization_state="stable", status="failed")
