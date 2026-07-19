"""Tests for scripts/tools/run_scripts_ghost_path_inventory.py."""
from __future__ import annotations

from scripts.tools.run_scripts_ghost_path_inventory import (
    build_inventory,
    render_markdown,
)


def test_build_inventory_is_advisory_and_structured() -> None:
    packet = build_inventory()
    assert packet["schema_version"] == "ScriptsGhostPathInventory.v1"
    assert packet["advisory_only"] is True
    assert packet["authority_granted"] is False
    assert packet["policy"]["do_not_invent_runners"] is True
    assert "core_scripts_hits" in packet["summary"]
    assert "tests_hits" in packet["summary"]
    assert isinstance(packet["core_and_scripts_findings"], list)
    assert "inventory_hash" in packet
    # Hash is stable for same payload fields excluding itself
    again = build_inventory()
    assert again["summary"]["core_scripts_hits"] == packet["summary"]["core_scripts_hits"]


def test_render_markdown_lists_policy() -> None:
    packet = build_inventory()
    md = render_markdown(packet)
    assert "Do **not** invent stub runners" in md
    assert "MISSING_PLAN_ONLY" in md
    assert packet["inventory_id"] in md


def test_core_findings_have_expected_kinds_only() -> None:
    packet = build_inventory()
    allowed = {
        "RELOCATABLE",
        "MISSING_PLAN_ONLY",
        "TEST_FIXTURE_PLACEHOLDER",
    }
    for row in packet["core_and_scripts_findings"]:
        assert row["kind"] in allowed
        assert row["referenced_path"].startswith("scripts/")
        assert row["basename"].startswith("run_")
