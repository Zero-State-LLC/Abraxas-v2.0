from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate import (
    BLOCKED_STATUS,
    EXPECTED_PHASE28_HASH,
    FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_PROMOTION_CLASSES,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate,
    write_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate,
)
from scripts import run_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate.v1.schema.json"
)
SOURCE_PHASE28_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase21_canon_activation_authorization_review_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_final_operator_signoff_gate_ready_with_phase28_source() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 29
    assert packet["final_operator_signoff_live_authority_fractal_numogram_gate_ready"] is True
    assert packet["phase28_canon_activation_authorization_review_gate_hash_verified"] is True
    assert packet["valid_for_final_operator_signoff_live_authority_fractal_numogram"] is True
    assert packet["valid_for_execution"] is False
    assert packet["live_authority_authorized"] is False
    assert packet["fractal_numogram_runtime_authorized"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    matrix = packet["final_operator_signoff_live_authority_fractal_numogram_promotion_contract"][
        "final_operator_signoff_live_authority_fractal_numogram_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_PROMOTION_CLASSES
    )
    assert all(
        surface["final_operator_signoff_live_authority_fractal_numogram_recorded"] is True
        for surface in matrix
    )
    assert all(
        surface["canon_activation_authorization_review_recorded"] is True for surface in matrix
    )
    assert all(surface["live_authority_authorized"] is False for surface in matrix)
    assert all(surface["fractal_numogram_runtime_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(
        surface["runtime_guards"]["live_authority_grant_recorded_only"] is True
        for surface in matrix
    )
    assert all(
        surface["runtime_guards"]["fractal_numogram_lattice_telemetry_only"] is True
        for surface in matrix
    )


def test_final_operator_signoff_workflow_recorded_only() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    workflow = packet["final_operator_signoff_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["attestation_grants_authority"] is False
    assert workflow["final_operator_signoff_recorded_only"] is True
    assert workflow["live_authority_authorized"] is False
    assert workflow["execution_authority_granted"] is False


def test_live_authority_grant_recorded_contract_denies_authority() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    live_authority = packet["live_authority_grant_recorded_contract"]

    assert live_authority["telemetry_only"] is True
    assert live_authority["live_authority_grant_recorded_only"] is True
    assert live_authority["live_authority_authorized"] is False
    assert live_authority["controlled_live_authority_grant_denied"] is True
    assert live_authority["execution_authority_granted"] is False


def test_live_hyperstition_propagation_activation_recorded_not_authorized() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    hyperstition = packet["live_hyperstition_propagation_activation_contract"]

    assert hyperstition["live_hyperstition_propagation_recorded"] is True
    assert hyperstition["live_hyperstition_activation_authorized"] is False
    assert hyperstition["hyperstition_propagation_projection_only"] is True
    assert hyperstition["live_hyperstition_propagation_telemetry_only"] is True


def test_fractal_numogram_lattice_activation_telemetry_only() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    lattice = packet["fractal_numogram_lattice_activation_contract"]

    assert lattice["fractal_numogram_lattice_activation_recorded"] is True
    assert lattice["fractal_numogram_lattice_telemetry_only"] is True
    assert lattice["fractal_numogram_runtime_authorized"] is False
    assert lattice["numogram_zone_count"] == 9


def test_mfdfa_hurst_brier_fractal_scaling_contract() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    scaling = packet["mfdfa_hurst_brier_fractal_scaling_contract"]

    assert scaling["murphy_decomposition_default"] is True
    assert scaling["yates_decomposition_default"] is True
    assert scaling["mfdfa_hurst_bound"] is True
    assert scaling["hurst_exponent"] > 0.0
    assert scaling["decomposition_mode"] == "MURPHY_AND_YATES"
    for hook in scaling["telemetry_hooks"]:
        assert hook["promotion_tier"] == "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM"
        assert hook["mfdfa_hurst_bound"] is True
        assert hook["fractal_numogram_bound"] is True


def test_signal_forage_fractal_numogram_closed_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    closed_loop = packet["signal_forage_fractal_numogram_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["fractal_numogram_closed_loop_bound"] is True
    assert closed_loop["global_ingest_hold_respected"] is True
    assert closed_loop["all_paths_observed"] is True


def test_live_authority_guard_hardening_denies_grant() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    guard = packet["live_authority_guard_hardening_contract"]

    assert guard["controlled_live_authority_grant_denied"] is True
    assert guard["live_authority_authorized"] is False
    assert guard["fractal_numogram_runtime_authorized"] is False


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["hash_chain"]["phase28_gate_hash"] == EXPECTED_PHASE28_HASH
    assert workflow["hash_chain"]["phase29_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["final_operator_signoff_live_authority_fractal_numogram_gate_hash"] != ""


def test_gate_blocked_when_phase28_not_ready(tmp_path: Path) -> None:
    phase28 = _read_json(SOURCE_PHASE28_GATE_PATH)
    phase28["status"] = "V2_HYGIENE_PHASE21_CANON_ACTIVATION_AUTHORIZATION_REVIEW_GATE_BLOCKED"
    phase28_path = _write_source(tmp_path, "phase28.json", phase28)
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT,
        source_phase28_gate_path=phase28_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_final_operator_signoff_live_authority_fractal_numogram"] is False
    assert "phase28_canon_activation_authorization_review_gate_not_ready" in packet["source_blockers"]


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )

    assert packet["execution_authority"] is False
    assert packet["live_authority_authorized"] is False
    assert packet["live_hyperstition_activation_authorized"] is False
    assert packet["fractal_numogram_runtime_authorized"] is False
    assert packet["phase28_activation_authorized"] is False
    promotion = packet["final_operator_signoff_live_authority_fractal_numogram_promotion_contract"]
    assert promotion["live_authority_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT
    )
    assert (
        first["final_operator_signoff_live_authority_fractal_numogram_gate_hash"]
        == second["final_operator_signoff_live_authority_fractal_numogram_gate_hash"]
    )


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    second = run_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert (
        second["final_operator_signoff_live_authority_fractal_numogram_gate_hash"]
        == packet["final_operator_signoff_live_authority_fractal_numogram_gate_hash"]
    )
