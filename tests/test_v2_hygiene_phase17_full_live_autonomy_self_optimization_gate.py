from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase17_full_live_autonomy_self_optimization_gate import (
    BLOCKED_STATUS,
    EXPECTED_PHASE23_HASH,
    FULL_LIVE_AUTONOMY_SELF_OPTIMIZATION_PROMOTION_CLASSES,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate,
    write_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate,
)
from scripts.hygiene import run_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase17_full_live_autonomy_self_optimization_gate.v1.schema.json"
)
SOURCE_PHASE23_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_full_live_autonomy_gate_ready_with_phase23_source() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 24
    assert packet["full_live_autonomy_self_optimization_gate_ready"] is True
    assert packet["phase23_live_runtime_execution_signal_forage_gate_hash_verified"] is True
    assert packet["valid_for_full_live_autonomy_self_optimization"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_full_live_autonomy_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    matrix = packet["full_live_autonomy_promotion_contract"][
        "full_live_autonomy_self_optimization_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        FULL_LIVE_AUTONOMY_SELF_OPTIMIZATION_PROMOTION_CLASSES
    )
    assert all(surface["full_live_autonomy_self_optimization_recorded"] is True for surface in matrix)
    assert all(surface["live_runtime_execution_recorded"] is True for surface in matrix)
    assert all(surface["full_live_autonomy_authorized"] is False for surface in matrix)
    assert all(surface["self_optimization_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["self_optimization_telemetry_only"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["adaptive_learning_denied"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["full_live_autonomy_attestation_required"] is True for surface in matrix)


def test_limited_write_allowed_matches_phase23_pattern() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    matrix = packet["full_live_autonomy_promotion_contract"][
        "full_live_autonomy_self_optimization_promotion_matrix"
    ]
    by_surface = {surface["surface_id"]: surface for surface in matrix}

    assert by_surface["brier_engine_telemetry"]["limited_write_allowed"] is False
    assert by_surface["core_oracle_shadow"]["limited_write_allowed"] is True
    assert by_surface["planning_lane_outputs"]["limited_write_allowed"] is True
    assert by_surface["rune_visualization_layer"]["limited_write_allowed"] is True
    assert by_surface["incarnation_core_planning_binding"]["limited_write_allowed"] is True


def test_self_optimization_loop_contract_advisory_only() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    loop = packet["self_optimization_loop_contract"]

    assert loop["telemetry_only"] is True
    assert loop["self_optimization_telemetry_only"] is True
    assert loop["self_optimization_loop_execution_authorized"] is False
    assert loop["adaptive_learning_denied"] is True
    assert loop["brier_feedback_loop_non_authoritative"] is True
    assert loop["drift_annihilation_advisory_only"] is True
    assert loop["auto_calibration_projection_only"] is True
    assert loop["execution_authority_granted"] is False


def test_signal_forage_closed_loop_contract_shadow_only() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    closed_loop = packet["signal_forage_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["telemetry_only"] is True
    assert closed_loop["closed_loop_bound"] is True
    assert closed_loop["global_ingest_adapter_spine_hold_active"] is True
    assert closed_loop["execution_authority"] is False
    assert closed_loop["all_paths_observed"] is True
    assert len(closed_loop["closed_loop_bindings"]) >= 3


def test_full_live_autonomy_brier_telemetry_includes_dual_decomposition() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    brier = packet["full_live_autonomy_brier_telemetry_contract"]

    assert brier["telemetry_only"] is True
    assert brier["full_live_autonomy_promotion"] is True
    assert brier["self_optimization_bound"] is True
    assert brier["murphy_decomposition_default"] is True
    assert brier["yates_decomposition_default"] is True
    assert brier["operator_signoff_required"] is True
    assert brier["decomposition_mode"] == "MURPHY_AND_YATES"
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    for hook in brier["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "FULL_LIVE_AUTONOMY"
        assert hook["self_optimization_bound"] is True
        assert hook["operator_signoff_required"] is True
        assert hook["resolution_allowed"] is False


def test_full_live_autonomy_receipt_contract() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    receipts = packet["full_live_autonomy_receipt_contract"]

    assert receipts["all_receipts_recorded"] is True
    assert receipts["receipt_count"] == 5
    assert receipts["execution_authority_granted"] is False
    assert all(
        receipt["self_optimization_telemetry_only"] is True for receipt in receipts["execution_receipts"]
    )
    assert all(receipt["operator_signoff_required"] is True for receipt in receipts["execution_receipts"])
    assert all(receipt["execution_authority_granted"] is False for receipt in receipts["execution_receipts"])


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
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
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["hash_chain"]["phase23_gate_hash"] == EXPECTED_PHASE23_HASH
    assert workflow["hash_chain"]["phase24_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["full_live_autonomy_self_optimization_gate_hash"] != ""


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["full_live_autonomy_authorized"] is False
    assert packet["self_optimization_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["live_runtime_execution_authorized"] is False
    assert packet["signal_forage_execution_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    promotion = packet["full_live_autonomy_promotion_contract"]
    assert promotion["full_live_autonomy_authorized"] is False
    assert promotion["self_optimization_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_full_live_autonomy_gate_blocked_when_phase23_not_ready(tmp_path: Path) -> None:
    phase23 = _read_json(SOURCE_PHASE23_GATE_PATH)
    phase23["status"] = "V2_HYGIENE_PHASE16_LIVE_RUNTIME_EXECUTION_SIGNAL_FORAGE_GATE_BLOCKED"
    phase23_path = _write_source(tmp_path, "phase23.json", phase23)
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(
        REPO_ROOT,
        source_phase23_gate_path=phase23_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_full_live_autonomy_self_optimization"] is False
    assert "phase23_live_runtime_execution_signal_forage_gate_not_ready" in packet["source_blockers"]


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["global_ingest_adapter_spine_hold_active"] is True
    assert denial["high_risk_mutations_denied"] is True


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    second = build_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(REPO_ROOT)
    assert (
        first["full_live_autonomy_self_optimization_gate_hash"]
        == second["full_live_autonomy_self_optimization_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("full_live_autonomy_self_optimization_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase17_full_live_autonomy_self_optimization_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["full_live_autonomy_self_optimization_gate_hash"]
        == packet["full_live_autonomy_self_optimization_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
