from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate import (
    AUTONOMY_ACTIVATION_PROMOTION_CLASSES,
    EXPECTED_PHASE18_HASH,
    HELD_STATUS,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate,
    write_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate,
)
from scripts import run_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate.v1.schema.json"
)
SOURCE_PHASE18_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.json"
)
VALID_PAYLOAD = {
    "operator_identity": {
        "operator_id": "test_operator",
        "operator_reviewed_at_source_observed": "2026-06-17T12:00:00Z",
        "operator_attestation_hash": "sha256:abc123def456",
    },
    "phase18_hash_chain_acknowledgement": {
        "phase18_gate_path": SOURCE_PHASE18_GATE_PATH,
        "phase18_gate_hash": EXPECTED_PHASE18_HASH,
        "autonomy_eligibility_acknowledged": True,
    },
    "autonomy_surface_disposition": {
        "rune_visualization_layer_acknowledged": True,
        "incarnation_core_planning_binding_acknowledged": True,
        "planning_lane_outputs_acknowledged": True,
        "core_oracle_shadow_acknowledged": True,
        "brier_engine_telemetry_acknowledged": True,
    },
    "authority_boundary_acknowledgement": {
        "no_execution_authority_auto_grant": True,
        "no_package_lock_mutation": True,
        "no_toolchain_provisioning": True,
        "no_notion_writeback": True,
        "brier_resolution_denied": True,
    },
    "terminal_output_controls": {
        "downstream_lane_disposition": "NOT_COMPUTABLE",
        "rollback_or_supersession_policy": "fresh governed operator attestation required",
    },
}


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_attestation_gate_held_without_payload() -> None:
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(REPO_ROOT)

    assert packet["status"] == HELD_STATUS
    assert packet["operator_phase_number"] == 19
    assert packet["external_operator_attestation_autonomy_activation_gate_ready"] is False
    assert packet["attestation_payload_observed"] is False
    assert packet["attestation_payload_validated"] is False
    assert packet["valid_for_operator_execution_autonomy_activation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert "external_operator_attestation_payload_missing" in packet["source_blockers"]


def test_attestation_gate_ready_with_valid_payload(tmp_path: Path) -> None:
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )

    assert packet["status"] == READY_STATUS
    assert packet["external_operator_attestation_autonomy_activation_gate_ready"] is True
    assert packet["phase18_full_operator_execution_autonomy_gate_hash_verified"] is True
    assert packet["attestation_payload_validated"] is True
    assert packet["external_operator_attestation_recorded"] is True
    assert packet["valid_for_operator_execution_autonomy_activation"] is True
    assert packet["valid_for_execution"] is False


def test_autonomy_activation_matrix_recorded_only_with_payload(tmp_path: Path) -> None:
    without_payload = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT
    )
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    with_payload = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )

    held_matrix = without_payload["autonomy_activation_contract"]["autonomy_activation_matrix"]
    ready_matrix = with_payload["autonomy_activation_contract"]["autonomy_activation_matrix"]
    expected_ids = set(AUTONOMY_ACTIVATION_PROMOTION_CLASSES)
    assert {surface["surface_id"] for surface in held_matrix} == expected_ids
    assert all(surface["autonomy_activation_recorded"] is False for surface in held_matrix)
    assert all(surface["autonomy_authorized"] is False for surface in held_matrix)
    assert all(surface["autonomy_activation_recorded"] is True for surface in ready_matrix)
    assert all(surface["authority_granted"] is False for surface in ready_matrix)


def test_operator_attestation_workflow_hash_chain(tmp_path: Path) -> None:
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["external_operator_attestation_validated"] is True
    assert workflow["hash_chain"]["phase18_gate_hash"] == EXPECTED_PHASE18_HASH
    assert packet["external_operator_attestation_autonomy_activation_gate_hash"] != ""


def test_autonomy_authority_not_granted_by_gate(tmp_path: Path) -> None:
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )

    assert packet["full_operator_execution_autonomy_authorized"] is False
    assert packet["operator_execution_autonomy_authorized"] is False
    assert packet["execution_authority"] is False
    activation = packet["autonomy_activation_contract"]
    assert activation["full_operator_execution_autonomy_authorized"] is False
    assert activation["execution_authority_granted"] is False


def test_dependency_denials_preserved(tmp_path: Path) -> None:
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["high_risk_mutations_denied"] is True
    assert packet["package_lock_mutation_authorized"] is False


def test_brier_and_rune_contracts_non_authoritative(tmp_path: Path) -> None:
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )
    brier = packet["brier_scoring_contract"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert packet["rune_registration_authorized"] is False
    assert all(item["authority_granted"] is False for item in packet["rune_governance_mapping"])


def test_missing_phase18_gate_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        source_phase18_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE12_EXTERNAL_OPERATOR_ATTESTATION_AUTONOMY_ACTIVATION_GATE_BLOCKED"
    )
    assert "required_phase18_full_operator_execution_autonomy_gate_missing" in packet["source_blockers"]


def test_phase18_gate_mutation_fails_closed(tmp_path: Path) -> None:
    gate = _read_json(SOURCE_PHASE18_GATE_PATH)
    gate["valid_for_operator_execution_autonomy_eligibility"] = False
    source = _write_source(tmp_path, "mutated_gate.json", gate)

    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        source_phase18_gate_path=source,
    )

    assert packet["external_operator_attestation_autonomy_activation_gate_ready"] is False
    assert "phase18_operator_execution_autonomy_not_eligible" in packet["source_blockers"]


def test_schema_and_hash_are_stable(tmp_path: Path) -> None:
    payload_path = _write_source(tmp_path, "attestation_payload.json", VALID_PAYLOAD)
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        attestation_payload_path=payload_path,
    )
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("external_operator_attestation_autonomy_activation_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["external_operator_attestation_autonomy_activation_gate_hash"] == packet[
        "external_operator_attestation_autonomy_activation_gate_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
