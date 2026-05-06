import pytest

from core.forecast.stabilization import ForecastStabilizationPacket


def test_unresolved_bindings_block_promotion() -> None:
    with pytest.raises(ValueError):
        ForecastStabilizationPacket(stabilization_id="s", forecast_hash="f", replay_match_count=1, replay_failure_count=0, calibration_score=0.8, unresolved_bindings=1, stabilization_window=3, stabilization_state="stable")
