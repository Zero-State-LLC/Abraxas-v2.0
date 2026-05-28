from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealExecutionPlan.v1"

SOURCE_OPERATOR_DECISION_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"
)

_CROSS_LANE_SOURCES: tuple[dict[str, str], ...] = (
    {
        "check_id": "p93_seal_plan_ready",
        "source": "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json",
        "status_field": "approval_record_seal_plan_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY",
    },
    {
        "check_id": "p94_seal_dry_run_ready",
        "source": "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json",
        "status_field": "approval_record_seal_dry_run_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY",
    },
    {
        "check_id": "p95_seal_operator_review_ready",
        "source": "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json",
        "status_field": "approval_record_seal_operator_review_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
    },
)

_SEAL_EXECUTION_STEPS: tuple[dict[str, Any], ...] = (
    {
        "step_id": "SEAL_EXEC_STEP_01_VERIFY_SEAL_PLAN",
        "step_type": "advisory_verification",
        "description": (
            "Confirm the P93 approval record seal plan remains in READY state "
            "before proceeding to seal execution."
        ),
        "command_advisory": (
            "ADVISORY_ONLY: python scripts/run_temporal_continuity_operator_authorization_record_approval_record_seal_plan.py"
        ),
        "target_artifact_path": (
            "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
        ),
        "expected_status_after_run": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P93_SEAL_PLAN_REGENERATION",
        "requires_separate_operator_authorization": False,
        "execution_plan_only": True,
    },
    {
        "step_id": "SEAL_EXEC_STEP_02_VERIFY_DRY_RUN",
        "step_type": "advisory_verification",
        "description": (
            "Confirm the P94 approval record seal dry-run remains in READY state "
            "and all 30 checks are passing."
        ),
        "command_advisory": (
            "ADVISORY_ONLY: python scripts/run_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run.py"
        ),
        "target_artifact_path": (
            "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
        ),
        "expected_status_after_run": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P94_SEAL_DRY_RUN_REGENERATION",
        "requires_separate_operator_authorization": False,
        "execution_plan_only": True,
    },
    {
        "step_id": "SEAL_EXEC_STEP_03_VERIFY_OPERATOR_REVIEW",
        "step_type": "advisory_verification",
        "description": (
            "Confirm the P95 approval record seal operator review remains in READY state "
            "with review_passed: true."
        ),
        "command_advisory": (
            "ADVISORY_ONLY: python scripts/run_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review.py"
        ),
        "target_artifact_path": (
            "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"
        ),
        "expected_status_after_run": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P95_SEAL_OPERATOR_REVIEW_REGENERATION",
        "requires_separate_operator_authorization": False,
        "execution_plan_only": True,
    },
    {
        "step_id": "SEAL_EXEC_STEP_04_VERIFY_OPERATOR_DECISION",
        "step_type": "advisory_verification",
        "description": (
            "Confirm the P96 approval record seal operator decision remains in APPROVED_RECORD state "
            "with decision_recorded: true and autonomous_approval: false."
        ),
        "command_advisory": (
            "ADVISORY_ONLY: python scripts/run_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision.py"
        ),
        "target_artifact_path": (
            "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json"
        ),
        "expected_status_after_run": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P96_SEAL_OPERATOR_DECISION",
        "requires_separate_operator_authorization": False,
        "execution_plan_only": True,
    },
    {
        "step_id": "SEAL_EXEC_STEP_05_EXECUTE_APPROVAL_RECORD_SEAL",
        "step_type": "advisory_seal_execution",
        "description": (
            "Advisory description of the seal execution step only. "
            "This step is NOT executed by P97. "
            "Actual seal execution requires a separate future lane (P98) with its own "
            "governance design proposal and operator authorization. "
            "No approval is granted, no record is sealed, and no execution authority is created by this step description."
        ),
        "command_advisory": (
            "ADVISORY_ONLY: [to be defined in P98 governance design proposal — not yet authorized]"
        ),
        "target_artifact_path": (
            "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json"
        ),
        "expected_status_after_run": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_COMPLETE",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P97_SEAL_EXECUTION_PLAN_REGENERATION",
        "requires_separate_operator_authorization": True,
        "execution_plan_only": True,
        "seal_not_executed_by_this_lane": True,
        "approval_granted": False,
        "approval_record_sealed": False,
        "execution_authority": False,
    },
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (FileNotFoundError, OSError):
        return "NOT_COMPUTABLE"


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {
        **packet_base,
        "approval_record_seal_execution_plan_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _cross_lane_sweep(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in _CROSS_LANE_SOURCES:
        p = root / spec["source"]
        payload = _load_json_dict(p)
        if payload is None:
            observed = "NOT_COMPUTABLE"
            passed = False
        else:
            observed = str(payload.get(spec["status_field"], "NOT_COMPUTABLE"))
            passed = observed == spec["expected_status"]
        results.append({
            "check_id": spec["check_id"],
            "source": spec["source"],
            "expected_status": spec["expected_status"],
            "observed_status": observed,
            "passed": passed,
        })
    return results


def _make_decision_provenance_anchor(p96: dict[str, Any], p96_file_hash: str) -> dict[str, Any]:
    odr = p96.get("operator_decision_record", {})
    if not isinstance(odr, dict):
        odr = {}
    up = p96.get("upstream_provenance", {})
    if not isinstance(up, dict):
        up = {}
    return {
        "decision_hash": str(p96.get("approval_record_seal_operator_decision_hash", "NOT_COMPUTABLE")),
        "decision_file_hash": p96_file_hash,
        "decision_id": str(odr.get("decision_id", "NOT_PROVIDED")),
        "operator_id": str(odr.get("operator_id", "NOT_PROVIDED")),
        "decision_value": str(odr.get("decision_value", "NOT_COMPUTABLE")),
        "review_hash": str(up.get("review_hash", "NOT_COMPUTABLE")),
        "review_file_hash": str(up.get("review_file_hash", "NOT_COMPUTABLE")),
        "autonomous_approval": False,
    }


def _check_p96_posture_violations(p96: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for field in ("approval_granted", "authorization_granted", "execution_authority",
                  "approval_record_sealed", "valid_for_execution", "token_minting_allowed"):
        if p96.get(field) is True:
            violations.append(f"p96_output_{field}_must_be_false:found_true")
    odr = p96.get("operator_decision_record", {})
    if isinstance(odr, dict):
        for field in ("approval_granted", "authorization_granted", "execution_authority",
                      "approval_record_sealed"):
            if odr.get(field) is True:
                violations.append(f"p96_operator_decision_record_{field}_must_be_false:found_true")
    if p96.get("autonomous_approval") is True:
        violations.append("p96_autonomous_approval_must_be_false:found_true")
    return violations


def build_temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan(
    *,
    repo_root: str | Path = ".",
    source_operator_decision_path: str = SOURCE_OPERATOR_DECISION_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_operator_decision_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    approval_record_seal_execution_plan_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P96_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
    )
    plan_ready = False
    plan_blockers: list[str] = []
    seal_execution_steps: list[dict[str, Any]] = []
    seal_execution_readiness_checks: list[dict[str, Any]] = []
    decision_provenance_anchor: dict[str, Any] = {}
    seal_execution_plan_summary: dict[str, Any] = {
        "step_count": 0,
        "all_steps_advisory": True,
        "execution_authority_required_externally": True,
        "execution_plan_only": True,
        "seal_not_executed": True,
    }

    if source_payload is None:
        plan_blockers = [
            "source_operator_decision_missing_or_unreadable",
            f"source_path:{source_operator_decision_path}",
        ]
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("approval_record_seal_operator_decision_status", "NOT_COMPUTABLE")
        )

        posture_violations = _check_p96_posture_violations(source_payload)
        if posture_violations:
            approval_record_seal_execution_plan_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_FAILED"
            )
            plan_blockers = sorted(posture_violations)
            decision_provenance_anchor = _make_decision_provenance_anchor(source_payload, source_hash)
        elif source_status != (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD"
        ):
            approval_record_seal_execution_plan_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
            )
            plan_blockers = [f"source_operator_decision_status:{source_status}"]
            decision_provenance_anchor = _make_decision_provenance_anchor(source_payload, source_hash)
        else:
            odr = source_payload.get("operator_decision_record", {})
            if not isinstance(odr, dict):
                odr = {}
            decision_val = str(odr.get("decision_value", ""))
            decision_recorded = source_payload.get("decision_recorded") is True
            autonomous_approval = source_payload.get("autonomous_approval") is True

            decision_provenance_anchor = _make_decision_provenance_anchor(source_payload, source_hash)

            if decision_val != "approve_seal_record":
                approval_record_seal_execution_plan_status = (
                    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
                )
                plan_blockers = [
                    f"operator_decision_record_decision_value_must_be_approve_seal_record:found_{decision_val!r}"
                ]
            elif not decision_recorded:
                approval_record_seal_execution_plan_status = (
                    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
                )
                plan_blockers = ["source_decision_recorded:false"]
            elif autonomous_approval:
                approval_record_seal_execution_plan_status = (
                    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
                )
                plan_blockers = ["source_autonomous_approval:true"]
            else:
                seal_execution_readiness_checks = _cross_lane_sweep(root)
                seal_execution_steps = [dict(s) for s in _SEAL_EXECUTION_STEPS]
                seal_execution_plan_summary = {
                    "step_count": len(seal_execution_steps),
                    "all_steps_advisory": True,
                    "execution_authority_required_externally": True,
                    "execution_plan_only": True,
                    "seal_not_executed": True,
                }
                approval_record_seal_execution_plan_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY"
                )
                recommended_next_lane = (
                    "P98_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION"
                )
                plan_ready = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_execution_plan_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan_001"
        ),
        "source_operator_decision_path": source_operator_decision_path,
        "source_operator_decision_hash": source_hash,
        "source_operator_decision_status": source_status,
        "source_operator_decision_observed": source_observed,
        "approval_record_seal_execution_plan_status": approval_record_seal_execution_plan_status,
        "plan_ready": plan_ready,
        "seal_execution_steps": seal_execution_steps,
        "seal_execution_readiness_checks": seal_execution_readiness_checks,
        "decision_provenance_anchor": decision_provenance_anchor,
        "seal_execution_plan_summary": seal_execution_plan_summary,
        "plan_only_attestation": {
            "no_seal_executed": True,
            "no_approval_granted": True,
            "no_execution_authority_created": True,
            "plan_preparation_only": True,
        },
        "plan_blockers": sorted(plan_blockers),
        "blockers": sorted(plan_blockers),
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "execution_plan_only": True,
        "approval_record_seal_execution_plan_only": True,
        "operator_approval_required": True,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
