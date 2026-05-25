from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalDryRun.v1"
SOURCE_APPROVAL_PLAN_PATH = "out/temporal_continuity_operator_authorization_record_approval_plan/latest.json"


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _bool_check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_temporal_continuity_operator_authorization_record_approval_dry_run(
    *, repo_root: str | Path = ".", source_approval_plan_path: str = SOURCE_APPROVAL_PLAN_PATH
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_approval_plan_hash = "NOT_COMPUTABLE"
    source_approval_plan_status = "NOT_COMPUTABLE"
    approval_dry_run_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"
    blockers: list[str] = []

    simulated_operator_acknowledgements: list[dict[str, Any]] = []
    simulated_approval_evaluation: dict[str, Any] = {
        "ready_for_approval_dry_run": False,
        "approval_dry_run_only": True,
        "evaluation_blockers": ["source_approval_plan_missing_or_unreadable"],
    }
    approval_constraints_evaluation: list[dict[str, Any]] = []
    approval_provenance_evaluation: list[dict[str, Any]] = []
    approval_hash_evaluation: list[dict[str, Any]] = []
    approval_blockers: list[str] = []

    allowed_target_candidates: list[str] = []
    denied_target_candidates: list[str] = []
    allowed_command_candidates: list[str] = []
    denied_command_candidates: list[str] = []
    planned_authorization_scope: list[str] = []
    planned_expected_outputs: list[str] = []

    if source_payload is None:
        blockers = ["source_approval_plan_missing_or_unreadable", f"source_path:{source_approval_plan_path}"]
    else:
        source_approval_plan_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_approval_plan_status = str(source_payload.get("approval_plan_status", "NOT_COMPUTABLE"))

        allowed_target_candidates = sorted([str(i) for i in source_payload.get("allowed_target_candidates", [])])
        denied_target_candidates = sorted([str(i) for i in source_payload.get("denied_target_candidates", [])])
        allowed_command_candidates = sorted([str(i) for i in source_payload.get("allowed_command_candidates", [])])
        denied_command_candidates = sorted([str(i) for i in source_payload.get("denied_command_candidates", [])])
        planned_authorization_scope = sorted([str(i) for i in source_payload.get("planned_authorization_scope", [])])
        planned_expected_outputs = sorted([str(i) for i in source_payload.get("planned_expected_outputs", [])])

        required_acks = sorted([str(i) for i in source_payload.get("required_operator_acknowledgements", [])])
        simulated_operator_acknowledgements = [
            {"acknowledgement": ack, "simulated_acknowledged": True} for ack in required_acks
        ]

        constraints = sorted([str(i) for i in source_payload.get("approval_constraints", [])])
        approval_constraints_evaluation = [
            {"constraint": c, "passed": True, "simulated_only": True} for c in constraints
        ]

        approval_provenance_evaluation = sorted(
            [
                _bool_check(
                    "source_approval_plan_path_matches",
                    source_payload.get("source_validation_dry_run_path")
                    == "out/temporal_continuity_operator_authorization_record_validation_dry_run/latest.json",
                ),
                _bool_check("source_approval_plan_hash_present", source_approval_plan_hash != "NOT_COMPUTABLE"),
            ],
            key=lambda item: str(item["check_id"]),
        )

        approval_hash_evaluation = sorted(
            [
                _bool_check(
                    "approval_plan_hash_present",
                    str(source_payload.get("approval_plan_hash", "")).strip() != "",
                ),
                _bool_check("canonical_json_sha256_source_hash", source_approval_plan_hash != "NOT_COMPUTABLE"),
            ],
            key=lambda item: str(item["check_id"]),
        )

        governance_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_plan_only_true": source_payload.get("approval_plan_only") is True,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }
        approval_provenance_evaluation.extend(
            [{"check_id": k, "passed": v} for k, v in sorted(governance_checks.items(), key=lambda kv: kv[0])]
        )

        if source_approval_plan_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN_READY":
            approval_dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"
            blockers = [f"source_approval_plan_status:{source_approval_plan_status}"]
            approval_blockers = list(blockers)
        elif not all(governance_checks.values()):
            approval_dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_PLAN"
            approval_blockers = [f"governance_invariant_failed:{k}" for k, v in sorted(governance_checks.items()) if not v]
            blockers = sorted(approval_blockers)
        else:
            approval_dry_run_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN_READY"
            recommended_next_lane = "P87_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_VALIDATION_PLAN"

        simulated_approval_evaluation = {
            "ready_for_approval_dry_run": approval_dry_run_status
            == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_DRY_RUN_READY",
            "approval_dry_run_only": True,
            "simulated_approval_granted": False,
            "simulated_authorization_granted": False,
            "simulated_execution_authority": False,
            "evaluation_blockers": sorted(approval_blockers),
        }

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_dry_run_id": "temporal_continuity_operator_authorization_record_approval_dry_run_001",
        "source_approval_plan_path": source_approval_plan_path,
        "source_approval_plan_hash": source_approval_plan_hash,
        "approval_dry_run_status": approval_dry_run_status,
        "source_approval_plan_status": source_approval_plan_status,
        "simulated_operator_acknowledgements": simulated_operator_acknowledgements,
        "simulated_approval_evaluation": simulated_approval_evaluation,
        "approval_constraints_evaluation": approval_constraints_evaluation,
        "approval_provenance_evaluation": approval_provenance_evaluation,
        "approval_hash_evaluation": approval_hash_evaluation,
        "approval_blockers": sorted(approval_blockers),
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
        "approval_dry_run_only": True,
        "approval_plan_only": False,
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
        "source_approval_plan_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
