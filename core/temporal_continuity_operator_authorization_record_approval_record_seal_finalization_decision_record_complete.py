from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationDecisionRecordComplete.v1"
)

SOURCE_DECISION_RECORD_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record/latest.json"
)

_SOURCE_REQUIRED_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_READY"
)

_STATUS_COMPLETE = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE_FAILED"
)

_NEXT_LANE_ON_COMPLETE = (
    "P107_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE_ACKNOWLEDGED"
)
_NEXT_LANE_FALLBACK = (
    "P105_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD"
)

_REQUIRED_ODR_DECISION_VALUE = "approve_finalization_review_record"

_FORBIDDEN_AUTHORITY_FIELDS: tuple[str, ...] = (
    "authorization_granted",
    "finalization_authorized",
    "approval_record_sealed",
    "valid_for_execution",
    "execution_authority",
    "token_minting_allowed",
    "actual_finalization_executed",
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "baseline_mutation",
    "runtime_mutation",
    "governance_authority_mutation",
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
        "finalization_decision_record_complete_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _run_completion_checks(p105: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append({
        "check_id": "source_record_status_is_ready",
        "passed": p105.get("finalization_decision_record_status") == _SOURCE_REQUIRED_STATUS,
    })

    checks.append({
        "check_id": "source_decision_record_ready_true",
        "passed": p105.get("decision_record_ready") is True,
    })

    record_hash = str(p105.get("finalization_decision_record_hash", ""))
    checks.append({
        "check_id": "source_record_hash_present",
        "passed": bool(record_hash) and record_hash != "NOT_COMPUTABLE",
    })

    checks.append({
        "check_id": "source_advisory_only_true",
        "passed": p105.get("advisory_only") is True and p105.get("decision_record_only") is True,
    })

    checks.append({
        "check_id": "source_autonomous_approval_false",
        "passed": p105.get("autonomous_approval") is not True,
    })

    lock_violations: list[str] = []
    for field in _FORBIDDEN_AUTHORITY_FIELDS:
        if p105.get(field) is True:
            lock_violations.append(f"p105_{field}_must_be_false:found_true")
    checks.append({
        "check_id": "source_authority_locks_clean",
        "passed": len(lock_violations) == 0,
        "violations": lock_violations,
    })

    dr = p105.get("finalization_decision_record", {})
    if not isinstance(dr, dict):
        dr = {}
    checks.append({
        "check_id": "source_decision_value_is_approve",
        "passed": dr.get("decision_value") == _REQUIRED_ODR_DECISION_VALUE,
    })

    return checks


def _build_completion_receipt(p105: dict[str, Any]) -> dict[str, Any]:
    dr = p105.get("finalization_decision_record", {})
    if not isinstance(dr, dict):
        dr = {}
    return {
        "p105_record_hash": str(p105.get("finalization_decision_record_hash", "NOT_COMPUTABLE")),
        "p105_record_status": str(p105.get("finalization_decision_record_status", "NOT_COMPUTABLE")),
        "p105_decision_record_ready": p105.get("decision_record_ready") is True,
        "p104_decision_hash_anchor": str(dr.get("p104_decision_hash_anchor", "NOT_COMPUTABLE")),
        "decision_value": str(dr.get("decision_value", "NOT_PROVIDED")),
        "decision_id": str(dr.get("decision_id", "NOT_PROVIDED")),
        "operator_id": str(dr.get("operator_id", "NOT_PROVIDED")),
        "advisory_only_confirmed": p105.get("advisory_only") is True,
        "decision_record_only_confirmed": p105.get("decision_record_only") is True,
        "autonomous_approval": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "approval_record_sealed": False,
        "execution_authority": False,
        "actual_finalization_executed": False,
    }


def _build_provenance_reanchor(p105: dict[str, Any]) -> dict[str, Any]:
    pc = p105.get("finalization_decision_provenance_chain", {})
    if not isinstance(pc, dict):
        pc = {}
    return {
        "p105_record_hash": str(p105.get("finalization_decision_record_hash", "NOT_COMPUTABLE")),
        "p104_decision_hash": str(pc.get("p104_decision_hash", "NOT_COMPUTABLE")),
        "p103_review_hash": str(pc.get("p103_review_hash", "NOT_COMPUTABLE")),
        "p103_review_file_hash": str(pc.get("p103_review_file_hash", "NOT_COMPUTABLE")),
        "p103_review_id": str(pc.get("p103_review_id", "NOT_COMPUTABLE")),
        "p103_review_passed": pc.get("p103_review_passed") is True,
        "p102_execution_hash_anchor": str(pc.get("p102_execution_hash_anchor", "NOT_COMPUTABLE")),
        "finalization_check_summary": pc.get("finalization_check_summary", {}),
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete(
    *,
    repo_root: str | Path = ".",
    source_decision_record_path: str = SOURCE_DECISION_RECORD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_decision_record_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_decision_record_complete_status = _STATUS_NOT_COMPUTABLE
    recommended_next_lane = _NEXT_LANE_FALLBACK
    completion_acknowledged = False
    receipt_issued = False
    completion_blockers: list[str] = []
    completion_checks: list[dict[str, Any]] = []
    completion_receipt: dict[str, Any] = {}
    completion_provenance_reanchor: dict[str, Any] = {}

    if source_payload is None:
        completion_blockers = [
            "source_decision_record_missing_or_unreadable",
            f"source_path:{source_decision_record_path}",
        ]
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("finalization_decision_record_status", "NOT_COMPUTABLE")
        )

        completion_checks = _run_completion_checks(source_payload)
        checks_all_pass = all(c.get("passed") is True for c in completion_checks)

        lock_violation = any(
            "must_be_false:found_true" in v
            for c in completion_checks
            if c.get("check_id") == "source_authority_locks_clean"
            for v in c.get("violations", [])
        )

        autonomous_fail = not any(
            c.get("passed") is True
            for c in completion_checks
            if c.get("check_id") == "source_autonomous_approval_false"
        )

        if lock_violation or autonomous_fail:
            finalization_decision_record_complete_status = _STATUS_FAILED
            completion_blockers = [
                f"completion_check_failed:{c['check_id']}"
                for c in completion_checks
                if not c.get("passed")
            ]
        elif source_status != _SOURCE_REQUIRED_STATUS:
            finalization_decision_record_complete_status = _STATUS_BLOCKED
            completion_blockers = [
                f"source_record_status:{source_status}",
                "source_record_not_ready",
            ]
        elif not checks_all_pass:
            finalization_decision_record_complete_status = _STATUS_FAILED
            completion_blockers = [
                f"completion_check_failed:{c['check_id']}"
                for c in completion_checks
                if not c.get("passed")
            ]
        else:
            finalization_decision_record_complete_status = _STATUS_COMPLETE
            recommended_next_lane = _NEXT_LANE_ON_COMPLETE
            completion_acknowledged = True
            receipt_issued = True
            completion_receipt = _build_completion_receipt(source_payload)
            completion_provenance_reanchor = _build_provenance_reanchor(source_payload)

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "finalization_decision_record_complete_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_001"
        ),
        "source_decision_record_path": source_decision_record_path,
        "source_decision_record_hash": source_hash,
        "source_decision_record_status": source_status,
        "source_decision_record_observed": source_observed,
        "finalization_decision_record_complete_status": finalization_decision_record_complete_status,
        "completion_acknowledged": completion_acknowledged,
        "receipt_issued": receipt_issued,
        "completion_blockers": sorted(completion_blockers),
        "blockers": sorted(completion_blockers),
        "completion_checks": completion_checks,
        "completion_receipt": completion_receipt,
        "completion_provenance_reanchor": completion_provenance_reanchor,
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "completion_receipt_only": True,
        "finalization_decision_record_complete_only": True,
        "decision_record_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "actual_finalization_executed": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "governance_authority_mutation": False,
        "autonomous_approval": False,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
