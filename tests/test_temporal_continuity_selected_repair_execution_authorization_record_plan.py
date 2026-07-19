from __future__ import annotations

import json
from pathlib import Path


from core.canonical.json import canonical_dumps
from core.temporal_continuity_selected_repair_execution_authorization_record_plan import (
    SOURCE_P102D_AUTHORIZATION_GATE_PATH,
    build_temporal_continuity_selected_repair_execution_authorization_record_plan,
    write_temporal_continuity_selected_repair_execution_authorization_record_plan,
)
from scripts.temporal import run_temporal_continuity_selected_repair_execution_authorization_record_plan

OUT_PATH = "out/temporal_continuity_selected_repair_execution_authorization_record_plan/latest.json"
SCHEMA_PATH = (
    "contracts/canon/temporal_continuity_selected_repair_execution_authorization_record_plan.v1.schema.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(payload) + "\n", encoding="utf-8")


def _seed_p102d(
    root: Path,
    *,
    status: str = "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_ELIGIBLE",
    authorization_eligible: bool = True,
    authorization_granted: bool = False,
    token_minting_allowed: bool = False,
    valid_for_execution: bool = False,
    execution_authority: bool = False,
) -> None:
    _write_json(
        root / SOURCE_P102D_AUTHORIZATION_GATE_PATH,
        {
            "artifact_type": "TemporalContinuitySelectedRepairExecutionAuthorizationGate.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "p102d_authorization_gate_status": status,
            "authorization_eligible": authorization_eligible,
            "authorization_granted": authorization_granted,
            "token_minting_allowed": token_minting_allowed,
            "valid_for_execution": valid_for_execution,
            "execution_authority": execution_authority,
            "recommended_next_lane": "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN",
            "degraded_evidence_inputs": ["d"],
            "inherited_blockers": ["b"],
            "inherited_drift_flags": ["f"],
            "semantic_overlap_flags": ["s"],
            "packet_hash": "f" * 64,
        },
    )


def test_missing_p102d_source_fails_closed_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    assert packet["p102e_record_plan_status"] == "NOT_COMPUTABLE"
    assert packet["authorization_record_required"] is False
    assert packet["authorization_record_created"] is False
    assert packet["recommended_next_lane"] == "P102D_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_GATE_REGENERATION"
    assert packet["missing_evidence"] == [SOURCE_P102D_AUTHORIZATION_GATE_PATH]


def test_eligible_p102d_plans_record_without_creating_or_granting(tmp_path: Path) -> None:
    _seed_p102d(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    assert (
        packet["p102e_record_plan_status"]
        == "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN_READY"
    )
    assert packet["authorization_record_required"] is True
    assert packet["authorization_record_created"] is False
    assert packet["authorization_granted"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["recommended_next_lane"] == "OPERATOR_AUTHORIZATION_RECORD_DECISION_REQUIRED"


def test_source_authority_drift_denies_record_plan(tmp_path: Path) -> None:
    _seed_p102d(tmp_path, authorization_granted=True)
    packet = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    assert (
        packet["p102e_record_plan_status"]
        == "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN_DENIED"
    )
    assert packet["authorization_record_required"] is False
    assert packet["recommended_next_lane"] == "P102D_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_GATE_REGENERATION"


def test_hard_authority_locks_remain_false(tmp_path: Path) -> None:
    _seed_p102d(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
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
        "authorization_authority",
        "authorization_record_creation_authority",
        "authorization_record_created",
        "authorization_granted",
        "token_minting_allowed",
        "token_minting_authority",
        "valid_for_execution",
    ):
        assert packet[field] is False
    assert packet["canonical_status"] == "ADVISORY_ONLY"
    assert packet["audit_only"] is True
    assert packet["projection_only"] is True


def test_determinism_repeated_builds_match(tmp_path: Path) -> None:
    _seed_p102d(tmp_path)
    first = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_required_fields_match_generated_packet(tmp_path: Path) -> None:
    _seed_p102d(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    schema = json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(packet)


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p102d(tmp_path)
    packet = build_temporal_continuity_selected_repair_execution_authorization_record_plan(
        repo_root=tmp_path
    )
    out = tmp_path / "p102e_output.json"
    write_temporal_continuity_selected_repair_execution_authorization_record_plan(out, packet)
    text = out.read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert text.endswith("\n")
    assert text == canonical_dumps(parsed) + "\n"


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p102d(tmp_path)
    packet = run_temporal_continuity_selected_repair_execution_authorization_record_plan.run(
        repo_root=tmp_path
    )
    expected = tmp_path / OUT_PATH
    assert expected.exists()
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert content["artifact_type"] == "TemporalContinuitySelectedRepairExecutionAuthorizationRecordPlan.v1"
    assert content["packet_hash"] == packet["packet_hash"]
