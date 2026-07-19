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


def test_build_interface_registry_has_entries_and_first_supported() -> None:
    registry = build_interface_registry(REPO_ROOT, write=False)
    assert registry["schema_version"] == "InterfaceRegistry.v1"
    assert registry["evidence_state"] == "PARTIAL"
    assert registry["summary"]["entry_count"] >= 15
    assert registry["summary"]["supported_count"] == 3
    by_id = {e["contract_id"]: e for e in registry["entries"]}
    assert "run_fast_ci" in by_id
    assert "production_readiness_baseline" in by_id
    assert "neon_genie_entry" in by_id
    assert by_id["canonical_json"]["stability_class"] == "SUPPORTED"
    assert by_id["canonical_json"]["tests"] == ["tests/test_canonical_json.py"]
    assert by_id["run_fast_ci"]["stability_class"] == "SUPPORTED"
    assert by_id["run_fast_ci"]["tests"] == ["tests/test_run_fast_ci.py"]
    assert by_id["validation_service.v1"]["stability_class"] == "SUPPORTED"
    assert by_id["validation_service.v1"]["tests"] == ["tests/test_validation_service.py"]
    # all stabilization schemas should be present
    assert any("stabilization_entry_gate" in i for i in by_id)
    # COMPATIBILITY.md roots registered
    assert "contracts_pipelines_root" in by_id
    assert "contracts_yggdrasil_root" in by_id
    assert "cli_operator_layer" in by_id


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
