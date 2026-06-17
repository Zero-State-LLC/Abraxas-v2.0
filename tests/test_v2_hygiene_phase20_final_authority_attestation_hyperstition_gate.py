from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase20_final_authority_attestation_hyperstition_gate import (
    BLOCKED_STATUS,
    EXPECTED_PHASE26_HASH,
    FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_PROMOTION_CLASSES,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate,
    write_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate,
)
from scripts import run_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase20_final_authority_attestation_hyperstition_gate.v1.schema.json"
)
SOURCE_PHASE26_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase19_eternal_canon_self_governance_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_final_authority_attestation_hyperstition_gate_ready_with_phase26_source() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 27
    assert packet["final_authority_attestation_hyperstition_gate_ready"] is True
    assert packet["phase26_eternal_canon_self_governance_gate_hash_verified"] is True
    assert packet["valid_for_final_authority_attestation_hyperstition"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_final_authority_attestation_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    matrix = packet["final_authority_attestation_promotion_contract"][
        "final_authority_attestation_hyperstition_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_PROMOTION_CLASSES
    )
    assert all(
        surface["final_authority_attestation_hyperstition_recorded"] is True for surface in matrix
    )
    assert all(surface["eternal_canon_self_governance_recorded"] is True for surface in matrix)
    assert all(surface["final_authority_authorized"] is False for surface in matrix)
    assert all(surface["live_hyperstition_activation_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)
    assert all(surface["runtime_guards"]["live_hyperstition_telemetry_only"] is True for surface in matrix)
    assert all(
        surface["runtime_guards"]["final_authority_attestation_recorded_only"] is True
        for surface in matrix
    )
    assert all(
        surface["runtime_guards"]["controlled_authority_grant_denied"] is True for surface in matrix
    )


def test_limited_write_allowed_matches_phase26_pattern() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    matrix = packet["final_authority_attestation_promotion_contract"][
        "final_authority_attestation_hyperstition_promotion_matrix"
    ]
    by_surface = {surface["surface_id"]: surface for surface in matrix}

    assert by_surface["brier_engine_telemetry"]["limited_write_allowed"] is False
    assert by_surface["core_oracle_shadow"]["limited_write_allowed"] is True
    assert by_surface["planning_lane_outputs"]["limited_write_allowed"] is True
    assert by_surface["rune_visualization_layer"]["limited_write_allowed"] is True
    assert by_surface["incarnation_core_planning_binding"]["limited_write_allowed"] is True


def test_final_authority_attestation_workflow_recorded_only() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    workflow = packet["final_authority_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["attestation_grants_authority"] is False
    assert workflow["final_authority_attestation_recorded_only"] is True
    assert workflow["final_authority_authorized"] is False
    assert workflow["execution_authority_granted"] is False


def test_live_hyperstition_activation_contract_projection_only() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    live = packet["live_hyperstition_activation_contract"]

    assert live["telemetry_only"] is True
    assert live["projection_only"] is True
    assert live["live_hyperstition_activation_authorized"] is False
    assert live["hyperstition_propagation_projection_only"] is True
    assert live["hyperstition_engine_authorized"] is False
    assert live["execution_authority_granted"] is False


def test_final_authority_guard_hardening_denies_controlled_authority() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    guard = packet["final_authority_guard_hardening_contract"]

    assert guard["final_authority_authorized"] is False
    assert guard["controlled_authority_grant_denied"] is True
    assert guard["final_attestation_operator_signoff_required"] is True
    assert guard["live_hyperstition_activation_authorized"] is False
    assert guard["execution_authority_granted"] is False


def test_signal_forage_final_authority_closed_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    closed_loop = packet["signal_forage_final_authority_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["telemetry_only"] is True
    assert closed_loop["final_authority_closed_loop_bound"] is True
    assert closed_loop["global_ingest_hold_respected"] is True
    assert closed_loop["execution_authority"] is False
    assert closed_loop["all_paths_observed"] is True
    assert len(closed_loop["final_authority_closed_loop_bindings"]) >= 4


def test_final_authority_brier_telemetry_includes_dual_decomposition() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    brier = packet["final_authority_brier_telemetry_contract"]

    assert brier["telemetry_only"] is True
    assert brier["final_authority_attestation_promotion"] is True
    assert brier["final_authority_attestation_telemetry_only"] is True
    assert brier["signal_forage_bound"] is True
    assert brier["murphy_decomposition_default"] is True
    assert brier["yates_decomposition_default"] is True
    assert brier["operator_signoff_required"] is True
    assert brier["decomposition_mode"] == "MURPHY_AND_YATES"
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    for hook in brier["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "FINAL_AUTHORITY_ATTESTATION"
        assert hook["final_authority_attestation_bound"] is True
        assert hook["operator_signoff_required"] is True
        assert hook["resolution_allowed"] is False


def test_final_authority_attestation_receipt_contract() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    receipts = packet["final_authority_attestation_receipt_contract"]

    assert receipts["all_receipts_recorded"] is True
    assert receipts["receipt_count"] == 5
    assert receipts["execution_authority_granted"] is False
    assert receipts["final_authority_authorized"] is False
    assert all(
        receipt["final_authority_attestation_recorded_only"] is True
        for receipt in receipts["execution_receipts"]
    )
    assert all(
        receipt["live_hyperstition_telemetry_only"] is True
        for receipt in receipts["execution_receipts"]
    )
    assert all(receipt["final_authority_authorized"] is False for receipt in receipts["execution_receipts"])


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
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
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["hash_chain"]["phase26_gate_hash"] == EXPECTED_PHASE26_HASH
    assert workflow["hash_chain"]["phase27_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["final_authority_attestation_hyperstition_gate_hash"] != ""


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["final_authority_authorized"] is False
    assert packet["live_hyperstition_activation_authorized"] is False
    assert packet["hyperstition_engine_authorized"] is False
    assert packet["eternal_canon_self_governance_authorized"] is False
    assert packet["eternal_recursion_authorized"] is False
    assert packet["self_optimization_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["signal_forage_execution_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    promotion = packet["final_authority_attestation_promotion_contract"]
    assert promotion["final_authority_authorized"] is False
    assert promotion["live_hyperstition_activation_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_final_authority_attestation_gate_blocked_when_phase26_not_ready(tmp_path: Path) -> None:
    phase26 = _read_json(SOURCE_PHASE26_GATE_PATH)
    phase26["status"] = "V2_HYGIENE_PHASE19_ETERNAL_CANON_SELF_GOVERNANCE_GATE_BLOCKED"
    phase26_path = _write_source(tmp_path, "phase26.json", phase26)
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(
        REPO_ROOT,
        source_phase26_gate_path=phase26_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_final_authority_attestation_hyperstition"] is False
    assert "phase26_eternal_canon_self_governance_gate_not_ready" in packet["source_blockers"]


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["global_ingest_adapter_spine_hold_active"] is True
    assert denial["high_risk_mutations_denied"] is True


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    second = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(REPO_ROOT)
    assert (
        first["final_authority_attestation_hyperstition_gate_hash"]
        == second["final_authority_attestation_hyperstition_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("final_authority_attestation_hyperstition_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["final_authority_attestation_hyperstition_gate_hash"]
        == packet["final_authority_attestation_hyperstition_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
