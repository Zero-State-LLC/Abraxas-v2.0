"""Tests for API error sanitization — exception text must not leak to clients."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_registry_500_returns_generic_detail(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Internal exception message must not appear in the HTTP response body."""
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")

    sensitive_text = "secret internal path /etc/abraxas/private.key traceback"

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError(sensitive_text)

    # Ensure file path doesn't exist so the on-the-fly branch is hit
    with (
        patch("apps.api.routers.registry._REGISTRY_PATH") as mock_path,
        patch("apps.api.routers.registry.asyncio.to_thread", new=_boom),
    ):
        mock_path.exists.return_value = False
        # Also patch the on-the-fly builder to raise with sensitive text
        with patch(
            "core.pipelines.registry.load_contracts",
            side_effect=RuntimeError(sensitive_text),
        ):
            response = client.get("/registry")

    assert response.status_code == 500
    body = response.text
    assert sensitive_text not in body
    assert "/etc" not in body
    assert "traceback" not in body.lower() or "Traceback" not in body
    assert response.json()["detail"] == "registry_unavailable"


def test_registry_500_detail_is_stable(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stable generic detail string is always returned, regardless of exception type."""
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")

    with (
        patch("apps.api.routers.registry._REGISTRY_PATH") as mock_path,
        patch(
            "core.pipelines.registry.load_contracts",
            side_effect=ValueError("some internal value error"),
        ),
    ):
        mock_path.exists.return_value = False
        response = client.get("/registry")

    assert response.status_code == 500
    assert response.json()["detail"] == "registry_unavailable"
    assert "some internal value error" not in response.text


def test_registry_500_no_file_path_in_response(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """File paths must not leak into client responses."""
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "true")

    with (
        patch("apps.api.routers.registry._REGISTRY_PATH") as mock_path,
        patch(
            "core.pipelines.registry.load_contracts",
            side_effect=FileNotFoundError("contracts/pipelines/secret.json"),
        ),
    ):
        mock_path.exists.return_value = False
        response = client.get("/registry")

    assert response.status_code == 500
    assert "contracts/pipelines" not in response.text
    assert "secret.json" not in response.text
    assert response.json()["detail"] == "registry_unavailable"
