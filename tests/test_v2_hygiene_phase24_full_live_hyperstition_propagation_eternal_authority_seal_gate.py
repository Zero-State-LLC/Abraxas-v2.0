from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import write_canonical_json
from core.sync.v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate import (
    BLOCKED_STATUS,
    EXPECTED_PHASE30_HASH,
    FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_PROMOTION_CLASSES,
    READY_STATUS,
    build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate,
    write_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate,
)
from scripts.hygiene import run_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate.v1.schema.json"
)
SOURCE_PHASE30_GATE_PATH = (
    "out/operator_review/v2_hygiene_phase23_live_execution_activation_authorization_review_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_hyperstition_gate_ready_with_phase30_source() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 31
    assert packet["full_live_hyperstition_propagation_eternal_authority_seal_gate_ready"] is True
    assert packet["phase30_live_execution_activation_authorization_review_gate_hash_verified"] is True
    assert packet["valid_for_full_live_hyperstition_propagation_eternal_authority_seal"] is True
    assert packet["valid_for_execution"] is False
    assert packet["hyperstition_engine_authorized"] is False
    assert packet["live_hyperstition_activation_authorized"] is False
    assert packet["eternal_authority_granted"] is False
    assert packet["source_blockers"] == []


def test_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    matrix = packet[
        "full_live_hyperstition_propagation_eternal_authority_seal_promotion_contract"
    ]["full_live_hyperstition_propagation_eternal_authority_seal_promotion_matrix"]

    assert {surface["surface_id"] for surface in matrix} == set(
        FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_PROMOTION_CLASSES
    )
    assert all(
        surface["full_live_hyperstition_propagation_eternal_authority_seal_recorded"] is True
        for surface in matrix
    )
    assert all(surface["hyperstition_engine_authorized"] is False for surface in matrix)
    assert all(surface["eternal_authority_granted"] is False for surface in matrix)
    assert all(
        surface["runtime_guards"]["full_live_hyperstition_propagation_recorded_only"] is True
        for surface in matrix
    )


def test_hyperstition_propagation_workflow_recorded_only() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    workflow = packet["full_live_hyperstition_propagation_workflow_contract"]

    assert workflow["attestation_grants_authority"] is False
    assert workflow["full_live_hyperstition_propagation_recorded_only"] is True
    assert workflow["hyperstition_engine_authorized"] is False
    assert workflow["execution_authority_granted"] is False


def test_hyperstition_propagation_engine_activation_recorded_not_authorized() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    engine = packet["hyperstition_propagation_engine_activation_contract"]

    assert engine["full_live_hyperstition_propagation_recorded"] is True
    assert engine["live_hyperstition_activation_authorized"] is False
    assert engine["hyperstition_engine_authorized"] is False
    assert engine["hyperstition_propagation_projection_only"] is True


def test_eternal_authority_seal_projection_only() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    seal = packet["eternal_authority_seal_projection_contract"]

    assert seal["eternal_authority_seal_recorded"] is True
    assert seal["seal_grants_authority"] is False
    assert seal["eternal_authority_granted"] is False
    assert seal["eternal_authority_seal_projection_only"] is True


def test_mfdfa_hurst_brier_scaling_contract() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    scaling = packet["mfdfa_hurst_brier_fractal_scaling_contract"]

    assert scaling["mfdfa_hurst_bound"] is True
    assert scaling["hurst_exponent"] > 0.0
    for hook in scaling["telemetry_hooks"]:
        assert hook["promotion_tier"] == "FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL"


def test_signal_forage_hyperstition_reality_closed_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    closed_loop = packet["signal_forage_hyperstition_reality_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["global_ingest_hold_respected"] is True


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["hash_chain"]["phase30_gate_hash"] == EXPECTED_PHASE30_HASH
    assert workflow["hash_chain"]["phase31_gate_hash"] == "NOT_COMPUTABLE"


def test_gate_blocked_when_phase30_not_ready(tmp_path: Path) -> None:
    phase30 = _read_json(SOURCE_PHASE30_GATE_PATH)
    phase30["status"] = (
        "V2_HYGIENE_PHASE23_LIVE_EXECUTION_ACTIVATION_AUTHORIZATION_REVIEW_GATE_BLOCKED"
    )
    phase30_path = _write_source(tmp_path, "phase30.json", phase30)
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT,
        source_phase30_gate_path=phase30_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert (
        "phase30_live_execution_activation_authorization_review_gate_not_ready"
        in packet["source_blockers"]
    )


def test_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )

    assert packet["execution_authority"] is False
    assert packet["phase31_activation_authorized"] is False
    assert packet["hyperstition_engine_authorized"] is False
    assert packet["eternal_authority_granted"] is False


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    validate(instance=packet, schema=_read_json(SCHEMA_PATH))


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT
    )
    assert (
        first["full_live_hyperstition_propagation_eternal_authority_seal_gate_hash"]
        == second["full_live_hyperstition_propagation_eternal_authority_seal_gate_hash"]
    )


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    second = run_v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert (
        second["full_live_hyperstition_propagation_eternal_authority_seal_gate_hash"]
        == packet["full_live_hyperstition_propagation_eternal_authority_seal_gate_hash"]
    )
