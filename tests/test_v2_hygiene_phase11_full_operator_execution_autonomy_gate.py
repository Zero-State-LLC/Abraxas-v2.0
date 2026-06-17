from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase11_full_operator_execution_autonomy_gate import (
    EXPECTED_PHASE17_HASH,
    FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase11_full_operator_execution_autonomy_gate,
    write_v2_hygiene_phase11_full_operator_execution_autonomy_gate,
)
from scripts import run_v2_hygiene_phase11_full_operator_execution_autonomy_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase11_full_operator_execution_autonomy_gate.v1.schema.json"
)
SOURCE_PHASE17_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_full_operator_execution_autonomy_gate_ready() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 18
    assert packet["full_operator_execution_autonomy_gate_ready"] is True
    assert packet["phase17_rune_viz_aal_viz_integration_gate_hash_verified"] is True
    assert packet["valid_for_operator_execution_autonomy_eligibility"] is True
    assert packet["valid_for_execution"] is False
    assert packet["external_operator_attestation_required"] is True
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_full_operator_execution_autonomy_matrix() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)
    matrix = packet["full_operator_execution_autonomy_contract"]["full_operator_execution_autonomy_matrix"]
    expected_ids = {entry["surface_id"] for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX}
    assert {surface["surface_id"] for surface in matrix} == expected_ids
    assert all(surface["all_paths_observed"] is True for surface in matrix)
    assert all(surface["autonomy_eligible"] is True for surface in matrix)
    assert all(surface["autonomy_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["final_signoff_required"] is True for surface in matrix)


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)
    attestation = packet["operator_attestation_workflow_contract"]

    assert attestation["manual_operator_signoff_required"] is True
    assert attestation["external_operator_attestation_required"] is True
    assert attestation["operator_signoff_auto_approved"] is False
    assert attestation["hash_chain"]["phase17_gate_hash"] == EXPECTED_PHASE17_HASH
    assert packet["full_operator_execution_autonomy_gate_hash"] != ""


def test_autonomy_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)

    assert packet["full_operator_execution_autonomy_authorized"] is False
    assert packet["operator_execution_autonomy_authorized"] is False
    assert packet["execution_authority"] is False
    autonomy = packet["full_operator_execution_autonomy_contract"]
    assert autonomy["full_operator_execution_autonomy_authorized"] is False
    assert autonomy["execution_authority_granted"] is False


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["high_risk_mutations_denied"] is True
    assert packet["package_lock_mutation_authorized"] is False


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)
    brier = packet["brier_scoring_contract"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert packet["rune_registration_authorized"] is False
    assert all(item["authority_granted"] is False for item in packet["rune_governance_mapping"])


def test_missing_phase17_gate_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(
        REPO_ROOT,
        source_phase17_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE11_FULL_OPERATOR_EXECUTION_AUTONOMY_GATE_BLOCKED"
    )
    assert "required_phase17_rune_viz_aal_viz_integration_gate_missing" in packet["source_blockers"]


def test_phase17_gate_mutation_fails_closed(tmp_path: Path) -> None:
    gate = _read_json(SOURCE_PHASE17_GATE_PATH)
    gate["valid_for_rune_viz_integration"] = False
    source = _write_source(tmp_path, "mutated_gate.json", gate)

    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(
        REPO_ROOT,
        source_phase17_gate_path=source,
    )

    assert packet["full_operator_execution_autonomy_gate_ready"] is False
    assert "phase17_rune_viz_integration_not_eligible" in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("full_operator_execution_autonomy_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase11_full_operator_execution_autonomy_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase11_full_operator_execution_autonomy_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["full_operator_execution_autonomy_gate_hash"] == packet[
        "full_operator_execution_autonomy_gate_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
