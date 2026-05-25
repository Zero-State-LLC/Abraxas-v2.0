from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_spine_binder_contract import (
    RECOMMENDED_BINDER_LANE,
    RECOMMENDED_P69_REPAIR_LANE,
    RECOMMENDED_REPAIR_INDEX_LANE,
    build_temporal_continuity_spine_binder_contract,
    write_temporal_continuity_spine_binder_contract,
)
from scripts import run_temporal_continuity_spine_binder_contract


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _seed_precheck(
    root: Path,
    *,
    recommended_next_lane: str = RECOMMENDED_BINDER_LANE,
    blockers: list[str] | None = None,
    missing_or_not_computable_inputs: list[str] | None = None,
    semantic_overlap_flags: list[str] | None = None,
) -> None:
    _write_json(
        root / "out" / "temporal_continuity_spine_precheck" / "latest.json",
        {
            "artifact_type": "TemporalContinuitySpinePrecheck.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "recommended_next_lane": recommended_next_lane,
            "continuity_surface_groups": [
                {"group_id": "z_group", "status": "READY"},
                {"group_id": "a_group", "status": "DEGRADED"},
            ],
            "binder_candidate_inputs": [
                "out/audit/input_b.latest.json",
                "out/audit/input_a.latest.json",
            ],
            "missing_or_not_computable_inputs": missing_or_not_computable_inputs or [],
            "semantic_overlap_flags": semantic_overlap_flags
            or [
                "SEMANTIC_OVERLAP_STABILITY_RECEIPT:z|a",
                "SEMANTIC_OVERLAP_CLOSURE_RECEIPT:b|a",
            ],
            "blockers": blockers or [],
            "drift_flags": ["GROUP_ARCHIVE_CHAIN_DEGRADED"],
        },
    )


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_precheck(tmp_path)
    first = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    second = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert first["packet_hash"] == second["packet_hash"]


def test_output_latest_json_has_exactly_one_newline(tmp_path: Path) -> None:
    _seed_precheck(tmp_path)
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_spine_binder_contract" / "latest.json"
    write_temporal_continuity_spine_binder_contract(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_missing_precheck_is_not_computable(tmp_path: Path) -> None:
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert packet["source_precheck_observed"] is False
    assert packet["source_precheck_hash"] == "NOT_COMPUTABLE"
    assert packet["binder_contract_status"] == "NOT_COMPUTABLE"
    assert packet["next_allowed_lanes"] == [RECOMMENDED_P69_REPAIR_LANE]


def test_malformed_precheck_is_not_computable(tmp_path: Path) -> None:
    precheck_path = tmp_path / "out" / "temporal_continuity_spine_precheck" / "latest.json"
    precheck_path.parent.mkdir(parents=True, exist_ok=True)
    precheck_path.write_text("{not_json", encoding="utf-8")
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert packet["source_precheck_observed"] is True
    assert packet["source_precheck_hash"] == "NOT_COMPUTABLE"
    assert packet["binder_contract_status"] == "NOT_COMPUTABLE"
    assert packet["next_allowed_lanes"] == [RECOMMENDED_P69_REPAIR_LANE]


def test_governance_denial_flags_locked_false(tmp_path: Path) -> None:
    _seed_precheck(tmp_path)
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    for field in (
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
        "forecast_influence",
        "production_activation",
        "canon_promotion",
    ):
        assert packet[field] is False


def test_repair_recommendation_blocks_contract(tmp_path: Path) -> None:
    _seed_precheck(tmp_path, recommended_next_lane=RECOMMENDED_REPAIR_INDEX_LANE)
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert packet["binder_contract_status"] == "BLOCKED"
    assert packet["next_allowed_lanes"] == [RECOMMENDED_REPAIR_INDEX_LANE]


def test_binder_recommendation_without_degradation_is_ready(tmp_path: Path) -> None:
    _seed_precheck(
        tmp_path,
        recommended_next_lane=RECOMMENDED_BINDER_LANE,
        blockers=[],
        missing_or_not_computable_inputs=[],
    )
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert packet["binder_contract_status"] == "CONTRACT_READY"
    assert packet["next_allowed_lanes"] == [RECOMMENDED_BINDER_LANE]


def test_degraded_evidence_preserved_verbatim(tmp_path: Path) -> None:
    degraded_marker = (
        "archive_chain:degraded:out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json:CLOSURE_RECEIPT_DEGRADED"
    )
    _seed_precheck(tmp_path, blockers=[degraded_marker, "temporal_coherence_chain:missing:out/audit/missing.json"])
    packet = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert packet["binder_contract_status"] == "CONTRACT_READY_WITH_DEGRADED_EVIDENCE"
    assert packet["degraded_inputs"] == [degraded_marker]
    assert degraded_marker in packet["blockers"]


def test_semantic_overlap_flags_sorted_deterministic(tmp_path: Path) -> None:
    _seed_precheck(
        tmp_path,
        semantic_overlap_flags=[
            "SEMANTIC_OVERLAP_STABILITY_RECEIPT:z|a",
            "SEMANTIC_OVERLAP_CLOSURE_RECEIPT:b|a",
        ],
    )
    first = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    second = build_temporal_continuity_spine_binder_contract(repo_root=tmp_path)
    assert first["semantic_overlap_flags"] == sorted(first["semantic_overlap_flags"])
    assert first["semantic_overlap_flags"] == second["semantic_overlap_flags"]


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_precheck(tmp_path)
    out_path = tmp_path / "out" / "temporal_continuity_spine_binder_contract" / "latest.json"
    first = run_temporal_continuity_spine_binder_contract.run(repo_root=tmp_path, out_path=out_path)
    first_text = out_path.read_text(encoding="utf-8")
    second = run_temporal_continuity_spine_binder_contract.run(repo_root=tmp_path, out_path=out_path)
    second_text = out_path.read_text(encoding="utf-8")
    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_schema_contains_required_authority_denial_fields() -> None:
    schema = json.loads(
        Path("contracts/canon/temporal_continuity_spine_binder_contract.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    required = set(schema["required"])
    assert {
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "spine_implementation_authority",
    }.issubset(required)


def test_schema_locks_mutation_and_authority_flags_false() -> None:
    schema = json.loads(
        Path("contracts/canon/temporal_continuity_spine_binder_contract.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for field in (
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "repair_authority",
        "spine_implementation_authority",
    ):
        assert schema["properties"][field]["const"] is False
