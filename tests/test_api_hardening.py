"""Tests for PATCH-P1-API-STATE-HARDENING-001: API hardening."""

from __future__ import annotations

import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Phase 2 – Exception leakage
# ---------------------------------------------------------------------------


def test_registry_internal_exception_not_leaked(tmp_path):
    """Internal exception strings must not appear in registry error response."""
    secret_detail = "super_secret_internal_path_xyz"
    with patch("apps.api.routers.registry._REGISTRY_PATH") as mock_path:
        mock_path.exists.return_value = False
        with patch("core.pipelines.registry.build_registry", side_effect=RuntimeError(secret_detail)):
            os.environ["ABRAXAS_API_PUBLIC_READONLY"] = "true"
            try:
                response = client.get("/registry")
                assert response.status_code == 500
                body = response.text
                assert secret_detail not in body
                assert response.json()["detail"] == "registry_unavailable"
            finally:
                del os.environ["ABRAXAS_API_PUBLIC_READONLY"]


def test_registry_error_returns_stable_code(tmp_path):
    """Registry error returns stable 'registry_unavailable' detail."""
    with patch("apps.api.routers.registry._REGISTRY_PATH") as mock_path:
        mock_path.exists.return_value = False
        with patch("core.pipelines.registry.build_registry", side_effect=Exception("boom")):
            os.environ["ABRAXAS_API_PUBLIC_READONLY"] = "true"
            try:
                response = client.get("/registry")
                assert response.status_code == 500
                assert response.json()["detail"] == "registry_unavailable"
            finally:
                del os.environ["ABRAXAS_API_PUBLIC_READONLY"]


# ---------------------------------------------------------------------------
# Phase 3 – Auth posture (public-readonly guard)
# ---------------------------------------------------------------------------


def test_health_always_accessible_without_flag():
    """Health endpoint is public and never blocked."""
    env = {k: v for k, v in os.environ.items() if k != "ABRAXAS_API_PUBLIC_READONLY"}
    with patch.dict(os.environ, env, clear=True):
        response = client.get("/health")
        assert response.status_code == 200


def test_registry_blocked_when_public_readonly_disabled():
    """Registry returns 403 when ABRAXAS_API_PUBLIC_READONLY is not set."""
    env = {k: v for k, v in os.environ.items() if k != "ABRAXAS_API_PUBLIC_READONLY"}
    with patch.dict(os.environ, env, clear=True):
        response = client.get("/registry")
        assert response.status_code == 403
        assert response.json()["detail"] == "api_public_readonly_disabled"


def test_registry_blocked_when_public_readonly_false():
    """Registry returns 403 when ABRAXAS_API_PUBLIC_READONLY=false."""
    with patch.dict(os.environ, {"ABRAXAS_API_PUBLIC_READONLY": "false"}):
        response = client.get("/registry")
        assert response.status_code == 403
        assert response.json()["detail"] == "api_public_readonly_disabled"


def test_validation_blocked_when_public_readonly_disabled():
    """Validation returns 403 when ABRAXAS_API_PUBLIC_READONLY is not set."""
    env = {k: v for k, v in os.environ.items() if k != "ABRAXAS_API_PUBLIC_READONLY"}
    with patch.dict(os.environ, env, clear=True):
        response = client.get("/validation")
        assert response.status_code == 403
        assert response.json()["detail"] == "api_public_readonly_disabled"


def test_projection_blocked_when_public_readonly_disabled():
    """Projection returns 403 when ABRAXAS_API_PUBLIC_READONLY is not set."""
    env = {k: v for k, v in os.environ.items() if k != "ABRAXAS_API_PUBLIC_READONLY"}
    with patch.dict(os.environ, env, clear=True):
        response = client.get("/projection")
        assert response.status_code == 403


def test_registry_allowed_when_public_readonly_enabled(tmp_path):
    """Registry accessible when ABRAXAS_API_PUBLIC_READONLY=true."""
    with patch.dict(os.environ, {"ABRAXAS_API_PUBLIC_READONLY": "true"}):
        response = client.get("/registry")
        # May be 200 or 500 depending on environment, but NOT 403
        assert response.status_code != 403


def test_validation_allowed_when_public_readonly_enabled():
    """Validation accessible when ABRAXAS_API_PUBLIC_READONLY=true."""
    with patch.dict(os.environ, {"ABRAXAS_API_PUBLIC_READONLY": "true"}):
        response = client.get("/validation")
        assert response.status_code != 403
