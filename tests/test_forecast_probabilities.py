import pytest

from core.forecast.probabilities import ForecastProbabilityPacket


def test_probability_range_enforced() -> None:
    with pytest.raises(ValueError):
        ForecastProbabilityPacket(probability_id="p", forecast_hash="f", probability=1.2, calibration_score=0.8, deterministic_probability_hash="x")
