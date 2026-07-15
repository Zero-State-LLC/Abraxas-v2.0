"""Tests for production slice 1 surface resolution packet 001."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.canonical.json import canonical_hash
from core.surface_resolution.discovery import (
    SLICE_CLASSIFICATION,
    SLICE_ENTRYPOINT,
    build_packet_payloads,
    run_surface_resolution_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = REPO_ROOT / "contracts/stabilization_readiness"
BASELINE = "0fd77b95ae3dd4b0ba86c378727160282a4ff692"

ARTIFACT_SCHEMAS = {
    "production_slice_candidate.latest.json": "production_slice_candidate.v1.schema.json",
    "production_reachability_graph.latest.json": "production_reachability_graph.v1.schema.json",
    "contract_boundary_candidates.latest.json": "contract_boundary_candidates.v1.schema.json",
    "cross_language_boundaries.latest.json": "cross_language_boundaries.v1.schema.json",
    "existing_inventory_reconciliation.latest.json": "existing_inventory_reconciliation.v1.schema.json",
    "unresolved_surface_questions.latest.json": "unresolved_surface_questions.v1.schema.json",
    "surface_resolution_receipt.latest.json": "surface_resolution_receipt.v1.schema.json",
}


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))


def _assert_no_absolute_paths(payload: object) -> None:
    if isinstance(payload, str):
        assert not payload.startswith("/Users/")
        assert not payload.startswith("/home/")
    elif isinstance(payload, dict):
        for value in payload.values():
            _assert_no_absolute_paths(value)
    elif isinstance(payload, list):
        for item in payload:
            _assert_no_absolute_paths(item)


def test_deterministic_discovery_ordering(tmp_path: Path) -> None:
    first = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    second = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    for name in ARTIFACT_SCHEMAS:
        assert canonical_hash(first[name]) == canonical_hash(second[name])


def test_python_pydantic_model_discovery() -> None:
    payloads = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    contracts = payloads["contract_boundary_candidates.latest.json"]
    pydantic = [c for c in contracts["candidates"] if c["language"] == "python" and "pydantic" in c["contract_id"]]
    assert pydantic
    assert any("PipelineContractV11" in c["symbol"] for c in pydantic)


def test_python_runtime_validator_discovery() -> None:
    payloads = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    contracts = payloads["contract_boundary_candidates.latest.json"]
    validators = [c for c in contracts["candidates"] if c["boundary_class"] == "RUNTIME_VALIDATOR"]
    assert validators
    assert any("pipelines" in c["surface"] for c in validators)


def test_typescript_boundary_declaration_discovery() -> None:
    payloads = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    contracts = payloads["contract_boundary_candidates.latest.json"]
    ts = [c for c in contracts["candidates"] if c["language"] == "typescript"]
    assert ts
    assert any(c["validation_mode"] == "STATIC_TYPE_ONLY" for c in ts)


def test_static_vs_runtime_validation_distinction() -> None:
    payloads = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    modes = payloads["contract_boundary_candidates.latest.json"]["validation_mode_counts"]
    assert modes.get("STATIC_TYPE_ONLY",0) >= 1
    assert sum(modes.get(k,0) for k in ("CONTRACT_DECLARATION","VALIDATOR_DECLARATION","VALIDATOR_INVOKED_AT_BOUNDARY")) >= 1


def test_cross_language_artifact_coupling() -> None:
    payloads = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    boundaries = payloads["cross_language_boundaries.latest.json"]["boundaries"]
    assert any(b["coupling_kind"] == "static_artifact_file" for b in boundaries)


def test_test_only_surfaces_excluded_from_slice() -> None:
    graph = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)[
        "production_reachability_graph.latest.json"
    ]
    test_surfaces = [s for s in graph["surfaces"] if s["repository_path"].startswith("tests/")]
    assert not test_surfaces


def test_unresolved_production_reachability_present() -> None:
    unresolved = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)[
        "unresolved_surface_questions.latest.json"
    ]
    assert unresolved["question_count"] >= 1


def test_zero_contract_inventory_root_cause_classification() -> None:
    reconciliation = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)[
        "existing_inventory_reconciliation.latest.json"
    ]
    assert "INVENTORY_SEMANTICS_DIFFER_FROM_STABILIZATION_GATE" in reconciliation["root_causes"]
    assert reconciliation["artifact_contract_inventory_has_contracts_key"] is False


def test_production_slice_candidate_classification() -> None:
    candidate = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)[
        "production_slice_candidate.latest.json"
    ]
    assert candidate["classification"] == SLICE_CLASSIFICATION
    assert candidate["entrypoint"] == SLICE_ENTRYPOINT


def test_canonical_serialization_and_schema_validation(tmp_path: Path) -> None:
    payloads = run_surface_resolution_packet(
        REPO_ROOT, baseline_commit=BASELINE, output_root=tmp_path / "packet"
    )
    for artifact_name, schema_name in ARTIFACT_SCHEMAS.items():
        payload = payloads[artifact_name]
        jsonschema.validate(payload, _load_schema(schema_name))
        _assert_no_absolute_paths(payload)
        on_disk = json.loads((tmp_path / "packet" / artifact_name).read_text(encoding="utf-8"))
        assert canonical_hash(on_disk) == canonical_hash(payload)


def test_two_run_hash_equality(tmp_path: Path) -> None:
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    first = run_surface_resolution_packet(REPO_ROOT, baseline_commit=BASELINE, output_root=out_a)
    second = run_surface_resolution_packet(REPO_ROOT, baseline_commit=BASELINE, output_root=out_b)
    for name in ARTIFACT_SCHEMAS:
        assert (out_a / name).read_bytes() == (out_b / name).read_bytes()
        assert canonical_hash(first[name]) == canonical_hash(second[name])


def test_receipt_terminal_decision_and_parent_status() -> None:
    payloads = build_packet_payloads(REPO_ROOT, baseline_commit=BASELINE)
    receipt = payloads["surface_resolution_receipt.latest.json"]
    assert receipt["packet_status"] == "PRODUCTION_SURFACE_RESOLUTION_001_COMPLETE"
    assert receipt["parent_stabilization_status"] == "STABILIZATION_ENTRY_HELD"
    assert receipt["recommended_next_work_order"] == "WO-ABX-STABILIZATION-CONTRACT-INVENTORY-002"