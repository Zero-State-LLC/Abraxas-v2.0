from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealPlan.v1"
SOURCE_APPROVAL_RECORD_VALIDATION_DRY_RUN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_seal_plan_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_approval_record_seal_plan(
    *,
    repo_root: str | Path = ".",
    source_approval_record_validation_dry_run_path: str = SOURCE_APPROVAL_RECORD_VALIDATION_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_validation_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    validation_passed = False
    plan_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P92_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN"
    blockers: list[str] = []

    seal_construction_requirements = sorted([
        "approval_record_seal_plan_must_remain_advisory_only",
        "no_real_approval_record_creation_allowed",
        "no_real_approval_record_sealing_allowed",
    ])
    seal_provenance_requirements = sorted([
        "source_approval_record_validation_dry_run_hash_must_be_present",
        "source_approval_record_validation_dry_run_path_must_match_expected_lane_output",
        "source_approval_record_validation_dry_run_status_must_be_evaluated",
    ])
    seal_hash_requirements = sorted([
        "approval_record_seal_plan_hash_must_be_canonical",
        "canonical_json_sha256_source_hash_required",
        "sorted_key_serialization_required",
    ])
    seal_blocker_requirements = sorted([
        "missing_source_must_fail_closed",
        "non_ready_source_status_must_block",
        "validation_failed_source_must_block",
    ])
    seal_authority_invariant_requirements = sorted([
        "approval_granted_must_remain_false",
        "authorization_granted_must_remain_false",
        "execution_authority_must_remain_false",
        "token_minting_allowed_must_remain_false",
        "valid_for_execution_must_remain_false",
    ])

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_record_validation_dry_run_missing_or_unreadable",
            f"source_path:{source_approval_record_validation_dry_run_path}",
        ]
    else:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_status = str(source_payload.get("approval_record_validation_dry_run_status", "NOT_COMPUTABLE"))
        validation_passed = source_payload.get("validation_passed") is True

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        if source_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY":
            plan_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN"
            blockers = [f"source_approval_record_validation_dry_run_status:{source_status}"]
        elif not validation_passed:
            plan_status = "BLOCKED_BY_FAILED_APPROVAL_RECORD_VALIDATION_DRY_RUN"
            blockers = ["source_validation_passed:false"]
        else:
            plan_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY"
            recommended_next_lane = "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_plan_id": "temporal_continuity_operator_authorization_record_approval_record_seal_plan_001",
        "source_approval_record_validation_dry_run_path": source_approval_record_validation_dry_run_path,
        "source_approval_record_validation_dry_run_hash": source_hash,
        "approval_record_seal_plan_status": plan_status,
        "source_approval_record_validation_dry_run_status": source_status,
        "validation_passed": validation_passed,
        "seal_construction_requirements": seal_construction_requirements,
        "seal_provenance_requirements": seal_provenance_requirements,
        "seal_hash_requirements": seal_hash_requirements,
        "seal_blocker_requirements": seal_blocker_requirements,
        "seal_authority_invariant_requirements": seal_authority_invariant_requirements,
        "allowed_target_candidates": allowed_target_candidates,
        "denied_target_candidates": denied_target_candidates,
        "allowed_command_candidates": allowed_command_candidates,
        "denied_command_candidates": denied_command_candidates,
        "planned_authorization_scope": planned_authorization_scope,
        "planned_expected_outputs": planned_expected_outputs,
        "recommended_next_lane": recommended_next_lane,
        "blockers": sorted(blockers),
        "advisory_only": True,
        "projection_only": True,
        "approval_record_seal_plan_only": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
        "valid_for_execution": False,
        "source_approval_record_validation_dry_run_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
