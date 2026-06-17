from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase15_controlled_runtime_execution_promotion_gate import (
    BLOCKED_STATUS,
    CONTROLLED_RUNTIME_EXECUTION_PROMOTION_CLASSES,
    EXPECTED_PHASE21_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate,
    write_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate,
)
from scripts import run_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase15_controlled_runtime_execution_promotion_gate.v1.schema.json"
)
SOURCE_PHASE21_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase14_runtime_execution_surface_activation_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_controlled_runtime_promotion_gate_ready_with_phase21_source() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 22
    assert packet["controlled_runtime_execution_promotion_gate_ready"] is True
    assert packet["phase21_runtime_execution_surface_activation_gate_hash_verified"] is True
    assert packet["valid_for_controlled_runtime_execution_promotion"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_controlled_runtime_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    matrix = packet["controlled_runtime_execution_promotion_contract"][
        "controlled_runtime_execution_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        CONTROLLED_RUNTIME_EXECUTION_PROMOTION_CLASSES
    )
    assert all(surface["runtime_execution_activation_recorded"] is True for surface in matrix)
    assert all(
        surface["controlled_runtime_execution_promotion_recorded"] is True for surface in matrix
    )
    assert all(surface["controlled_runtime_execution_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["operator_signoff_required"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["controlled_runtime_write_only"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["uncontrolled_execution_denied"] is True for surface in matrix)


def test_limited_write_allowed_matches_phase9_pattern() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    matrix = packet["controlled_runtime_execution_promotion_contract"][
        "controlled_runtime_execution_promotion_matrix"
    ]
    by_surface = {surface["surface_id"]: surface for surface in matrix}

    assert by_surface["brier_engine_telemetry"]["limited_write_allowed"] is False
    assert by_surface["core_oracle_shadow"]["limited_write_allowed"] is True
    assert by_surface["planning_lane_outputs"]["limited_write_allowed"] is True
    assert by_surface["rune_visualization_layer"]["limited_write_allowed"] is True
    assert by_surface["incarnation_core_planning_binding"]["limited_write_allowed"] is True


def test_controlled_runtime_brier_telemetry_includes_dual_decomposition() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    brier = packet["controlled_runtime_brier_telemetry_contract"]

    assert brier["telemetry_only"] is True
    assert brier["runtime_telemetry_only"] is True
    assert brier["controlled_runtime_promotion"] is True
    assert brier["murphy_decomposition_default"] is True
    assert brier["yates_decomposition_default"] is True
    assert brier["operator_signoff_required"] is True
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
        assert hook["promotion_tier"] == "CONTROLLED_RUNTIME"
        assert hook["operator_signoff_required"] is True
        assert hook["controlled_runtime_promotion"] is True


def test_controlled_runtime_execution_receipt_contract() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    receipts = packet["controlled_runtime_execution_receipt_contract"]

    assert receipts["all_receipts_recorded"] is True
    assert receipts["receipt_count"] == 5
    assert receipts["execution_authority_granted"] is False
    assert all(receipt["controlled_runtime_only"] is True for receipt in receipts["execution_receipts"])
    assert all(receipt["operator_signoff_required"] is True for receipt in receipts["execution_receipts"])
    assert all(receipt["execution_authority_granted"] is False for receipt in receipts["execution_receipts"])


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
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
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["hash_chain"]["phase21_gate_hash"] == EXPECTED_PHASE21_HASH
    assert workflow["hash_chain"]["phase22_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["controlled_runtime_execution_promotion_gate_hash"] != ""


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["brier_resolution_authorized"] is False
    promotion = packet["controlled_runtime_execution_promotion_contract"]
    assert promotion["controlled_runtime_execution_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_controlled_runtime_promotion_gate_blocked_when_phase21_not_ready(tmp_path: Path) -> None:
    phase21 = _read_json(SOURCE_PHASE21_GATE_PATH)
    phase21["status"] = "V2_HYGIENE_PHASE14_RUNTIME_EXECUTION_SURFACE_ACTIVATION_GATE_BLOCKED"
    phase21_path = _write_source(tmp_path, "phase21.json", phase21)
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(
        REPO_ROOT,
        source_phase21_gate_path=phase21_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_controlled_runtime_execution_promotion"] is False
    assert "phase21_runtime_execution_surface_activation_gate_not_ready" in packet["source_blockers"]


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["high_risk_mutations_denied"] is True


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    second = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(REPO_ROOT)
    assert (
        first["controlled_runtime_execution_promotion_gate_hash"]
        == second["controlled_runtime_execution_promotion_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("controlled_runtime_execution_promotion_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["controlled_runtime_execution_promotion_gate_hash"]
        == packet["controlled_runtime_execution_promotion_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
