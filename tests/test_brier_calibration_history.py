from core.brier.calibration_history import CalibrationHistoryPacket


def test_calibration_history_average() -> None:
    assert CalibrationHistoryPacket.compute_average([0.5, 0.7]) == 0.6
