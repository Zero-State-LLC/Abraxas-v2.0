from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_dumps
from core.temporal_continuity_selected_repair_execution_authorization_gate import (
    SOURCE_P102C_EXECUTION_PLAN_PATH,
    build_temporal_continuity_selected_repair_execution_authorization_gate,
    write_temporal_continuity_selected_repair_execution_authorization_gate,
)
from scripts import run_temporal_continuity_selected_repair_execution_authorization_gate

OUT_PATH = "out/temporal_continuity_selected_repair_execution_authorization_gate/latest.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _seed_p102c(
    root: Path,
    *,
    p102c_execution_plan_status: str = "SELECTED_REPAIR_EXECUTION_PLAN_READY",
    selected_branch_type: str = "P101_GATE_ONLY",
    selected_execution_plan_lane: str = "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN",
    recommended_next_lane: str = "P102D_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_GATE",
) -> None:
    _write_json(
        root / SOURCE_P102C_EXECUTION_PLAN_PATH,
        {
            "artifact_type": "TemporalContinuitySelectedRepairExecutionPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "repair_execution_authority": False,
            "regeneration_authority": False,
            "regeneration_execution_authority": False,
            "execution_authority": False,
            "authorization_granted": False,
            "source_p102b_router_path": "out/temporal_continuity_repair_execution_plan_router/latest.json",
            "p102c_execution_plan_status": p102c_execution_plan_status,
            "selected_branch_type": selected_branch_type,
            "selected_execution_plan_lane": selected_execution_plan_lane,
            "recommended_next_lane": recommended_next_lane,
            "degraded_evidence_inputs": ["a"],
            "inherited_blockers": ["b"],
            "inherited_drift_flags": ["c"],
            "semantic_overlap_flags": ["d"],
            "packet_hash": "f" * 64,
        },
    )


def test_missing_p102c_source_fails_closed_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    assert packet["p102d_authorization_gate_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_eligible"] is False
    assert packet["authorization_granted"] is False
    assert packet["recommended_next_lane"] == "P102C_SELECTED_REPAIR_EXECUTION_PLAN_REGENERATION"


def test_blocked_p102c_source_maps_to_authorization_blocked(tmp_path: Path) -> None:
    _seed_p102c(
        tmp_path,
        p102c_execution_plan_status="SELECTED_REPAIR_EXECUTION_PLAN_BLOCKED",
    )
    packet = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    assert (
        packet["p102d_authorization_gate_status"]
        == "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_BLOCKED"
    )
    assert packet["authorization_eligible"] is False
    assert packet["authorization_granted"] is False
    assert packet["recommended_next_lane"] == "P102C_SELECTED_REPAIR_EXECUTION_PLAN_REGENERATION"


def test_ready_p102c_source_is_eligible_but_not_granted(tmp_path: Path) -> None:
    _seed_p102c(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    assert (
        packet["p102d_authorization_gate_status"]
        == "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_ELIGIBLE"
    )
    assert packet["authorization_eligible"] is True
    assert packet["authorization_granted"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert (
        packet["recommended_next_lane"]
        == "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN"
    )


def test_determinism_repeated_builds_match_hash_and_payload(tmp_path: Path) -> None:
    _seed_p102c(tmp_path)
    first = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_hard_authority_locks_remain_false(tmp_path: Path) -> None:
    _seed_p102c(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "repair_execution_authority",
        "regeneration_authority",
        "regeneration_execution_authority",
        "execution_authority",
        "authorization_granted",
        "token_minting_allowed",
        "valid_for_execution",
    ):
        assert packet[field] is False
    assert packet["projection_only"] is True
    assert packet["audit_only"] is True
    assert packet["canonical_status"] == "ADVISORY_ONLY"


def test_recommended_next_lane_is_p102e_only_when_eligible(tmp_path: Path) -> None:
    _seed_p102c(
        tmp_path,
        p102c_execution_plan_status="SELECTED_REPAIR_EXECUTION_PLAN_BLOCKED",
    )
    blocked = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    _seed_p102c(tmp_path)
    ready = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    assert blocked["recommended_next_lane"] != "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN"
    assert (
        ready["recommended_next_lane"]
        == "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN"
    )


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p102c(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_gate(
        repo_root=tmp_path
    )
    out = tmp_path / "p102d_output.json"
    write_temporal_continuity_selected_repair_execution_authorization_gate(out, packet)
    text = out.read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert text.endswith("\n")
    assert text == canonical_dumps(parsed) + "\n"


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p102c(tmp_path)
    packet = run_temporal_continuity_selected_repair_execution_authorization_gate.run(
        repo_root=tmp_path
    )
    expected = tmp_path / OUT_PATH
    assert expected.exists()
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert (
        content["artifact_type"]
        == "TemporalContinuitySelectedRepairExecutionAuthorizationGate.v1"
    )
    assert content["packet_hash"] == packet["packet_hash"]
