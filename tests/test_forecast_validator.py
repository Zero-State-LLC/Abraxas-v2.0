from core.forecast.calibration import ForecastCalibrationPacket
from core.forecast.replay import ForecastReplayPacket
from core.forecast.validators import validate_forecast_candidate


def test_validator_catches_autonomous_promotion_attempt() -> None:
    replay = ForecastReplayPacket(replay_id="r", forecast_hash="f", deterministic_match=True, replayed_probabilities=[], mismatched_probabilities=[])
    cal = ForecastCalibrationPacket(calibration_id="c", forecast_hash="f", calibration_method="replay_consistency", calibration_score=0.8, deterministic_calibration_hash=ForecastCalibrationPacket.compute_hash("f", "replay_consistency", 0.8))
    result = validate_forecast_candidate({"unresolved_bindings": 0, "pending_actions": ["autonomous_promotion"]}, replay, cal)
    assert result["status"] == "repair_required"
