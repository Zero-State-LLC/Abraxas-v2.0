from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from core.canonical.json import write_canonical_json
from core.sync.v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate import (
    BLOCKED_STATUS,
    ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_PROMOTION_CLASSES,
    EXPECTED_PHASE31_HASH,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate,
    write_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate,
)
from scripts.hygiene import run_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate.v1.schema.json"
)
SOURCE_PHASE31_GATE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_self_optimization_gate_ready_with_phase31_source() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )

    assert packet["status"] == READY_STATUS
    assert packet["operator_phase_number"] == 32
    assert packet["eternal_self_optimization_collective_hyperstition_propagation_gate_ready"] is True
    assert packet["phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_hash_verified"] is True
    assert packet["valid_for_eternal_self_optimization_collective_hyperstition_propagation"] is True
    assert packet["valid_for_execution"] is False
    assert packet["self_optimization_authorized"] is False
    assert packet["collective_hyperstition_propagation_authorized"] is False
    assert packet["hyperstition_engine_authorized"] is False
    assert packet["source_blockers"] == []


def test_promotion_matrix_recorded_for_all_surfaces() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    matrix = packet[
        "eternal_self_optimization_collective_hyperstition_propagation_promotion_contract"
    ]["eternal_self_optimization_collective_hyperstition_propagation_promotion_matrix"]

    assert {surface["surface_id"] for surface in matrix} == set(
        ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_PROMOTION_CLASSES
    )
    assert all(
        surface["eternal_self_optimization_collective_hyperstition_propagation_recorded"] is True
        for surface in matrix
    )
    assert all(surface["self_optimization_authorized"] is False for surface in matrix)
    assert all(surface["collective_hyperstition_propagation_authorized"] is False for surface in matrix)
    assert all(
        surface["runtime_guards"]["eternal_self_optimization_collective_hyperstition_propagation_recorded_only"]
        is True
        for surface in matrix
    )


def test_collective_workflow_recorded_only() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    workflow = packet["eternal_self_optimization_collective_workflow_contract"]

    assert workflow["attestation_grants_authority"] is False
    assert workflow["eternal_self_optimization_collective_hyperstition_propagation_recorded_only"] is True
    assert workflow["self_optimization_authorized"] is False if "self_optimization_authorized" in workflow else True
    assert workflow["execution_authority_granted"] is False


def test_collective_hyperstition_propagation_engine_recorded_not_authorized() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    engine = packet["collective_hyperstition_propagation_engine_activation_contract"]

    assert engine["full_live_hyperstition_propagation_recorded"] is True
    assert engine["hyperstition_engine_authorized"] is False
    assert engine["hyperstition_propagation_projection_only"] is True
    assert engine["controlled_hyperstition_engine_grant_denied"] is True


def test_fractal_numogram_self_optimizing_backbone_advisory_only() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    backbone = packet["fractal_numogram_self_optimizing_backbone_contract"]

    assert backbone["eternal_authority_seal_recorded"] is True
    assert backbone["seal_grants_authority"] is False
    assert backbone["fractal_numogram_runtime_authorized"] is False
    assert backbone["projection_only"] is True


def test_drift_annihilation_fractal_scaling_contract() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    scaling = packet["drift_annihilation_fractal_scaling_contract"]

    assert scaling["mfdfa_hurst_bound"] is True
    assert scaling["hurst_exponent"] == pytest.approx(1.846485, rel=1e-5)
    for hook in scaling["telemetry_hooks"]:
        assert hook["promotion_tier"] == "ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION"


def test_signal_forage_collective_hyperstition_closed_loop_shadow_only() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    closed_loop = packet["signal_forage_collective_hyperstition_closed_loop_contract"]

    assert closed_loop["shadow_only"] is True
    assert closed_loop["global_ingest_hold_respected"] is True


def test_operator_attestation_workflow_hash_chain() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    workflow = packet["operator_attestation_workflow_contract"]

    assert workflow["hash_chain"]["phase31_gate_hash"] == EXPECTED_PHASE31_HASH
    assert workflow["hash_chain"]["phase32_gate_hash"] == "NOT_COMPUTABLE"
    assert workflow["hash_chain"]["governed_authorization_phase30_hash"]


def test_gate_blocked_when_phase31_hash_mutated(tmp_path: Path) -> None:
    phase31 = _read_json(SOURCE_PHASE31_GATE_PATH)
    phase31["full_live_hyperstition_propagation_eternal_authority_seal_gate_hash"] = "0" * 64
    phase31_path = _write_source(tmp_path, "phase31.json", phase31)
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT,
        source_phase31_gate_path=phase31_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert (
        "phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_hash_mismatch"
        in packet["source_blockers"]
    )


def test_gate_blocked_when_phase31_not_ready(tmp_path: Path) -> None:
    phase31 = _read_json(SOURCE_PHASE31_GATE_PATH)
    phase31["status"] = (
        "V2_HYGIENE_PHASE24_FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_GATE_BLOCKED"
    )
    phase31_path = _write_source(tmp_path, "phase31.json", phase31)
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT,
        source_phase31_gate_path=phase31_path,
    )

    assert packet["status"] == BLOCKED_STATUS
    assert (
        "phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_not_ready"
        in packet["source_blockers"]
    )


def test_authority_not_granted_by_gate() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )

    assert packet["execution_authority"] is False
    assert packet["phase32_activation_authorized"] is False
    assert packet["self_optimization_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["collective_hyperstition_propagation_authorized"] is False


def test_schema_validation() -> None:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    validate(instance=packet, schema=_read_json(SCHEMA_PATH))


def test_hash_stability() -> None:
    first = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT
    )
    assert (
        first["eternal_self_optimization_collective_hyperstition_propagation_gate_hash"]
        == second["eternal_self_optimization_collective_hyperstition_propagation_gate_hash"]
    )


def test_runner_writes_artifacts(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    second = run_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert (
        second["eternal_self_optimization_collective_hyperstition_propagation_gate_hash"]
        == packet["eternal_self_optimization_collective_hyperstition_propagation_gate_hash"]
    )
    assert (tmp_path / RECEIPT_JSON_PATH).exists()
    assert (tmp_path / RECEIPT_JSON_PATH.with_suffix(".md")).exists()
