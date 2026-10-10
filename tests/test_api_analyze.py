"""Tests for create_app factory and /analyze endpoints."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from apps.api.settings import AppSettings

    _HAS = True
except ImportError:
    _HAS = False

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not _HAS, reason="httpx/TestClient not available")
def test_create_app_ready_and_version() -> None:
    app = create_app(AppSettings(app_version="2.5.0-test"))
    client = TestClient(app)
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["candidate_status"] == "NOT_READY"
    version = client.get("/version")
    assert version.status_code == 200
    body = version.json()
    assert body["role"] == "doctrine-reference"
    assert body["reference_build"] == "2.5.0-test"
    assert body["product_version"] is None
    assert body["canonical_product_repository"] == "Zero-State-LLC/Abraxas"


@pytest.mark.skipif(not _HAS, reason="httpx/TestClient not available")
def test_analyze_endpoint_with_alembic_task() -> None:
    app = create_app(AppSettings())
    client = TestClient(app)
    task = json.loads(
        (REPO / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    response = client.post(
        "/analyze",
        json={
            "run_id": "api-analyze-001",
            "input_payload": {"goal": task["goal"]},
            "alembic_task": task,
            "enable_alembic": True,
            "activation_lane": "LOCAL_DEV",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["advisory_result"]["lane"] == "SHADOW"
    assert data["alembic"]["routing_decision"]["decision_id"]


@pytest.mark.skipif(not _HAS, reason="httpx/TestClient not available")
def test_analyze_rejects_external_production() -> None:
    app = create_app(AppSettings())
    client = TestClient(app)
    response = client.post(
        "/analyze",
        json={
            "run_id": "api-ext",
            "enable_alembic": False,
            "activation_lane": "EXTERNAL_PRODUCTION",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATOR_GATE"
