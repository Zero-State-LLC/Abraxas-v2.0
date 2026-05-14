"""Tests for ABRAXAS_API_PUBLIC_READONLY guard on /registry, /validation, /projection."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_health_public_without_flag(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ABRAXAS_API_PUBLIC_READONLY", raising=False)
    response = client.get("/health")
    assert response.status_code == 200


def test_registry_blocked_when_flag_absent(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ABRAXAS_API_PUBLIC_READONLY", raising=False)
    response = client.get("/registry")
    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"


def test_registry_blocked_when_flag_false(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "false")
    response = client.get("/registry")
    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"


def test_registry_allowed_when_flag_true(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")
    response = client.get("/registry")
    assert response.status_code == 200




def test_registry_blocked_when_flag_malformed(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "maybe")
    response = client.get("/registry")
    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"

def test_validation_blocked_when_flag_absent(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ABRAXAS_API_PUBLIC_READONLY", raising=False)
    response = client.get("/validation")
    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"


def test_validation_blocked_when_flag_false(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "false")
    response = client.get("/validation")
    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"


def test_validation_allowed_when_flag_true(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")
    response = client.get("/validation")
    assert response.status_code == 200


def test_projection_blocked_when_flag_absent(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ABRAXAS_API_PUBLIC_READONLY", raising=False)
    response = client.get("/projection")
    assert response.status_code == 403
    assert response.json()["detail"] == "api_public_readonly_disabled"


def test_projection_allowed_when_flag_true(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")
    response = client.get("/projection")
    assert response.status_code == 200
