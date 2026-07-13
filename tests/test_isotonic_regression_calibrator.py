"""Tests for core/calibration/isotonic_regression_calibrator.py (HARDENING candidate ff0a4e3d4bd1c1d3)"""

import pytest
from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator

def test_init():
    cal = IsotonicRegressionCalibrator()
    assert not cal._fitted
    assert cal.provenance["method"] == "isotonic_regression"

def test_fit_basic():
    cal = IsotonicRegressionCalibrator()
    scores = [0.1, 0.5, 0.9]
    targets = [0.0, 0.5, 1.0]
    result = cal.fit(scores, targets)
    assert result["status"] == "fitted"
    assert result["n_samples"] == 3
    assert cal._fitted

def test_predict_after_fit():
    cal = IsotonicRegressionCalibrator()
    cal.fit([0.0, 0.5, 1.0], [0.0, 0.5, 1.0])
    out = cal.predict([0.25, 0.75])
    assert len(out) == 2
    assert all(isinstance(x, float) for x in out)

def test_fit_mismatched_lengths():
    cal = IsotonicRegressionCalibrator()
    with pytest.raises(ValueError):
        cal.fit([0.1, 0.2], [0.0])

def test_predict_unfitted_returns_input():
    cal = IsotonicRegressionCalibrator()
    scores = [0.3, 0.7]
    assert cal.predict(scores) == scores
