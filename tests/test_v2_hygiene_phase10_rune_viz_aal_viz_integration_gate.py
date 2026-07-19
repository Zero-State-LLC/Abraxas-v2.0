from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase10_rune_viz_aal_viz_integration_gate import (
    EXPECTED_PHASE16_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    RUNE_VIZ_AAL_VIZ_INTEGRATION_MATRIX,
    build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate,
    write_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate,
)
from scripts.hygiene import run_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase10_rune_viz_aal_viz_integration_gate.v1.schema.json"
)
SOURCE_PHASE16_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase9_controlled_execution_promotion_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_rune_viz_aal_viz_integration_gate_ready() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 17
    assert packet["rune_viz_aal_viz_integration_gate_ready"] is True
    assert packet["phase16_controlled_execution_promotion_gate_hash_verified"] is True
    assert packet["valid_for_rune_viz_integration"] is True
    assert packet["valid_for_controlled_execution"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_rune_viz_aal_viz_integration_matrix() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)
    matrix = packet["rune_viz_aal_viz_integration_contract"]["rune_viz_aal_viz_integration_matrix"]
    expected_ids = {entry["surface_id"] for entry in RUNE_VIZ_AAL_VIZ_INTEGRATION_MATRIX}
    assert {surface["surface_id"] for surface in matrix} == expected_ids
    assert all(surface["all_paths_observed"] is True for surface in matrix)
    assert all(surface["rune_viz_integration_promoted"] is True for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["full_execution_denied"] is True for surface in matrix)
    assert all(surface["operator_signoff_required"] is True for surface in matrix)


def test_incarnation_core_integration_contract() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)
    incarnation = packet["incarnation_core_integration_contract"]

    assert incarnation["incarnation_core_planning_stub_observed"] is True
    assert incarnation["rune_route_binding_matrix_observed"] is True
    assert incarnation["incarnation_core_binding_authority_granted"] is False
    assert incarnation["rune_registration_authorized"] is False


def test_operator_signoff_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)
    signoff = packet["operator_signoff_workflow_contract"]

    assert signoff["manual_operator_signoff_required"] is True
    assert signoff["operator_signoff_auto_approved"] is False
    assert signoff["notion_writeback_allowed"] is False
    assert signoff["hash_chain"]["phase16_gate_hash"] == EXPECTED_PHASE16_HASH
    assert packet["rune_viz_aal_viz_integration_gate_hash"] != ""


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["high_authority_mutations_denied"] is True
    assert packet["package_lock_mutation_authorized"] is False


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)
    brier = packet["brier_scoring_contract"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert packet["rune_registration_authorized"] is False
    assert all(item["authority_granted"] is False for item in packet["rune_governance_mapping"])


def test_missing_phase16_gate_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(
        REPO_ROOT,
        source_phase16_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE10_RUNE_VIZ_AAL_VIZ_INTEGRATION_GATE_BLOCKED"
    )
    assert "required_phase16_controlled_execution_promotion_gate_missing" in packet["source_blockers"]


def test_phase16_gate_mutation_fails_closed(tmp_path: Path) -> None:
    gate = _read_json(SOURCE_PHASE16_GATE_PATH)
    gate["valid_for_controlled_execution"] = False
    source = _write_source(tmp_path, "mutated_gate.json", gate)

    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(
        REPO_ROOT,
        source_phase16_gate_path=source,
    )

    assert packet["rune_viz_aal_viz_integration_gate_ready"] is False
    assert "phase16_controlled_execution_not_eligible" in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("rune_viz_aal_viz_integration_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["rune_viz_aal_viz_integration_gate_hash"] == packet[
        "rune_viz_aal_viz_integration_gate_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
