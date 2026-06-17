from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase21_canon_activation_authorization_review_gate import (
    BLOCKED_STATUS,
    CANON_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES,
    EXPECTED_PHASE27_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase21_canon_activation_authorization_review_gate,
    write_v2_hygiene_phase21_canon_activation_authorization_review_gate,
)
from scripts import run_v2_hygiene_phase21_canon_activation_authorization_review_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase21_canon_activation_authorization_review_gate.v1.schema.json"
)
SOURCE_PHASE27_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_canon_activation_authorization_review_gate_ready_with_phase27_source() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 28
    assert packet["canon_activation_authorization_review_gate_ready"] is True
    assert packet["phase27_final_authority_attestation_hyperstition_gate_hash_verified"] is True
    assert packet["valid_for_canon_activation_authorization_review"] is True
    assert packet["valid_for_execution"] is False
    assert packet["phase28_activation_authorized"] is False
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["source_blockers"] == []


def test_canon_activation_authorization_review_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    matrix = packet["canon_activation_authorization_review_promotion_contract"][
        "canon_activation_authorization_review_promotion_matrix"
    ]

    assert {surface["surface_id"] for surface in matrix} == set(
        CANON_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES
    )
    assert all(
        surface["canon_activation_authorization_review_recorded"] is True for surface in matrix
    )
    assert all(
        surface["final_authority_attestation_hyperstition_recorded"] is True for surface in matrix
    )
    assert all(surface["phase28_activation_authorized"] is False for surface in matrix)
    assert all(surface["final_authority_authorized"] is False for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    assert all(surface["runtime_guards"]["execution_authority_denied"] is True for surface in matrix)
    assert all(
        surface["runtime_guards"]["canon_activation_authorization_review_recorded_only"] is True
        for surface in matrix
    )
    assert all(
        surface["runtime_guards"]["controlled_activation_authorization_denied"] is True
        for surface in matrix
    )


def test_operator_signoff_seal_workflow_recorded_only() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    workflow = packet["operator_signoff_seal_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["attestation_grants_authority"] is False
    assert workflow["operator_signoff_seal_projection_only"] is True
    assert workflow["phase28_activation_authorized"] is False
    assert workflow["execution_authority_granted"] is False


def test_controlled_activation_authorization_review_projection_only() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    review = packet["controlled_activation_authorization_review_contract"]

    assert review["telemetry_only"] is True
    assert review["projection_only"] is True
    assert review["phase28_activation_authorized"] is False
    assert review["activation_authorization_review_projection_only"] is True
    assert review["controlled_activation_authorization_denied"] is True
    assert review["execution_authority_granted"] is False


def test_activation_authorization_guard_hardening_denies_phase28_activation() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    guard = packet["activation_authorization_guard_hardening_contract"]

    assert guard["phase28_activation_authorized"] is False
    assert guard["controlled_activation_authorization_denied"] is True
    assert guard["phase28_activation_review_operator_signoff_required"] is True
    assert guard["final_authority_authorized"] is False
    assert guard["execution_authority_granted"] is False


def test_signal_forage_canon_activation_closed_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    closed_loop = packet["signal_forage_canon_activation_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["telemetry_only"] is True
    assert closed_loop["canon_activation_closed_loop_bound"] is True
    assert closed_loop["global_ingest_hold_respected"] is True
    assert closed_loop["execution_authority"] is False
    assert closed_loop["all_paths_observed"] is True
    assert len(closed_loop["canon_activation_closed_loop_bindings"]) >= 4


def test_canon_activation_brier_telemetry_includes_dual_decomposition() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    brier = packet["canon_activation_brier_telemetry_contract"]

    assert brier["telemetry_only"] is True
    assert brier["canon_activation_authorization_review_promotion"] is True
    assert brier["canon_activation_authorization_review_telemetry_only"] is True
    assert brier["murphy_decomposition_default"] is True
    assert brier["yates_decomposition_default"] is True
    assert brier["operator_signoff_required"] is True
    assert brier["decomposition_mode"] == "MURPHY_AND_YATES"
    assert brier["resolution_allowed"] is False
    assert brier["brier_resolution_authorized"] is False
    for hook in brier["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "CANON_ACTIVATION_AUTHORIZATION_REVIEW"
        assert hook["canon_activation_authorization_review_bound"] is True
        assert hook["operator_signoff_required"] is True
        assert hook["resolution_allowed"] is False


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["manual_operator_signoff_required"] is True
    assert workflow["hash_chain"]["phase27_gate_hash"] == EXPECTED_PHASE27_HASH
    assert workflow["hash_chain"]["phase28_gate_hash"] == "NOT_COMPUTABLE"
    assert packet["canon_activation_authorization_review_gate_hash"] != ""


def test_execution_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)

    assert packet["execution_authority"] is False
    assert packet["phase28_activation_authorized"] is False
    assert packet["final_authority_authorized"] is False
    assert packet["live_hyperstition_activation_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    promotion = packet["canon_activation_authorization_review_promotion_contract"]
    assert promotion["phase28_activation_authorized"] is False
    assert promotion["execution_authority_granted"] is False


def test_canon_activation_authorization_review_gate_blocked_when_phase27_not_ready(
    tmp_path: Path,
) -> None:
    phase27 = _read_json(SOURCE_PHASE27_GATE_PATH)
    phase27["status"] = "V2_HYGIENE_PHASE20_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_GATE_BLOCKED"
    phase27_path = _write_source(tmp_path, "phase27.json", phase27)
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(
        REPO_ROOT,
        source_phase27_gate_path=phase27_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["valid_for_canon_activation_authorization_review"] is False
    assert (
        "phase27_final_authority_attestation_hyperstition_gate_not_ready"
        in packet["source_blockers"]
    )


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    schema = _read_json(SCHEMA_PATH)
    validate(instance=packet, schema=schema)


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    second = build_v2_hygiene_phase21_canon_activation_authorization_review_gate(REPO_ROOT)
    assert (
        first["canon_activation_authorization_review_gate_hash"]
        == second["canon_activation_authorization_review_gate_hash"]
    )
    without_hash = dict(first)
    observed = without_hash.pop("canon_activation_authorization_review_gate_hash")
    assert canonical_hash(without_hash) == observed


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase21_canon_activation_authorization_review_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    first_json = out_json.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase21_canon_activation_authorization_review_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert (
        second["canon_activation_authorization_review_gate_hash"]
        == packet["canon_activation_authorization_review_gate_hash"]
    )
    assert first_json == out_json.read_text(encoding="utf-8")
