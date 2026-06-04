from core.observability.metrics import MetricPoint, build_metric_series


def test_metric_series_deterministic() -> None:
    pts = [MetricPoint(timestamp_index=0, metric_name="m", metric_value=1.0)]
    s1 = build_metric_series("f", pts)
    s2 = build_metric_series("f", pts)
    assert s1.series_id == s2.series_id
