from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase16_live_runtime_execution_signal_forage_gate import (
    BLOCKED_STATUS,
    EXPECTED_PHASE22_HASH,
    LIVE_RUNTIME_EXECUTION_PROMOTION_CLASSES,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate,
    write_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate,
)
from scripts import run_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase16_live_runtime_execution_signal_forage_gate.v1.schema.json"
)
SOURCE_PHASE22_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_live_runtime_gate_ready_with_phase22_source() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 23
    assert packet["live_runtime_execution_signal_forage_gate_ready"] is True
    assert packet["phase22_controlled_runtime_execution_promotion_gate_hash_verified"] is True
    assert packet["valid_for_live_runtime_execution"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_live_runtime_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    matrix = packet["live_runtime_execution_promotion_contract"]["live_runtime_execution_promotion_matrix"]

    assert {surface["surface_id"] for surface in matrix} == set(LIVE_RUNTIME_EXECUTION_PROMOTION_CLASSES)
    assert all(surface["runtime_execution_activation_recorded"] is True for surface in matrix)
    assert all(surface["controlled_runtime_execution_promotion_recorded"] is True for surface in matrix)
    assert all(surface["live_runtime_execution_recorded"] is True for surface in matrix)
    assert all(surface["live_runtime_execution_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["live_runtime_attestation_required"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["signal_forage_shadow_only"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["global_ingest_hold_respected"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["uncontrolled_live_execution_denied"] is True for surface in matrix)


def test_limited_write_allowed_matches_phase22_pattern() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    matrix = packet["live_runtime_execution_promotion_contract"]["live_runtime_execution_promotion_matrix"]
    by_surface = {surface["surface_id"]: surface for surface in matrix}

    assert by_surface["brier_engine_telemetry"]["limited_write_allowed"] is False
    assert by_surface["core_oracle_shadow"]["limited_write_allowed"] is True
    assert by_surface["planning_lane_outputs"]["limited_write_allowed"] is True
    assert by_surface["rune_visualization_layer"]["limited_write_allowed"] is True
    assert by_surface["incarnation_core_planning_binding"]["limited_write_allowed"] is True


def test_signal_forage_integration_contract_shadow_only() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    signal_forage = packet["signal_forage_integration_contract"]

    assert signal_forage["shadow_only"] is True
    assert signal_forage["telemetry_only"] is True
    assert signal_forage["signal_forage_bound"] is True
    assert signal_forage["global_ingest_adapter_spine_hold_active"] is True
    assert signal_forage["execution_authority"] is False
    assert signal_forage["all_paths_observed"] is True
    assert "scripts/ingest/run_ingest_once.py" in signal_forage["global_ingest_shadow_paths"]
    assert "scripts/ingest/run_oracle_intake.py" in signal_forage["global_ingest_shadow_paths"]


def test_unified_execution_loop_contract_non_authoritative() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    loop = packet["unified_execution_loop_contract"]

    assert loop["telemetry_only"] is True
    assert loop["live_loop_execution_authorized"] is False
    assert loop["signal_forage_shadow_only"] is True
    assert loop["execution_authority_granted"] is False
    assert len(loop["loop_bindings"]) == 4


def test_live_runtime_brier_telemetry_includes_dual_decomposition_and_signal_forage() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    brier = packet["live_runtime_brier_telemetry_contract"]

    assert brier["telemetry_only"] is True
    assert brier["live_runtime_promotion"] is True
    assert brier["signal_forage_bound"] is True
    assert brier["murphy_decomposition_default"] is True
    assert brier["yates_decomposition_default"] is True
    assert brier["operator_signoff_required"] is True
    assert brier["decomposition_mode"] == "MURPHY_AND_YATES"
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    for hook in brier["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "LIVE_RUNTIME"
        assert hook["signal_forage_bound"] is True
        assert hook["operator_signoff_required"] is True
        assert hook["resolution_allowed"] is False


def test_live_runtime_execution_receipt_contract() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    receipts = packet["live_runtime_execution_receipt_contract"]

    assert receipts["all_receipts_recorded"] is True
    assert receipts["receipt_count"] == 5
    assert receipts["execution_authority_granted"] is False
    assert all(receipt["live_runtime_only"] is True for receipt in receipts["execution_receipts"])
    assert all(receipt["operator_signoff_required"] is True for receipt in receipts["execution_receipts"])
    assert all(receipt["execution_authority_granted"] is False for receipt in receipts["execution_receipts"])


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
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
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["hash_chain"]["phase22_gate_hash"] == EXPECTED_PHASE22_HASH
    assert workflow["hash_chain"]["phase23_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["live_runtime_execution_signal_forage_gate_hash"] != ""


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["live_runtime_execution_authorized"] is False
    assert packet["signal_forage_execution_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    promotion = packet["live_runtime_execution_promotion_contract"]
    assert promotion["live_runtime_execution_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_live_runtime_gate_blocked_when_phase22_not_ready(tmp_path: Path) -> None:
    phase22 = _read_json(SOURCE_PHASE22_GATE_PATH)
    phase22["status"] = "V2_HYGIENE_PHASE15_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_GATE_BLOCKED"
    phase22_path = _write_source(tmp_path, "phase22.json", phase22)
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(
        REPO_ROOT,
        source_phase22_gate_path=phase22_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_live_runtime_execution"] is False
    assert "phase22_controlled_runtime_execution_promotion_gate_not_ready" in packet["source_blockers"]


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["global_ingest_adapter_spine_hold_active"] is True
    assert denial["high_risk_mutations_denied"] is True


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    second = build_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(REPO_ROOT)
    assert (
        first["live_runtime_execution_signal_forage_gate_hash"]
        == second["live_runtime_execution_signal_forage_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("live_runtime_execution_signal_forage_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase16_live_runtime_execution_signal_forage_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["live_runtime_execution_signal_forage_gate_hash"]
        == packet["live_runtime_execution_signal_forage_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
