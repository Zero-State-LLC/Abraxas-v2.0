from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import write_canonical_json
from core.sync.v2_hygiene_phase23_live_execution_activation_authorization_review_gate import (
    BLOCKED_STATUS,
    EXPECTED_PHASE29_HASH,
    LIVE_EXECUTION_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES,
    READY_STATUS,
    build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate,
    write_v2_hygiene_phase23_live_execution_activation_authorization_review_gate,
)
from scripts.hygiene import run_v2_hygiene_phase23_live_execution_activation_authorization_review_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase23_live_execution_activation_authorization_review_gate.v1.schema.json"
)
SOURCE_PHASE29_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_live_execution_activation_gate_ready_with_phase29_source() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 30
    assert packet["live_execution_activation_authorization_review_gate_ready"] is True
    assert packet["phase29_final_operator_signoff_live_authority_fractal_numogram_gate_hash_verified"] is True
    assert packet["valid_for_live_execution_activation_authorization_review"] is True
    assert packet["valid_for_execution"] is False
    assert packet["phase30_activation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    matrix = packet["live_execution_activation_authorization_review_promotion_contract"][
        "live_execution_activation_authorization_review_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        LIVE_EXECUTION_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES
    )
    assert all(
        surface["live_execution_activation_authorization_review_recorded"] is True
        for surface in matrix
    )
    assert all(
        surface["final_operator_signoff_live_authority_fractal_numogram_recorded"] is True
        for surface in matrix
    )
    assert all(surface["phase30_activation_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(
        surface["runtime_guards"]["live_execution_activation_recorded_only"] is True
        for surface in matrix
    )
    assert all(
        surface["runtime_guards"]["canon_execution_seal_projection_only"] is True
        for surface in matrix
    )


def test_live_execution_activation_workflow_recorded_only() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    workflow = packet["live_execution_activation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["attestation_grants_authority"] is False
    assert workflow["live_execution_activation_recorded_only"] is True
    assert workflow["canon_execution_seal_projection_only"] is True
    assert workflow["execution_authority_granted"] is False
    assert workflow["phase30_activation_authorized"] is False


def test_live_execution_activation_recorded_contract_denies_authority() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    live_execution = packet["live_execution_activation_recorded_contract"]

    assert live_execution["telemetry_only"] is True
    assert live_execution["live_execution_activation_recorded_only"] is True
    assert live_execution["execution_authority"] is False
    assert live_execution["controlled_live_execution_grant_denied"] is True
    assert live_execution["execution_authority_granted"] is False


def test_canon_execution_seal_projection_only() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    seal = packet["canon_execution_seal_projection_contract"]

    assert seal["canon_execution_seal_recorded"] is True
    assert seal["canon_seal_grants_authority"] is False
    assert seal["canon_execution_seal_projection_only"] is True
    assert seal["execution_authority_granted"] is False


def test_phase30_activation_authorization_review_recorded_not_authorized() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    review = packet["phase30_activation_authorization_review_contract"]

    assert review["phase30_activation_review_recorded"] is True
    assert review["phase30_activation_authorized"] is False
    assert review["phase30_activation_authorization_review_recorded_only"] is True


def test_fractal_numogram_lattice_activation_telemetry_only() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    lattice = packet["fractal_numogram_lattice_activation_contract"]

    assert lattice["fractal_numogram_lattice_activation_recorded"] is True
    assert lattice["fractal_numogram_lattice_telemetry_only"] is True
    assert lattice["fractal_numogram_runtime_authorized"] is False
    assert lattice["numogram_zone_count"] == 9


def test_mfdfa_hurst_brier_fractal_scaling_contract() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    scaling = packet["mfdfa_hurst_brier_fractal_scaling_contract"]

    assert scaling["murphy_decomposition_default"] is True
    assert scaling["yates_decomposition_default"] is True
    assert scaling["mfdfa_hurst_bound"] is True
    assert scaling["hurst_exponent"] > 0.0
    assert scaling["decomposition_mode"] == "MURPHY_AND_YATES"
    for hook in scaling["telemetry_hooks"]:
        assert hook["promotion_tier"] == "LIVE_EXECUTION_ACTIVATION_AUTHORIZATION_REVIEW"
        assert hook["mfdfa_hurst_bound"] is True
        assert hook["fractal_numogram_bound"] is True


def test_signal_forage_fractal_numogram_closed_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    closed_loop = packet["signal_forage_fractal_numogram_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["fractal_numogram_closed_loop_bound"] is True
    assert closed_loop["global_ingest_hold_respected"] is True
    assert closed_loop["all_paths_observed"] is True


def test_live_execution_guard_hardening_denies_grant() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    guard = packet["live_execution_guard_hardening_contract"]

    assert guard["controlled_live_execution_grant_denied"] is True
    assert guard["live_execution_activation_recorded_only"] is True
    assert guard["canon_execution_seal_projection_only"] is True
    assert guard["phase30_activation_authorized"] is False


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["hash_chain"]["phase29_gate_hash"] == EXPECTED_PHASE29_HASH
    assert workflow["hash_chain"]["phase30_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["live_execution_activation_authorization_review_gate_hash"] != ""


def test_gate_blocked_when_phase29_not_ready(tmp_path: Path) -> None:
    phase29 = _read_json(SOURCE_PHASE29_GATE_PATH)
    phase29["status"] = (
        "V2_HYGIENE_PHASE22_FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_GATE_BLOCKED"
    )
    phase29_path = _write_source(tmp_path, "phase29.json", phase29)
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(
        REPO_ROOT,
        source_phase29_gate_path=phase29_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_live_execution_activation_authorization_review"] is False
    assert (
        "phase29_final_operator_signoff_live_authority_fractal_numogram_gate_not_ready"
        in packet["source_blockers"]
    )


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["phase30_activation_authorized"] is False
    assert packet["phase31_activation_authorized"] is False
    assert packet["live_authority_authorized"] is False
    assert packet["fractal_numogram_runtime_authorized"] is False
    promotion = packet["live_execution_activation_authorization_review_promotion_contract"]
    assert promotion["execution_authority_granted"] is False
    assert promotion["phase30_activation_authorized"] is False


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    second = build_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(REPO_ROOT)
    assert (
        first["live_execution_activation_authorization_review_gate_hash"]
        == second["live_execution_activation_authorization_review_gate_hash"]
    )


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase23_live_execution_activation_authorization_review_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    second = run_v2_hygiene_phase23_live_execution_activation_authorization_review_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert (
        second["live_execution_activation_authorization_review_gate_hash"]
        == packet["live_execution_activation_authorization_review_gate_hash"]
    )
