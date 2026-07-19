"""Tests for WP-E boundary fail-closed design receipt."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.boundary_fail_closed_design import (
    build_boundary_fail_closed_design,
)


def test_design_default_off() -> None:
    doc = build_boundary_fail_closed_design(Path(__file__).resolve().parents[1], write=False)
    assert doc["decision"] == "DESIGN_ONLY_DEFAULT_OFF"
    assert doc["mechanism"]["default"] is False
    assert doc["mechanism"]["env_var"] == "ABRAXAS_BOUNDARY_FAIL_CLOSED"
