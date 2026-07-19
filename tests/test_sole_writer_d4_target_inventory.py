"""Tests for WP-D4-prep sole-writer target inventory."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.sole_writer_d4_target_inventory import (
    build_sole_writer_d4_target_inventory,
)


REPO = Path(__file__).resolve().parents[1]


def test_d4_inventory_no_implementation() -> None:
    inv = build_sole_writer_d4_target_inventory(REPO, write=False)
    assert inv["schema_version"] == "sole_writer_d4_target_inventory.v1"
    assert inv["implementation_executed"] is False
    assert inv["fail_closed_recommended"] is False
    assert len(inv["clusters"]) >= 3
