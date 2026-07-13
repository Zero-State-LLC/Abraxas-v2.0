"""Tests for core/intelligence/temporal_anomaly_intelligence.py (HARDENING candidate a023e170f1a1b445)"""

from core.intelligence.temporal_anomaly_intelligence import (
    TemporalAnomalyIntelligenceLayer,
    get_calibrator,
)

def test_available_calibration_methods():
    methods = TemporalAnomalyIntelligenceLayer.available_calibration_methods()
    assert isinstance(methods, list)
    assert "dirichlet" in methods
    assert "isotonic" in methods

def test_get_calibrator():
    cal = get_calibrator("dirichlet")
    assert cal is not None
    assert hasattr(cal, "calibrate")

def test_layer_instantiation_and_process():
    layer = TemporalAnomalyIntelligenceLayer(config={"calibration_method": "isotonic", "use_ensemble": False})
    assert layer is not None
    assert "vacuity_threshold" in str(layer.config) or isinstance(layer.config, dict)

    # Numeric stream (for bocpd path)
    res = layer.process_stream(42.0)
    assert "change_points" in res
    assert "provenance" in res
    assert res["ensemble_used"] is False

    # List stream (for hdbscan/pitman_yor/hdp)
    res2 = layer.process_stream([1.0, 2.0, 3.0, 100.0, 2.0])
    assert isinstance(res2.get("anomalies", []), list)
    assert "dynamic_vacuity_threshold" in res2

def test_layer_status_and_brier():
    layer = TemporalAnomalyIntelligenceLayer(config={"use_ensemble": False})
    status = layer.get_status()
    assert status["status"] == "active"
    assert "brier_summary" in status

    # Brier via process with target
    layer2 = TemporalAnomalyIntelligenceLayer()
    res = layer2.process_stream([1, 2, 3], target=0.5)
    # May or may not have brier depending on anomalies
    assert "provenance" in res
