from core.geometric_intelligence_runtime import compute_shadow_metrics


def test_compute_shadow_metrics() -> None:
    result = compute_shadow_metrics({"item_id": "signal-1"})
    assert result["signal_id"] == "signal-1"
    assert result["status"] == "SHADOW_METRICS_COMPUTED"
