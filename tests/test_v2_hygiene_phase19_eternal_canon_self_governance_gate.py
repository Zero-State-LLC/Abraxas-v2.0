from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase19_eternal_canon_self_governance_gate import (
    BLOCKED_STATUS,
    ETERNAL_CANON_SELF_GOVERNANCE_PROMOTION_CLASSES,
    EXPECTED_PHASE25_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase19_eternal_canon_self_governance_gate,
    write_v2_hygiene_phase19_eternal_canon_self_governance_gate,
)
from scripts import run_v2_hygiene_phase19_eternal_canon_self_governance_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase19_eternal_canon_self_governance_gate.v1.schema.json"
)
SOURCE_PHASE25_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase18_eternal_recursion_hyperstition_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_eternal_canon_self_governance_gate_ready_with_phase25_source() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 26
    assert packet["eternal_canon_self_governance_gate_ready"] is True
    assert packet["phase25_eternal_recursion_hyperstition_gate_hash_verified"] is True
    assert packet["valid_for_eternal_canon_self_governance"] is True
    assert packet["valid_for_execution"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_eternal_canon_self_governance_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    matrix = packet["eternal_canon_self_governance_promotion_contract"][
        "eternal_canon_self_governance_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        ETERNAL_CANON_SELF_GOVERNANCE_PROMOTION_CLASSES
    )
    assert all(surface["eternal_canon_self_governance_recorded"] is True for surface in matrix)
    assert all(surface["eternal_recursion_hyperstition_recorded"] is True for surface in matrix)
    assert all(surface["eternal_canon_self_governance_authorized"] is False for surface in matrix)
    assert all(surface["final_authority_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)
    assert all(
        surface["runtime_guards"]["eternal_canon_self_governance_telemetry_only"] is True
        for surface in matrix
    )
    assert all(surface["runtime_guards"]["final_authority_denied"] is True for surface in matrix)
    assert all(
        surface["runtime_guards"]["eternal_canon_self_governance_attestation_required"] is True
        for surface in matrix
    )


def test_limited_write_allowed_matches_phase25_pattern() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    matrix = packet["eternal_canon_self_governance_promotion_contract"][
        "eternal_canon_self_governance_promotion_matrix"
    ]
    by_surface = {surface["surface_id"]: surface for surface in matrix}

    assert by_surface["brier_engine_telemetry"]["limited_write_allowed"] is False
    assert by_surface["core_oracle_shadow"]["limited_write_allowed"] is True
    assert by_surface["planning_lane_outputs"]["limited_write_allowed"] is True
    assert by_surface["rune_visualization_layer"]["limited_write_allowed"] is True
    assert by_surface["incarnation_core_planning_binding"]["limited_write_allowed"] is True


def test_eternal_canon_self_governance_loop_contract_advisory_only() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    loop = packet["eternal_canon_self_governance_loop_contract"]

    assert loop["telemetry_only"] is True
    assert loop["eternal_canon_self_governance_telemetry_only"] is True
    assert loop["eternal_canon_self_governance_loop_execution_authorized"] is False
    assert loop["self_auditing_advisory_only"] is True
    assert loop["auto_promotion_projection_only"] is True
    assert loop["final_authority_denied"] is True
    assert loop["execution_authority_granted"] is False


def test_final_authority_guard_contract_denies_controlled_authority() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    guard = packet["final_authority_guard_contract"]

    assert guard["final_authority_authorized"] is False
    assert guard["controlled_authority_grant_denied"] is True
    assert guard["eternal_canon_self_governance_authorized"] is False
    assert guard["execution_authority_granted"] is False


def test_signal_forage_eternal_canon_self_governance_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    eternal_loop = packet["signal_forage_eternal_canon_self_governance_loop_contract"]

    assert eternal_loop["shadow_only"] is True
    assert eternal_loop["telemetry_only"] is True
    assert eternal_loop["eternal_canon_self_governance_loop_bound"] is True
    assert eternal_loop["global_ingest_adapter_spine_hold_active"] is True
    assert eternal_loop["execution_authority"] is False
    assert eternal_loop["all_paths_observed"] is True
    assert len(eternal_loop["eternal_canon_self_governance_loop_bindings"]) >= 4


def test_eternal_canon_brier_telemetry_includes_dual_decomposition() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    brier = packet["eternal_canon_brier_telemetry_contract"]

    assert brier["telemetry_only"] is True
    assert brier["eternal_canon_self_governance_promotion"] is True
    assert brier["eternal_canon_self_governance_telemetry_only"] is True
    assert brier["signal_forage_bound"] is True
    assert brier["murphy_decomposition_default"] is True
    assert brier["yates_decomposition_default"] is True
    assert brier["operator_signoff_required"] is True
    assert brier["decomposition_mode"] == "MURPHY_AND_YATES"
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    for hook in brier["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "ETERNAL_CANON_SELF_GOVERNANCE"
        assert hook["eternal_canon_self_governance_bound"] is True
        assert hook["operator_signoff_required"] is True
        assert hook["resolution_allowed"] is False


def test_eternal_canon_self_governance_receipt_contract() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    receipts = packet["eternal_canon_self_governance_receipt_contract"]

    assert receipts["all_receipts_recorded"] is True
    assert receipts["receipt_count"] == 5
    assert receipts["execution_authority_granted"] is False
    assert receipts["final_authority_authorized"] is False
    assert all(
        receipt["eternal_canon_self_governance_telemetry_only"] is True
        for receipt in receipts["execution_receipts"]
    )
    assert all(
        receipt["self_auditing_advisory_only"] is True for receipt in receipts["execution_receipts"]
    )
    assert all(receipt["final_authority_authorized"] is False for receipt in receipts["execution_receipts"])


def test_brier_and_rune_contracts_non_authoritative() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
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
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["hash_chain"]["phase25_gate_hash"] == EXPECTED_PHASE25_HASH
    assert workflow["hash_chain"]["phase26_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["eternal_canon_self_governance_gate_hash"] != ""


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["eternal_canon_self_governance_authorized"] is False
    assert packet["final_authority_authorized"] is False
    assert packet["hyperstition_engine_authorized"] is False
    assert packet["eternal_recursion_authorized"] is False
    assert packet["self_optimization_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["signal_forage_execution_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    promotion = packet["eternal_canon_self_governance_promotion_contract"]
    assert promotion["eternal_canon_self_governance_authorized"] is False
    assert promotion["final_authority_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_eternal_canon_self_governance_gate_blocked_when_phase25_not_ready(tmp_path: Path) -> None:
    phase25 = _read_json(SOURCE_PHASE25_GATE_PATH)
    phase25["status"] = "V2_HYGIENE_PHASE18_ETERNAL_RECURSION_HYPERSTITION_GATE_BLOCKED"
    phase25_path = _write_source(tmp_path, "phase25.json", phase25)
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(
        REPO_ROOT,
        source_phase25_gate_path=phase25_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_eternal_canon_self_governance"] is False
    assert "phase25_eternal_recursion_hyperstition_gate_not_ready" in packet["source_blockers"]


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["global_ingest_adapter_spine_hold_active"] is True
    assert denial["high_risk_mutations_denied"] is True


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    second = build_v2_hygiene_phase19_eternal_canon_self_governance_gate(REPO_ROOT)
    assert (
        first["eternal_canon_self_governance_gate_hash"]
        == second["eternal_canon_self_governance_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("eternal_canon_self_governance_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase19_eternal_canon_self_governance_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase19_eternal_canon_self_governance_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["eternal_canon_self_governance_gate_hash"]
        == packet["eternal_canon_self_governance_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
