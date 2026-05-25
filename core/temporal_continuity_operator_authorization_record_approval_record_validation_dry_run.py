from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordValidationDryRun.v1"
SOURCE_APPROVAL_RECORD_VALIDATION_PLAN_PATH = (
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


def _results(requirements: list[str], passed: bool) -> list[dict[str, Any]]:
    return [{"requirement": item, "passed": passed, "simulated_only": True} for item in sorted(requirements)]


def build_temporal_continuity_operator_authorization_record_approval_record_validation_dry_run(
    *,
    repo_root: str | Path = ".",
    source_approval_record_validation_plan_path: str = SOURCE_APPROVAL_RECORD_VALIDATION_PLAN_PATH,
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
    validation_blockers: list[str] = []
    validation_passed = False

    executed_approval_record_field_validation_results: list[dict[str, Any]] = []
    record_construction_validation_results: list[dict[str, Any]] = []
    provenance_validation_results: list[dict[str, Any]] = []
    hash_validation_results: list[dict[str, Any]] = []
    seal_validation_results: list[dict[str, Any]] = []
    authority_invariant_validation_results: list[dict[str, Any]] = []
    approval_record_blocker_validation_results: list[dict[str, Any]] = []

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

        executed_approval_record_field_validation_results = _results(
            [str(i) for i in source_payload.get("approval_record_field_validation_requirements", [])], True
        )
        record_construction_validation_results = _results(
            [str(i) for i in source_payload.get("record_construction_validation_requirements", [])], True
        )
        provenance_validation_results = _results(
            [str(i) for i in source_payload.get("provenance_validation_requirements", [])], True
        )
        hash_validation_results = _results([str(i) for i in source_payload.get("hash_validation_requirements", [])], True)
        seal_validation_results = _results([str(i) for i in source_payload.get("seal_validation_requirements", [])], True)
        authority_invariant_validation_results = _results(
            [str(i) for i in source_payload.get("authority_invariant_validation_requirements", [])], True
        )
        approval_record_blocker_validation_results = _results(
            [str(i) for i in source_payload.get("approval_record_blocker_validation_requirements", [])], True
        )

        governance_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_validation_plan_only_true": source_payload.get("approval_record_validation_plan_only")
            is True,
            "source_approval_record_created_false": source_payload.get("approval_record_created") is False,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }

        if source_approval_record_validation_plan_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN_READY":
            approval_record_validation_dry_run_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN"
            )
            blockers = [f"source_approval_record_validation_plan_status:{source_approval_record_validation_plan_status}"]
            validation_blockers = sorted(blockers)
        else:
            validation_blockers = [
                f"governance_invariant_failed:{k}" for k, v in sorted(governance_checks.items()) if not v
            ]
            validation_passed = len(validation_blockers) == 0
            if validation_passed:
                approval_record_validation_dry_run_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_DRY_RUN_READY"
                )
                recommended_next_lane = "P93_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
            else:
                approval_record_validation_dry_run_status = "APPROVAL_RECORD_VALIDATION_DRY_RUN_FAILED"
                blockers = sorted(validation_blockers)

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_validation_dry_run_id": "temporal_continuity_operator_authorization_record_approval_record_validation_dry_run_001",
        "source_approval_record_validation_plan_path": source_approval_record_validation_plan_path,
        "source_approval_record_validation_plan_hash": source_approval_record_validation_plan_hash,
        "approval_record_validation_dry_run_status": approval_record_validation_dry_run_status,
        "source_approval_record_validation_plan_status": source_approval_record_validation_plan_status,
        "executed_approval_record_field_validation_results": executed_approval_record_field_validation_results,
        "record_construction_validation_results": record_construction_validation_results,
        "provenance_validation_results": provenance_validation_results,
        "hash_validation_results": hash_validation_results,
        "seal_validation_results": seal_validation_results,
        "authority_invariant_validation_results": authority_invariant_validation_results,
        "approval_record_blocker_validation_results": approval_record_blocker_validation_results,
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
        "source_approval_record_validation_plan_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_validation_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
