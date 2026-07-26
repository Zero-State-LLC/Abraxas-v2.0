"""Phase 6 service hardening: request-id, headers, auth/rate boundaries, OpenAPI."""

from __future__ import annotations

from unittest.mock import patch

import pytest

try:
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from apps.api.settings import AppSettings, configure_settings, get_settings

    _HAS = True
except ImportError:
    _HAS = False


pytestmark = pytest.mark.skipif(not _HAS, reason="httpx/TestClient not available")


def test_ready_includes_security_headers_and_request_id() -> None:
    previous = get_settings()
    try:
        app = create_app(AppSettings())
        client = TestClient(app)
        response = client.get("/ready", headers={"X-Request-ID": "probe-req-001"})
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == "probe-req-001"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert response.headers["Cache-Control"] == "no-store"
    finally:
        configure_settings(previous)


def test_auth_boundary_fail_closed_when_enabled() -> None:
    previous = get_settings()
    try:
        app = create_app(AppSettings(require_auth=True))
        client = TestClient(app)
        # Readiness stays open; auth boundary is scoped to POST /analyze.
        assert client.get("/ready").status_code == 200
        denied = client.post("/analyze", json={"run_id": "x", "enable_alembic": False})
        assert denied.status_code == 401
        assert denied.json()["detail"] == "authentication_required"
        stub = client.post(
            "/analyze",
            json={"run_id": "x", "enable_alembic": False},
            headers={"Authorization": "Bearer unused"},
        )
        assert stub.status_code == 501
        assert stub.json()["detail"] == "authenticator_not_configured"
    finally:
        configure_settings(previous)


def test_rate_limit_boundary_fail_closed_when_enabled() -> None:
    previous = get_settings()
    try:
        app = create_app(AppSettings(require_rate_limit=True))
        client = TestClient(app)
        denied = client.post("/analyze", json={"run_id": "x", "enable_alembic": False})
        assert denied.status_code == 501
        assert denied.json()["detail"] == "rate_limiter_not_configured"
    finally:
        configure_settings(previous)


def test_unhandled_exception_sanitized_with_request_id() -> None:
    previous = get_settings()
    try:
        app = create_app(AppSettings())
        client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "apps.api.routers.analyze.run_advisory_spine",
            side_effect=RuntimeError("secret path /etc/abraxas/key"),
        ):
            response = client.post(
                "/analyze",
                json={
                    "run_id": "boom",
                    "enable_alembic": False,
                    "activation_lane": "LOCAL_DEV",
                },
                headers={"X-Request-ID": "err-req-9"},
            )
        assert response.status_code == 500
        body = response.json()
        assert body["detail"] == "internal_error"
        assert body["request_id"] == "err-req-9"
        assert "secret" not in response.text
        assert "/etc" not in response.text
    finally:
        configure_settings(previous)


def test_openapi_contains_supported_routes() -> None:
    previous = get_settings()
    try:
        app = create_app(AppSettings())
        client = TestClient(app)
        spec = client.get("/openapi.json").json()
        paths = spec["paths"]
        assert "/ready" in paths
        assert "/version" in paths
        assert "/analyze" in paths
        assert paths["/analyze"].get("post") is not None
    finally:
        configure_settings(previous)
