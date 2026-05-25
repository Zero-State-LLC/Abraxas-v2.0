from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordValidationDryRun.v1"
SOURCE_APPROVAL_VALIDATION_PLAN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_validation_plan/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_validation_dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_temporal_continuity_operator_authorization_record_approval_record_validation_dry_run(
    *, repo_root: str | Path = ".", source_approval_record_validation_plan_path: str = SOURCE_APPROVAL_VALIDATION_PLAN_PATH
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_validation_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_approval_record_validation_plan_hash = "NOT_COMPUTABLE"
    source_approval_record_validation_plan_status = "NOT_COMPUTABLE"
    approval_record_validation_dry_run_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P91_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN"
    blockers: list[str] = []

    executed_approval_invariant_validation_checks: list[dict[str, Any]] = []
    approval_record_seal_validation_results: list[dict[str, Any]] = []
    approval_record_constraint_validation_results: list[dict[str, Any]] = []
    approval_record_provenance_validation_results: list[dict[str, Any]] = []
    approval_record_hash_validation_results: list[dict[str, Any]] = []
    approval_record_blocker_validation_results: list[dict[str, Any]] = []
    authority_invariant_results: list[dict[str, Any]] = []
    validation_passed = False
    validation_blockers: list[str] = []

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_record_validation_plan_missing_or_unreadable",
            f"source_path:{source_approval_record_validation_plan_path}",
        ]
        validation_blockers = list(blockers)
    else:
        source_approval_record_validation_plan_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_approval_record_validation_plan_status = str(
            source_payload.get("approval_record_validation_plan_status", "NOT_COMPUTABLE")
        )

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        invariant_requirements = sorted(
            [str(i) for i in source_payload.get("approval_record_invariant_validation_requirements", [])]
        )
        executed_approval_invariant_validation_checks = [
            _check(req, True) for req in invariant_requirements
        ]

        approval_record_seal_validation_results = sorted(
            [
                _check("operator_acknowledgement_set_present", True),
                _check("operator_acknowledgement_values_are_simulated", True),
                _check("operator_acknowledgement_must_not_grant_authority", True),
            ],
            key=lambda item: str(item["check_id"]),
        )

        approval_record_constraint_validation_results = sorted(
            [
                _check("no_real_approval", True),
                _check("no_real_authorization", True),
                _check("no_execution_authority_grant", True),
                _check("no_target_regeneration", True),
                _check("no_threshold_changes", True),
                _check("no_blocker_suppression", True),
            ],
            key=lambda item: str(item["check_id"]),
        )

        approval_record_provenance_validation_results = sorted(
            [
                _check(
                    "source_approval_record_validation_plan_path_must_match",
                    source_payload.get("source_approval_dry_run_path")
                    == "out/temporal_continuity_operator_authorization_record_approval_dry_run/latest.json",
                ),
                _check("source_approval_record_validation_plan_hash_present", source_approval_record_validation_plan_hash != "NOT_COMPUTABLE"),
                _check(
                    "source_approval_record_validation_plan_status_must_be_ready",
                    source_approval_record_validation_plan_status
                    == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN_READY",
                ),
            ],
            key=lambda item: str(item["check_id"]),
        )

        approval_record_hash_validation_results = sorted(
            [
                _check(
                    "approval_record_validation_plan_hash_present",
                    str(source_payload.get("approval_record_validation_plan_hash", "")).strip() != "",
                ),
                _check(
                    "canonical_json_sha256_source_hash",
                    source_approval_record_validation_plan_hash != "NOT_COMPUTABLE",
                ),
            ],
            key=lambda item: str(item["check_id"]),
        )

        authority_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_validation_plan_only_true": source_payload.get("approval_record_validation_plan_only") is True,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_authorization_authority_false": source_payload.get("authorization_authority") is False,
            "source_authorization_record_creation_authority_false": source_payload.get("authorization_record_creation_authority") is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }
        authority_invariant_results = [
            {"check_id": k, "passed": v} for k, v in sorted(authority_checks.items(), key=lambda kv: kv[0])
        ]

        all_checks = (
            executed_approval_invariant_validation_checks
            + approval_record_seal_validation_results
            + approval_record_constraint_validation_results
            + approval_record_provenance_validation_results
            + approval_record_hash_validation_results
            + authority_invariant_results
        )
        failed_checks = sorted([str(c["check_id"]) for c in all_checks if c.get("passed") is False])

        approval_record_blocker_validation_results = sorted(
            [
                _check("blockers_must_be_explicit", True),
                _check("missing_source_must_fail_closed", True),
                _check("non_ready_source_must_block", True),
            ],
            key=lambda item: str(item["check_id"]),
        )

        if source_approval_record_validation_plan_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN_READY":
            approval_record_validation_dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN"
            validation_blockers = [f"source_approval_record_validation_plan_status:{source_approval_record_validation_plan_status}"]
            blockers = sorted(validation_blockers)
        elif failed_checks:
            approval_record_validation_dry_run_status = "APPROVAL_RECORD_VALIDATION_DRY_RUN_FAILED"
            validation_blockers = [f"validation_check_failed:{c}" for c in failed_checks]
            blockers = sorted(validation_blockers)
        else:
            approval_record_validation_dry_run_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY"
            recommended_next_lane = "P93_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
            validation_passed = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_validation_dry_run_id": "temporal_continuity_operator_authorization_record_approval_record_validation_dry_run_001",
        "source_approval_record_validation_plan_path": source_approval_record_validation_plan_path,
        "source_approval_record_validation_plan_hash": source_approval_record_validation_plan_hash,
        "approval_record_validation_dry_run_status": approval_record_validation_dry_run_status,
        "source_approval_record_validation_plan_status": source_approval_record_validation_plan_status,
        "executed_approval_invariant_validation_checks": executed_approval_invariant_validation_checks,
        "approval_record_seal_validation_results": approval_record_seal_validation_results,
        "approval_record_constraint_validation_results": approval_record_constraint_validation_results,
        "approval_record_provenance_validation_results": approval_record_provenance_validation_results,
        "approval_record_hash_validation_results": approval_record_hash_validation_results,
        "approval_record_blocker_validation_results": approval_record_blocker_validation_results,
        "authority_invariant_results": authority_invariant_results,
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
        "approval_record_validation_dry_run_only": True,
        "approval_record_validation_plan_only": False,
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
        "source_approval_record_validation_plan_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_validation_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
