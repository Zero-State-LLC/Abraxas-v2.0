"""Tests for core/calibration/beta_calibrator.py (HARDENING candidate c134c1f43dcff4e3)"""

from core.calibration.beta_calibrator import BetaCalibrator

def test_fit_and_predict():
    cal = BetaCalibrator()
    scores = [0.1, 0.5, 0.9]
    targets = [0.0, 0.5, 1.0]
    res = cal.fit(scores, targets)
    assert res["status"] == "fitted"
    assert cal._fitted is True
    preds = cal.predict([0.2, 0.8])
    assert len(preds) == 2
    assert all(0 <= p <= 1 for p in preds)

def test_calibrate():
    cal = BetaCalibrator()
    scores = [0.3, 0.7]
    targets = [0.2, 0.8]
    cal.fit(scores, targets)
    out = cal.calibrate([0.4])
    assert "calibrated_scores" in out
    assert len(out["calibrated_scores"]) == 1

def test_unfitted_predict_returns_input():
    cal = BetaCalibrator()
    scores = [0.1, 0.5]
    assert cal.predict(scores) == scores

def test_get_status():
    cal = BetaCalibrator()
    status = cal.get_status()
    assert "fitted" in status
    assert "alpha" in status
    assert "beta" in status
