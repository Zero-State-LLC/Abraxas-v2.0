from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordValidationPlan.v1"
SOURCE_APPROVAL_RECORD_DRY_RUN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_dry_run/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_validation_plan_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_approval_record_validation_plan(
    *, repo_root: str | Path = ".", source_approval_record_dry_run_path: str = SOURCE_APPROVAL_RECORD_DRY_RUN_PATH
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_approval_record_dry_run_hash = "NOT_COMPUTABLE"
    source_approval_record_dry_run_status = "NOT_COMPUTABLE"
    approval_record_validation_plan_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P90_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN"
    blockers: list[str] = []

    approval_record_field_validation_requirements = sorted(
        [
            "approval_record_schema_version_must_be_present",
            "identity_fields_must_match_expected_shape",
            "source_reference_fields_must_be_present",
        ]
    )
    record_construction_validation_requirements = sorted(
        [
            "record_construction_dry_run_results_must_exist",
            "simulated_approval_record_must_be_present",
            "simulated_record_must_not_be_persisted_as_real_record",
        ]
    )
    provenance_validation_requirements = sorted(
        [
            "provenance_results_must_exist",
            "source_dry_run_hash_must_be_present",
            "source_dry_run_path_must_match_expected_lane_output",
        ]
    )
    hash_validation_requirements = sorted(
        [
            "approval_record_dry_run_hash_must_be_present",
            "approval_record_validation_plan_hash_must_be_canonical",
            "source_approval_record_dry_run_sha256_required",
        ]
    )
    seal_validation_requirements = sorted(
        [
            "seal_validation_is_advisory_only",
            "simulated_seal_fields_must_not_grant_authorization",
            "validation_plan_must_not_create_real_approval_record",
        ]
    )
    authority_invariant_validation_requirements = sorted(
        [
            "approval_granted_must_remain_false",
            "authorization_granted_must_remain_false",
            "execution_authority_must_remain_false",
            "token_minting_allowed_must_remain_false",
            "valid_for_execution_must_remain_false",
        ]
    )
    approval_record_blocker_validation_requirements = sorted(
        [
            "blockers_must_be_explicit_when_not_ready",
            "ready_status_requires_empty_blockers",
            "source_status_must_route_next_lane_deterministically",
        ]
    )

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_record_dry_run_missing_or_unreadable",
            f"source_path:{source_approval_record_dry_run_path}",
        ]
    else:
        source_approval_record_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_approval_record_dry_run_status = str(source_payload.get("approval_record_dry_run_status", "NOT_COMPUTABLE"))

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        governance_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_dry_run_only_true": source_payload.get("approval_record_dry_run_only") is True,
            "source_approval_record_created_false": source_payload.get("approval_record_created") is False,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }

        if source_approval_record_dry_run_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN_READY":
            approval_record_validation_plan_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN"
            blockers = [f"source_approval_record_dry_run_status:{source_approval_record_dry_run_status}"]
        elif not all(governance_checks.values()):
            approval_record_validation_plan_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN"
            blockers = [f"governance_invariant_failed:{k}" for k, v in sorted(governance_checks.items()) if not v]
        else:
            approval_record_validation_plan_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN_READY"
            recommended_next_lane = "P92_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN"

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_validation_plan_id": "temporal_continuity_operator_authorization_record_approval_record_validation_plan_001",
        "source_approval_record_dry_run_path": source_approval_record_dry_run_path,
        "source_approval_record_dry_run_hash": source_approval_record_dry_run_hash,
        "approval_record_validation_plan_status": approval_record_validation_plan_status,
        "source_approval_record_dry_run_status": source_approval_record_dry_run_status,
        "approval_record_field_validation_requirements": approval_record_field_validation_requirements,
        "record_construction_validation_requirements": record_construction_validation_requirements,
        "provenance_validation_requirements": provenance_validation_requirements,
        "hash_validation_requirements": hash_validation_requirements,
        "seal_validation_requirements": seal_validation_requirements,
        "authority_invariant_validation_requirements": authority_invariant_validation_requirements,
        "approval_record_blocker_validation_requirements": approval_record_blocker_validation_requirements,
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
        "approval_record_validation_plan_only": True,
        "approval_record_dry_run_only": False,
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
        "source_approval_record_dry_run_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_validation_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
