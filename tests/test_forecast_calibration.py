import pytest

from core.forecast.calibration import ForecastCalibrationPacket


def test_calibration_threshold_range() -> None:
    with pytest.raises(ValueError):
        ForecastCalibrationPacket(calibration_id="c", forecast_hash="f", calibration_method="replay_consistency", calibration_score=1.5, deterministic_calibration_hash="x")
