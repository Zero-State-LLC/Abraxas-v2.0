from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase13_autonomy_activation_brier_hardening_gate import (
    AUTONOMY_HARDENING_PROMOTION_CLASSES,
    BLOCKED_STATUS,
    EXPECTED_PHASE19_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate,
    write_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate,
)
from scripts import run_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase13_autonomy_activation_brier_hardening_gate.v1.schema.json"
)
SOURCE_PHASE19_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_hardening_gate_ready_with_phase19_source() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 20
    assert packet["autonomy_activation_brier_hardening_gate_ready"] is True
    assert packet["phase19_external_operator_attestation_autonomy_activation_gate_hash_verified"] is True
    assert packet["valid_for_autonomy_hardening"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_autonomy_hardening_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    matrix = packet["autonomy_hardening_contract"]["autonomy_hardening_matrix"]

    assert {surface["surface_id"] for surface in matrix} == set(AUTONOMY_HARDENING_PROMOTION_CLASSES)
    assert all(surface["autonomy_hardening_recorded"] is True for surface in matrix)
    assert all(surface["autonomy_activation_recorded"] is True for surface in matrix)
    assert all(surface["autonomy_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)


def test_brier_hardening_contract_includes_dual_decomposition() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    brier = packet["brier_hardening_contract"]

    assert brier["telemetry_only"] is True
    assert brier["murphy_decomposition_enabled"] is True
    assert brier["yates_decomposition_enabled"] is True
    assert brier["decomposition_mode"] == "MURPHY_AND_YATES"
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    fixture = brier["fixture_decomposition"]
    assert set(fixture["murphy"]) == {"reliability", "resolution", "uncertainty", "brier_score"}
    assert set(fixture["yates"]) == {
        "bias_squared",
        "excess_variance",
        "covariance_deficit",
        "brier_score",
    }
    for hook in brier["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["resolution_allowed"] is False


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    brier = packet["brier_scoring_contract"]
    rune = packet["rune_governance_mapping"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert all(entry["authority_granted"] is False for entry in rune)
    weigh = next(entry for entry in rune if entry["rune"] == "Weigh")
    assert weigh["decomposition_mode"] == "MURPHY_AND_YATES"


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["external_operator_attestation_validated"] is True
    assert workflow["hash_chain"]["phase19_gate_hash"] == EXPECTED_PHASE19_HASH
    assert packet["autonomy_activation_brier_hardening_gate_hash"] != ""


def test_final_attestation_receipt_contract() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    receipt = packet["final_attestation_receipt_contract"]

    assert receipt["attestation_payload_validated"] is True
    assert receipt["external_operator_attestation_recorded"] is True
    assert receipt["phase19_gate_hash"] == EXPECTED_PHASE19_HASH
    assert receipt["operator_id"] == "daniel_meyer"
    assert receipt["authority_granted"] is False


def test_autonomy_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)

    assert packet["full_operator_execution_autonomy_authorized"] is False
    assert packet["operator_execution_autonomy_authorized"] is False
    assert packet["execution_authority"] is False
    hardening = packet["autonomy_hardening_contract"]
    assert hardening["full_operator_execution_autonomy_authorized"] is False
    assert hardening["execution_authority_granted"] is False


def test_hardening_gate_blocked_when_phase19_not_ready(tmp_path: Path) -> None:
    phase19 = _read_json(SOURCE_PHASE19_GATE_PATH)
    phase19["status"] = "V2_HYGIENE_PHASE12_EXTERNAL_OPERATOR_ATTESTATION_AUTONOMY_ACTIVATION_GATE_BLOCKED"
    phase19_path = _write_source(tmp_path, "phase19.json", phase19)
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(
        REPO_ROOT,
        source_phase19_gate_path=phase19_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_autonomy_hardening"] is False
    assert "phase19_external_operator_attestation_autonomy_activation_gate_not_ready" in packet["source_blockers"]


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["high_risk_mutations_denied"] is True


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    second = build_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(REPO_ROOT)
    assert (
        first["autonomy_activation_brier_hardening_gate_hash"]
        == second["autonomy_activation_brier_hardening_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("autonomy_activation_brier_hardening_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase13_autonomy_activation_brier_hardening_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["autonomy_activation_brier_hardening_gate_hash"]
        == packet["autonomy_activation_brier_hardening_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
