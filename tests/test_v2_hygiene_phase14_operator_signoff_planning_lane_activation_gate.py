from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate import (
    EXPECTED_PHASE13_CLOSURE_HASH,
    PLANNING_SURFACE_MATRIX,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate,
    write_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate,
)
from scripts.hygiene import run_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate.v1.schema.json"
)
SOURCE_PHASE13_CLOSURE_PATH = (
    "out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_planning_lane_activation_gate_ready() -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_signoff_planning_lane_activation_gate_ready"] is True
    assert packet["planning_lane_activated"] is True
    assert packet["planning_lane_status"] == "PLANNING_LANE_ACTIVE_ADVISORY_ONLY"
    assert packet["phase13_operator_intelligence_closure_receipt_hash_verified"] is True
    assert packet["valid_for_planning_lane"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_planning_surface_matrix() -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(REPO_ROOT)
    matrix = packet["planning_lane_activation_contract"]["planning_surface_matrix"]
    expected_ids = {entry["surface_id"] for entry in PLANNING_SURFACE_MATRIX}
    assert {surface["surface_id"] for surface in matrix} == expected_ids
    assert all(surface["all_paths_observed"] is True for surface in matrix)
    assert all(surface["planning_lane_only"] is True for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)


def test_operator_signoff_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(REPO_ROOT)
    signoff = packet["operator_signoff_workflow_contract"]
    chain = signoff["hash_chain"]

    assert signoff["manual_operator_signoff_required"] is True
    assert signoff["operator_signoff_auto_approved"] is False
    assert signoff["notion_writeback_allowed"] is False
    assert chain["phase13_closure_receipt_hash"] == EXPECTED_PHASE13_CLOSURE_HASH
    assert packet["operator_signoff_planning_lane_activation_gate_hash"] != ""


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["package_lock_resolution_held"] is True
    assert packet["package_lock_mutation_authorized"] is False


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(REPO_ROOT)
    brier = packet["brier_scoring_contract"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert packet["rune_registration_authorized"] is False
    assert all(item["authority_granted"] is False for item in packet["rune_governance_mapping"])


def test_missing_phase13_closure_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(
        REPO_ROOT,
        source_phase13_closure_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE14_OPERATOR_SIGNOFF_PLANNING_LANE_ACTIVATION_GATE_BLOCKED"
    )
    assert "required_phase13_closure_receipt_missing" in packet["source_blockers"]


def test_phase13_closure_mutation_fails_closed(tmp_path: Path) -> None:
    closure = _read_json(SOURCE_PHASE13_CLOSURE_PATH)
    closure["operator_intelligence_closure_receipt_ready"] = False
    source = _write_source(tmp_path, "mutated_closure.json", closure)

    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(
        REPO_ROOT,
        source_phase13_closure_path=source,
    )

    assert packet["operator_signoff_planning_lane_activation_gate_ready"] is False
    assert "phase13_closure_receipt_ready_not_true" in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("operator_signoff_planning_lane_activation_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["operator_signoff_planning_lane_activation_gate_hash"] == packet[
        "operator_signoff_planning_lane_activation_gate_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
