from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealReview.v1"
SOURCE_APPROVAL_RECORD_SEAL_DRY_RUN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_seal_review_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_temporal_continuity_operator_authorization_record_approval_record_seal_review(
    *,
    repo_root: str | Path = ".",
    source_approval_record_seal_dry_run_path: str = SOURCE_APPROVAL_RECORD_SEAL_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_seal_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    review_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )
    blockers: list[str] = []
    review_findings: list[dict[str, Any]] = []
    validation_passed = False

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_record_seal_dry_run_missing_or_unreadable",
            f"source_path:{source_approval_record_seal_dry_run_path}",
        ]
    else:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_status = str(
            source_payload.get("approval_record_seal_dry_run_status", "NOT_COMPUTABLE")
        )
        source_validation_passed = source_payload.get("validation_passed") is True

        allowed_target_candidates = sorted(
            [str(i) for i in source_payload.get("allowed_target_candidates", [])]
        )
        denied_target_candidates = sorted(
            [str(i) for i in source_payload.get("denied_target_candidates", [])]
        )
        allowed_command_candidates = sorted(
            [str(i) for i in source_payload.get("allowed_command_candidates", [])]
        )
        denied_command_candidates = sorted(
            [str(i) for i in source_payload.get("denied_command_candidates", [])]
        )
        planned_authorization_scope = sorted(
            [str(i) for i in source_payload.get("planned_authorization_scope", [])]
        )
        planned_expected_outputs = sorted(
            [str(i) for i in source_payload.get("planned_expected_outputs", [])]
        )

        authority_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_seal_dry_run_only_true": (
                source_payload.get("approval_record_seal_dry_run_only") is True
            ),
            "source_approval_record_sealed_false": (
                source_payload.get("approval_record_sealed") is False
            ),
            "source_approval_record_created_false": (
                source_payload.get("approval_record_created") is False
            ),
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": (
                source_payload.get("authorization_granted") is False
            ),
            "source_execution_authority_false": (
                source_payload.get("execution_authority") is False
            ),
            "source_authorization_authority_false": (
                source_payload.get("authorization_authority") is False
            ),
            "source_authorization_record_creation_authority_false": (
                source_payload.get("authorization_record_creation_authority") is False
            ),
            "source_token_minting_allowed_false": (
                source_payload.get("token_minting_allowed") is False
            ),
            "source_valid_for_execution_false": (
                source_payload.get("valid_for_execution") is False
            ),
        }
        review_findings = [
            _check(check_id, passed)
            for check_id, passed in sorted(authority_checks.items(), key=lambda kv: kv[0])
        ]
        failed_findings = sorted(
            [str(finding["check_id"]) for finding in review_findings if finding["passed"] is False]
        )

        if source_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY":
            review_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
            blockers = [f"source_approval_record_seal_dry_run_status:{source_status}"]
        elif not source_validation_passed:
            review_status = "BLOCKED_BY_FAILED_APPROVAL_RECORD_SEAL_DRY_RUN"
            blockers = ["source_validation_passed:false"]
        elif failed_findings:
            review_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_FAILED"
            blockers = [f"review_check_failed:{finding}" for finding in failed_findings]
        else:
            review_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR"
            )
            recommended_next_lane = "NOT_COMPUTABLE"
            validation_passed = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_review_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_review_001"
        ),
        "source_approval_record_seal_dry_run_path": source_approval_record_seal_dry_run_path,
        "source_approval_record_seal_dry_run_hash": source_hash,
        "source_approval_record_seal_dry_run_status": source_status,
        "source_approval_record_seal_dry_run_observed": source_observed,
        "approval_record_seal_review_status": review_status,
        "review_findings": review_findings,
        "validation_passed": validation_passed,
        "allowed_target_candidates": allowed_target_candidates,
        "denied_target_candidates": denied_target_candidates,
        "allowed_command_candidates": allowed_command_candidates,
        "denied_command_candidates": denied_command_candidates,
        "planned_authorization_scope": planned_authorization_scope,
        "planned_expected_outputs": planned_expected_outputs,
        "recommended_next_lane": recommended_next_lane,
        "blockers": sorted(blockers),
        "operator_review_required": True,
        "operator_hold_required": True,
        "advisory_only": True,
        "projection_only": True,
        "approval_record_seal_review_only": True,
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
        "valid_for_execution": False,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_review(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
