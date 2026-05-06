import pytest

from core.drift.stabilization import DriftStabilizationPacket


def test_unresolved_mismatches_block_stable() -> None:
    with pytest.raises(ValueError):
        DriftStabilizationPacket(stabilization_id="s", overlay_hash="o", replay_match_count=1, replay_failure_count=1, calibration_score=0.9, drift_confidence=0.9, stabilization_window=3, stabilization_state="stable")
