"""Tests for Workstream 1 interface registry builder."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.production_readiness.interface_registry import build_interface_registry


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    REPO_ROOT
    / "contracts"
    / "stabilization_readiness"
    / "interface_registry.v1.schema.json"
)


def test_build_interface_registry_has_entries_and_no_supported() -> None:
    registry = build_interface_registry(REPO_ROOT, write=False)
    assert registry["schema_version"] == "InterfaceRegistry.v1"
    assert registry["evidence_state"] == "PARTIAL"
    assert registry["summary"]["entry_count"] >= 15
    assert registry["summary"]["supported_count"] == 0
    ids = {e["contract_id"] for e in registry["entries"]}
    assert "run_fast_ci" in ids
    assert "production_readiness_baseline" in ids
    assert "neon_genie_entry" in ids
    # all stabilization schemas should be present
    assert any("stabilization_entry_gate" in i for i in ids)


def test_registry_validates_against_schema() -> None:
    registry = build_interface_registry(REPO_ROOT, write=False)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=registry, schema=schema)


def test_stability_classes_are_allowed() -> None:
    registry = build_interface_registry(REPO_ROOT, write=False)
    allowed = {
        "SUPPORTED",
        "ADVISORY",
        "INTERNAL",
        "EXPERIMENTAL",
        "DEPRECATED",
        "REMOVED",
    }
    for entry in registry["entries"]:
        assert entry["stability_class"] in allowed
