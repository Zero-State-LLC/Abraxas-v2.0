"""Tests for WP-RUNBOOK supported surface operator runbook."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.supported_surface_operator_runbook import (
    build_supported_surface_operator_runbook,
)


REPO = Path(__file__).resolve().parents[1]


def test_runbook_has_core_surfaces() -> None:
    runbook = build_supported_surface_operator_runbook(REPO, write=False)
    assert runbook["schema_version"] == "supported_surface_operator_runbook.v1"
    surfaces = {p["surface"] for p in runbook["procedures"]}
    assert "canonical_json" in surfaces
    assert "run_fast_ci" in surfaces
    assert "validation_service.v1" in surfaces
    assert "artifact_and_provenance_service.v0" in surfaces
