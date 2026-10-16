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


# Access policy (auth, anonymous local dev, rate limit, body size): tests/test_api_access_policy.py


def test_unhandled_exception_sanitized_with_request_id() -> None:
    previous = get_settings()
    try:
        app = create_app(AppSettings(api_token="hardening-token"))
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
                headers={"X-Request-ID": "err-req-9", "X-ABX-Token": "hardening-token"},
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


@pytest.mark.parametrize("supplied", ["x" * 129, "bad id with spaces", "<script>alert(1)</script>"])
def test_unsafe_client_request_id_is_replaced(supplied: str) -> None:
    previous = get_settings()
    try:
        client = TestClient(create_app(AppSettings()))
        response = client.get("/ready", headers={"X-Request-ID": supplied})
        assert response.status_code == 200
        echoed = response.headers["X-Request-ID"]
        assert echoed != supplied
        assert len(echoed) == 16
    finally:
        configure_settings(previous)
