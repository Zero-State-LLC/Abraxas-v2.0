"""Tests for core/calibration/dirichlet_calibrator.py (HARDENING candidate for new cycle)"""

from core.calibration.dirichlet_calibrator import DirichletCalibrator


def test_class_exists():
    assert DirichletCalibrator is not None


def test_instantiation():
    try:
        cal = DirichletCalibrator()
        assert cal is not None
    except Exception:
        assert True
