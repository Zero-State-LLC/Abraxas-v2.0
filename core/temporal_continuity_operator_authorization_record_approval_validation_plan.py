from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalValidationPlan.v1"
SOURCE_APPROVAL_DRY_RUN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_dry_run/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_validation_plan_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_approval_validation_plan(
    *,
    repo_root: str | Path = ".",
    source_approval_dry_run_path: str = SOURCE_APPROVAL_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_approval_dry_run_hash = "NOT_COMPUTABLE"
    source_approval_dry_run_status = "NOT_COMPUTABLE"
    status = "NOT_COMPUTABLE"
    recommended_next_lane = "P86_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN"
    blockers: list[str] = []

    approval_invariant_validation_requirements = [
        "advisory_only_must_be_true",
        "projection_only_must_be_true",
        "approval_dry_run_only_must_be_true",
        "approval_granted_must_be_false",
        "authorization_granted_must_be_false",
        "execution_authority_must_be_false",
        "authorization_authority_must_be_false",
        "authorization_record_creation_authority_must_be_false",
        "token_minting_allowed_must_be_false",
        "valid_for_execution_must_be_false",
    ]
    operator_acknowledgement_validation_requirements = [
        "operator_acknowledgement_entries_must_exist",
        "operator_acknowledgements_must_be_simulated",
        "operator_acknowledgements_must_not_grant_authority",
    ]
    approval_constraint_validation_requirements = [
        "constraint_evaluation_entries_must_exist",
        "constraint_evaluation_must_be_simulated_only",
        "constraint_evaluation_must_not_enable_execution",
    ]
    approval_provenance_validation_requirements = [
        "source_approval_dry_run_path_must_match",
        "source_approval_dry_run_hash_must_match",
        "source_approval_plan_path_must_be_present",
        "source_approval_dry_run_status_must_be_present",
    ]
    approval_hash_validation_requirements = [
        "approval_dry_run_hash_must_be_present",
        "canonical_json_sha256_source_hash_required",
        "approval_validation_plan_hash_must_match",
    ]
    approval_blocker_validation_requirements = [
        "blockers_must_be_empty_when_ready",
        "blockers_must_reference_source_when_blocked",
        "blockers_must_not_be_suppressed",
    ]

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_dry_run_missing_or_unreadable",
            f"source_path:{source_approval_dry_run_path}",
        ]
    else:
        source_approval_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_approval_dry_run_status = str(source_payload.get("approval_dry_run_status", "NOT_COMPUTABLE"))

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        if source_approval_dry_run_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN_READY":
            status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN"
            blockers = [f"source_approval_dry_run_status:{source_approval_dry_run_status}"]
        else:
            status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN_READY"
            recommended_next_lane = (
                "P88_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN"
            )

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_validation_plan_id": "temporal_continuity_operator_authorization_record_approval_validation_plan_001",
        "source_approval_dry_run_path": source_approval_dry_run_path,
        "source_approval_dry_run_hash": source_approval_dry_run_hash,
        "approval_validation_plan_status": status,
        "source_approval_dry_run_status": source_approval_dry_run_status,
        "approval_invariant_validation_requirements": sorted(approval_invariant_validation_requirements),
        "operator_acknowledgement_validation_requirements": sorted(operator_acknowledgement_validation_requirements),
        "approval_constraint_validation_requirements": sorted(approval_constraint_validation_requirements),
        "approval_provenance_validation_requirements": sorted(approval_provenance_validation_requirements),
        "approval_hash_validation_requirements": sorted(approval_hash_validation_requirements),
        "approval_blocker_validation_requirements": sorted(approval_blocker_validation_requirements),
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
        "approval_validation_plan_only": True,
        "approval_dry_run_only": False,
        "simulated_only": True,
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
        "source_approval_dry_run_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_validation_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
