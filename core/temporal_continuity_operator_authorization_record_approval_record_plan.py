from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordPlan.v1"
SOURCE_APPROVAL_VALIDATION_DRY_RUN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.json"
)


_REQUIRED_APPROVAL_RECORD_FIELDS = {
    "identity_fields": [
        "approval_record_id",
        "approval_record_schema_version",
        "approval_record_created_at",
    ],
    "source_fields": [
        "source_approval_validation_dry_run_path",
        "source_approval_validation_dry_run_hash",
        "source_approval_validation_dry_run_status",
    ],
    "operator_fields": [
        "operator_id",
        "operator_acknowledgement",
        "operator_attestation",
    ],
    "authority_lock_fields": [
        "approval_granted",
        "authorization_granted",
        "execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
    ],
    "integrity_fields": ["approval_record_hash", "approval_record_seal", "approval_record_signature"],
}


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_plan_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_approval_record_plan(
    *, repo_root: str | Path = ".", source_approval_validation_dry_run_path: str = SOURCE_APPROVAL_VALIDATION_DRY_RUN_PATH
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_validation_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_approval_validation_dry_run_hash = "NOT_COMPUTABLE"
    source_approval_validation_dry_run_status = "NOT_COMPUTABLE"
    approval_record_plan_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P88_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN"
    blockers: list[str] = []
    validation_passed = False

    required_approval_record_fields = {
        key: sorted(values) for key, values in sorted(_REQUIRED_APPROVAL_RECORD_FIELDS.items(), key=lambda kv: kv[0])
    }
    approval_record_construction_requirements = sorted(
        [
            "approval_record_must_not_be_created_in_plan_lane",
            "approval_record_plan_must_declare_future_record_shape_only",
            "canonical_json_serialization_required",
            "deterministic_ordering_required",
            "planned_expected_outputs_must_exclude_real_authorization_records",
        ]
    )
    operator_approval_provenance_requirements = sorted(
        [
            "operator_attestation_reference_required",
            "source_approval_validation_dry_run_hash_must_be_present",
            "source_approval_validation_dry_run_status_must_be_ready",
            "source_path_must_match_expected_lane_output",
        ]
    )
    approval_record_hash_requirements = sorted(
        [
            "approval_record_plan_hash_must_be_canonical",
            "approval_record_plan_hash_must_be_reproducible",
            "source_approval_validation_dry_run_sha256_required",
        ]
    )
    approval_record_seal_requirements = sorted(
        [
            "approval_record_creation_requires_future_governed_lane",
            "approval_record_plan_must_set_approval_record_created_false",
            "approval_record_plan_must_set_authority_flags_false",
            "seal_must_not_grant_authorization",
        ]
    )
    approval_record_blockers: list[str] = []

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_validation_dry_run_missing_or_unreadable",
            f"source_path:{source_approval_validation_dry_run_path}",
        ]
        approval_record_blockers = sorted(blockers)
    else:
        source_approval_validation_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_approval_validation_dry_run_status = str(
            source_payload.get("approval_validation_dry_run_status", "NOT_COMPUTABLE")
        )
        validation_passed = source_payload.get("validation_passed") is True

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        if source_approval_validation_dry_run_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY":
            approval_record_plan_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_DRY_RUN"
            blockers = [f"source_approval_validation_dry_run_status:{source_approval_validation_dry_run_status}"]
        elif not validation_passed:
            approval_record_plan_status = "BLOCKED_BY_FAILED_APPROVAL_VALIDATION_DRY_RUN"
            blockers = ["approval_validation_dry_run_validation_passed_false"]
        else:
            approval_record_plan_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY"
            recommended_next_lane = "P90_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN"

        approval_record_blockers = sorted(blockers)

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_plan_id": "temporal_continuity_operator_authorization_record_approval_record_plan_001",
        "source_approval_validation_dry_run_path": source_approval_validation_dry_run_path,
        "source_approval_validation_dry_run_hash": source_approval_validation_dry_run_hash,
        "approval_record_plan_status": approval_record_plan_status,
        "source_approval_validation_dry_run_status": source_approval_validation_dry_run_status,
        "validation_passed": validation_passed,
        "required_approval_record_fields": required_approval_record_fields,
        "approval_record_construction_requirements": approval_record_construction_requirements,
        "operator_approval_provenance_requirements": operator_approval_provenance_requirements,
        "approval_record_hash_requirements": approval_record_hash_requirements,
        "approval_record_seal_requirements": approval_record_seal_requirements,
        "approval_record_blockers": approval_record_blockers,
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
        "approval_record_plan_only": True,
        "approval_record_creation_authority": False,
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
        "source_approval_validation_dry_run_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
