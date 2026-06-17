from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase8_execution_surface_expansion_advisory_gate import (
    EXECUTION_SURFACE_EXPANSION_MATRIX,
    EXPECTED_PHASE14_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate,
    write_v2_hygiene_phase8_execution_surface_expansion_advisory_gate,
)
from scripts import run_v2_hygiene_phase8_execution_surface_expansion_advisory_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase8_execution_surface_expansion_advisory_gate.v1.schema.json"
)
SOURCE_PHASE14_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_execution_surface_expansion_advisory_gate_ready() -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 15
    assert packet["execution_surface_expansion_advisory_gate_ready"] is True
    assert packet["phase14_operator_signoff_planning_lane_activation_gate_hash_verified"] is True
    assert packet["planning_lane_status"] == "PLANNING_LANE_ACTIVE_ADVISORY_ONLY"
    assert packet["valid_for_advisory_promotion"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_execution_surface_expansion_matrix() -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(REPO_ROOT)
    matrix = packet["execution_surface_expansion_contract"]["execution_surface_expansion_matrix"]
    expected_ids = {entry["surface_id"] for entry in EXECUTION_SURFACE_EXPANSION_MATRIX}
    assert {surface["surface_id"] for surface in matrix} == expected_ids
    assert all(surface["all_paths_observed"] is True for surface in matrix)
    assert all(surface["advisory_promotion_only"] is True for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["execution_denied"] is True for surface in matrix)


def test_advisory_promotion_hash_chain() -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(REPO_ROOT)
    hash_chain = packet["advisory_promotion_hash_chain_contract"]

    assert hash_chain["manual_operator_review_required"] is True
    assert hash_chain["notion_writeback_allowed"] is False
    assert hash_chain["hash_chain"]["phase14_gate_hash"] == EXPECTED_PHASE14_HASH
    assert packet["execution_surface_expansion_advisory_gate_hash"] != ""


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["package_lock_resolution_held"] is True
    assert packet["package_lock_mutation_authorized"] is False


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(REPO_ROOT)
    brier = packet["brier_scoring_contract"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert packet["rune_registration_authorized"] is False
    assert all(item["authority_granted"] is False for item in packet["rune_governance_mapping"])


def test_missing_phase14_gate_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(
        REPO_ROOT,
        source_phase14_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE8_EXECUTION_SURFACE_EXPANSION_ADVISORY_GATE_BLOCKED"
    )
    assert "required_phase14_planning_lane_gate_missing" in packet["source_blockers"]


def test_phase14_gate_mutation_fails_closed(tmp_path: Path) -> None:
    gate = _read_json(SOURCE_PHASE14_GATE_PATH)
    gate["planning_lane_activated"] = False
    source = _write_source(tmp_path, "mutated_gate.json", gate)

    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(
        REPO_ROOT,
        source_phase14_gate_path=source,
    )

    assert packet["execution_surface_expansion_advisory_gate_ready"] is False
    assert "phase14_planning_lane_not_activated" in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("execution_surface_expansion_advisory_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase8_execution_surface_expansion_advisory_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["execution_surface_expansion_advisory_gate_hash"] == packet[
        "execution_surface_expansion_advisory_gate_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
