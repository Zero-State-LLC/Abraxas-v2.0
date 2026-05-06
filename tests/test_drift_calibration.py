from core.drift.calibration import DriftCalibrationPacket


def test_calibration_deterministic() -> None:
    h = DriftCalibrationPacket.compute_hash("o", 1.0, 0.9, 0.9, 0.93)
    assert h == DriftCalibrationPacket.compute_hash("o", 1.0, 0.9, 0.9, 0.93)
