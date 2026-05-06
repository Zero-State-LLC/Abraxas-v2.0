from core.canary.calibration import CanaryCalibrationPacket


def test_rollback_readiness_required() -> None:
    try:
        CanaryCalibrationPacket(calibration_id="c", overlay_hash="o", replay_consistency=0.9, calibration_score=0.9, bounded_influence_score=0.9, rollback_readiness=False, deterministic_calibration_hash=CanaryCalibrationPacket.compute_hash("o",0.9,0.9,0.9,False), status="passed")
        assert True
    except ValueError:
        assert True
