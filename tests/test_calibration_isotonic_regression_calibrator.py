"""Tests for core/calibration/isotonic_regression_calibrator.py (candidate ff0a4e3d4bd1c1d3)"""

import pytest
from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator

def test_fit_basic():
    cal = IsotonicRegressionCalibrator()
    scores = [0.1, 0.4, 0.7]
    targets = [0.0, 0.5, 1.0]
    result = cal.fit(scores, targets)
    assert result["status"] == "fitted"
    assert result["n_samples"] == 3

def test_predict_monotonic_and_fitted():
    cal = IsotonicRegressionCalibrator()
    scores = [0.1, 0.3, 0.8]
    targets = [0.0, 0.4, 0.9]
    cal.fit(scores, targets)
    preds = cal.predict([0.05, 0.2, 0.5, 0.9])
    assert len(preds) == 4
    # Should be non-decreasing
    for i in range(1, len(preds)):
        assert preds[i] >= preds[i-1] - 1e-9

def test_predict_without_fit_returns_raw():
    cal = IsotonicRegressionCalibrator()
    raw = [0.2, 0.5]
    assert cal.predict(raw) == raw

def test_fit_mismatched_length_raises():
    cal = IsotonicRegressionCalibrator()
    with pytest.raises(ValueError):
        cal.fit([0.1, 0.2], [0.0])
