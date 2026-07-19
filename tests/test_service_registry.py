"""Tests for WP-C service registry seed."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.service_registry import build_service_registry


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_service_registry_seed() -> None:
    reg = build_service_registry(REPO_ROOT, write=False)
    assert reg["schema_version"] == "ServiceRegistry.v1"
    assert reg["summary"]["implemented"] == 2
    ids = {s["service_id"] for s in reg["services"]}
    assert "validation_service" in ids
    assert "artifact_and_provenance_service" in ids
    assert "forecast_service" in ids
    validation = next(s for s in reg["services"] if s["service_id"] == "validation_service")
    assert validation["stability_class"] == "SUPPORTED"
    assert validation["version"] == "1.0.0"
    artifact = next(
        s for s in reg["services"] if s["service_id"] == "artifact_and_provenance_service"
    )
    assert artifact["status"] == "IMPLEMENTED"
    assert artifact["version"] == "0.1.0"

