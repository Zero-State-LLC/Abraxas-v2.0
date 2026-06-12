from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import app


def test_metric_dashboard_route_blocked_without_public_readonly_flag(monkeypatch) -> None:
    monkeypatch.delenv("ABRAXAS_API_PUBLIC_READONLY", raising=False)
    client = TestClient(app)

    response = client.get("/api/abx/metrics/dashboard")

    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"


def test_metric_dashboard_route_returns_readonly_frame(monkeypatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")
    client = TestClient(app)

    response = client.get("/api/abx/metrics/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["packet_type"] == "ABXMetricDashboardFrame.v1"
    assert data["authority"] == "SHADOW_ONLY_TRACE"
    assert data["output_effect"] == "VISUAL_ANNOTATION_ONLY"
    assert data["prediction_frame"]["packet_type"] == "ABXMetricPredictionFrame.v1"
    assert data["prediction_frame"]["authority"] == "FORECAST_ANNOTATION_ONLY"
    assert data["runtime_locks"]["execution_authority"] is False
    assert data["runtime_locks"]["forecast_weight_allowed"] is False
    assert data["compliance"]["filter_calls_detected"] is False
