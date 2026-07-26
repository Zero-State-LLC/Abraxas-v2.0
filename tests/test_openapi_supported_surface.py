"""OpenAPI supported-surface freeze (Phase 7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.production_convergence.openapi_freeze import (
    extract_route_surface,
    freeze_violations,
)

REPO = Path(__file__).resolve().parents[1]
FREEZE_PATH = REPO / "contracts/api/openapi_supported_surface.v1.json"

try:
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from apps.api.settings import AppSettings, configure_settings, get_settings

    _HAS = True
except ImportError:
    _HAS = False


pytestmark = pytest.mark.skipif(not _HAS, reason="httpx/TestClient not available")


def test_openapi_supported_surface_not_shrunk() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    previous = get_settings()
    try:
        app = create_app(AppSettings())
        client = TestClient(app)
        live = extract_route_surface(client.get("/openapi.json").json())
        violations = freeze_violations(
            live_surface=live,
            frozen_surface=freeze["routes"],
        )
        assert violations == [], violations
    finally:
        configure_settings(previous)


def test_freeze_violations_detect_missing_method() -> None:
    violations = freeze_violations(
        live_surface=[{"path": "/analyze", "methods": ["GET"]}],
        frozen_surface=[{"path": "/analyze", "methods": ["POST"]}],
    )
    assert violations == ["missing_methods:/analyze:POST"]
