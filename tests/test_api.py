"""Tests for FastAPI endpoints."""

from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient

    from apps.api.main import app

    _HAS_TEST_CLIENT = True
except ImportError:
    _HAS_TEST_CLIENT = False


@pytest.mark.skipif(not _HAS_TEST_CLIENT, reason="httpx/TestClient not available")
def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["system"] == "abraxas-v2"


@pytest.mark.skipif(not _HAS_TEST_CLIENT, reason="httpx/TestClient not available")
def test_registry_endpoint_returns_registry(monkeypatch):
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")
    client = TestClient(app)
    response = client.get("/registry")
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == "GlobalPipelineRegistry.v1"
    assert data["pipeline_count"] == 7
