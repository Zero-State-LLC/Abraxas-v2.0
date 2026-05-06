from core.drift.calibration import DriftCalibrationPacket
from core.drift.replay import DriftReplayPacket
from core.drift.validators import validate_weight_drift


def test_validator_catches_production_mutation_attempts() -> None:
    replay = DriftReplayPacket(replay_id="r", overlay_hash="o", deterministic_match=True, replayed_overlays=[], mismatched_overlays=[])
    cal = DriftCalibrationPacket(calibration_id="c", overlay_hash="o", replay_consistency=1.0, reliability_consistency=0.9, stabilization_consistency=0.9, calibration_score=0.93, deterministic_calibration_hash=DriftCalibrationPacket.compute_hash("o", 1.0, 0.9, 0.9, 0.93))
    result = validate_weight_drift({"overlay_weight": 0.5, "pending_actions": ["production_mutation"]}, replay, cal)
    assert result["status"] == "repair_required"
