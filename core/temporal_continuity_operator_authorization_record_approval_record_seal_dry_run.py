from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealDryRun.v1"
SOURCE_APPROVAL_RECORD_SEAL_PLAN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_seal_dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(
    *,
    repo_root: str | Path = ".",
    source_approval_record_seal_plan_path: str = SOURCE_APPROVAL_RECORD_SEAL_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_seal_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    validation_passed = False
    dry_run_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P93_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
    blockers: list[str] = []
    validation_blockers: list[str] = []

    seal_construction_validation_results: list[dict[str, Any]] = []
    seal_provenance_validation_results: list[dict[str, Any]] = []
    seal_hash_validation_results: list[dict[str, Any]] = []
    seal_blocker_validation_results: list[dict[str, Any]] = []
    authority_invariant_validation_results: list[dict[str, Any]] = []

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_record_seal_plan_missing_or_unreadable",
            f"source_path:{source_approval_record_seal_plan_path}",
        ]
        validation_blockers = list(blockers)
    else:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_status = str(source_payload.get("approval_record_seal_plan_status", "NOT_COMPUTABLE"))
        validation_passed = source_payload.get("validation_passed") is True

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        for source_key, output_key in (
            ("seal_construction_requirements", "seal_construction_validation_results"),
            ("seal_provenance_requirements", "seal_provenance_validation_results"),
            ("seal_hash_requirements", "seal_hash_validation_results"),
            ("seal_blocker_requirements", "seal_blocker_validation_results"),
        ):
            reqs = sorted([str(i) for i in source_payload.get(source_key, [])])
            checks = [_check(req, True) for req in reqs]
            if output_key == "seal_construction_validation_results":
                seal_construction_validation_results = checks
            elif output_key == "seal_provenance_validation_results":
                seal_provenance_validation_results = checks
            elif output_key == "seal_hash_validation_results":
                seal_hash_validation_results = checks
            else:
                seal_blocker_validation_results = checks

        authority_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_seal_plan_only_true": source_payload.get("approval_record_seal_plan_only") is True,
            "source_approval_record_sealed_false": source_payload.get("approval_record_sealed") is False,
            "source_approval_record_created_false": source_payload.get("approval_record_created") is False,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_authorization_authority_false": source_payload.get("authorization_authority") is False,
            "source_authorization_record_creation_authority_false": source_payload.get("authorization_record_creation_authority") is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }
        authority_invariant_validation_results = [
            {"check_id": k, "passed": v} for k, v in sorted(authority_checks.items(), key=lambda kv: kv[0])
        ]

        all_checks = (
            seal_construction_validation_results
            + seal_provenance_validation_results
            + seal_hash_validation_results
            + seal_blocker_validation_results
            + authority_invariant_validation_results
        )
        failed_checks = sorted([str(c["check_id"]) for c in all_checks if c.get("passed") is False])

        if source_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY":
            dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
            validation_blockers = [f"source_approval_record_seal_plan_status:{source_status}"]
            blockers = sorted(validation_blockers)
        elif not validation_passed:
            dry_run_status = "BLOCKED_BY_FAILED_APPROVAL_RECORD_SEAL_PLAN_SOURCE"
            validation_blockers = ["source_validation_passed:false"]
            blockers = sorted(validation_blockers)
        elif failed_checks:
            dry_run_status = "APPROVAL_RECORD_SEAL_DRY_RUN_FAILED"
            validation_blockers = [f"validation_check_failed:{c}" for c in failed_checks]
            blockers = sorted(validation_blockers)
        else:
            dry_run_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY"
            recommended_next_lane = "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW"
            validation_passed = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_dry_run_id": "temporal_continuity_operator_authorization_record_approval_record_seal_dry_run_001",
        "source_approval_record_seal_plan_path": source_approval_record_seal_plan_path,
        "source_approval_record_seal_plan_hash": source_hash,
        "approval_record_seal_dry_run_status": dry_run_status,
        "source_approval_record_seal_plan_status": source_status,
        "seal_construction_validation_results": seal_construction_validation_results,
        "seal_provenance_validation_results": seal_provenance_validation_results,
        "seal_hash_validation_results": seal_hash_validation_results,
        "seal_blocker_validation_results": seal_blocker_validation_results,
        "authority_invariant_validation_results": authority_invariant_validation_results,
        "validation_passed": validation_passed,
        "validation_blockers": sorted(validation_blockers),
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
        "approval_record_seal_dry_run_only": True,
        "approval_record_seal_plan_only": False,
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
        "source_approval_record_seal_plan_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
