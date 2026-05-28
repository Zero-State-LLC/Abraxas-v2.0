from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationDecisionRecordCompleteAcknowledged.v1"
)

SOURCE_COMPLETE_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete/latest.json"
)

_SOURCE_REQUIRED_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE"
)

_STATUS_ACKNOWLEDGED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE_ACKNOWLEDGED"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE_ACKNOWLEDGED_FAILED"
)

_NEXT_LANE_ON_ACKNOWLEDGED = "FINALIZATION_DECISION_RECORD_SEGMENT_CLOSED"
_NEXT_LANE_FALLBACK = (
    "P106_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE"
)

_REQUIRED_DECISION_VALUE = "approve_finalization_review_record"

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
    h = canonical_hash(packet_base)
    packet = {**packet_base, "finalization_decision_record_complete_acknowledged_hash": h}
    snap = packet.get("terminal_provenance_snapshot")
    if isinstance(snap, dict) and snap.get("p107_acknowledged_hash") == "SELF":
        snap["p107_acknowledged_hash"] = h
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _run_acknowledgment_checks(p106: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append({
        "check_id": "source_complete_status_is_complete",
        "passed": p106.get("finalization_decision_record_complete_status") == _SOURCE_REQUIRED_STATUS,
    })

    checks.append({
        "check_id": "source_completion_acknowledged_true",
        "passed": (
            p106.get("completion_acknowledged") is True
            and p106.get("receipt_issued") is True
        ),
    })

    complete_hash = str(p106.get("finalization_decision_record_complete_hash", ""))
    checks.append({
        "check_id": "source_complete_hash_present",
        "passed": bool(complete_hash) and complete_hash != "NOT_COMPUTABLE",
    })

    checks.append({
        "check_id": "source_advisory_posture_confirmed",
        "passed": (
            p106.get("advisory_only") is True
            and p106.get("completion_receipt_only") is True
            and p106.get("decision_record_only") is True
        ),
    })

    checks.append({
        "check_id": "source_autonomous_approval_false",
        "passed": p106.get("autonomous_approval") is not True,
    })

    lock_violations: list[str] = []
    for field in _FORBIDDEN_AUTHORITY_FIELDS:
        if p106.get(field) is True:
            lock_violations.append(f"p106_{field}_must_be_false:found_true")
    checks.append({
        "check_id": "source_authority_locks_clean",
        "passed": len(lock_violations) == 0,
        "violations": lock_violations,
    })

    cr = p106.get("completion_receipt", {})
    if not isinstance(cr, dict):
        cr = {}
    checks.append({
        "check_id": "source_decision_value_is_approve",
        "passed": cr.get("decision_value") == _REQUIRED_DECISION_VALUE,
    })

    return checks


def _build_acknowledgment_receipt(p106: dict[str, Any]) -> dict[str, Any]:
    cr = p106.get("completion_receipt", {})
    if not isinstance(cr, dict):
        cr = {}
    pr = p106.get("completion_provenance_reanchor", {})
    if not isinstance(pr, dict):
        pr = {}
    return {
        "p106_complete_hash": str(p106.get("finalization_decision_record_complete_hash", "NOT_COMPUTABLE")),
        "p106_complete_status": str(p106.get("finalization_decision_record_complete_status", "NOT_COMPUTABLE")),
        "p106_completion_acknowledged": p106.get("completion_acknowledged") is True,
        "p106_receipt_issued": p106.get("receipt_issued") is True,
        "p105_record_hash": str(pr.get("p105_record_hash", "NOT_COMPUTABLE")),
        "decision_value": str(cr.get("decision_value", "NOT_PROVIDED")),
        "decision_id": str(cr.get("decision_id", "NOT_PROVIDED")),
        "operator_id": str(cr.get("operator_id", "NOT_PROVIDED")),
        "advisory_only_confirmed": p106.get("advisory_only") is True,
        "completion_receipt_only_confirmed": p106.get("completion_receipt_only") is True,
        "segment_acknowledged": True,
        "autonomous_approval": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "approval_record_sealed": False,
        "execution_authority": False,
        "actual_finalization_executed": False,
    }


def _build_terminal_provenance_snapshot(p106: dict[str, Any]) -> dict[str, Any]:
    pr = p106.get("completion_provenance_reanchor", {})
    if not isinstance(pr, dict):
        pr = {}
    return {
        "p107_acknowledged_hash": "SELF",
        "p106_complete_hash": str(p106.get("finalization_decision_record_complete_hash", "NOT_COMPUTABLE")),
        "p105_record_hash": str(pr.get("p105_record_hash", "NOT_COMPUTABLE")),
        "p104_decision_hash": str(pr.get("p104_decision_hash", "NOT_COMPUTABLE")),
        "p103_review_hash": str(pr.get("p103_review_hash", "NOT_COMPUTABLE")),
        "p103_review_file_hash": str(pr.get("p103_review_file_hash", "NOT_COMPUTABLE")),
        "p103_review_passed": pr.get("p103_review_passed") is True,
        "p102_execution_hash_anchor": str(pr.get("p102_execution_hash_anchor", "NOT_COMPUTABLE")),
        "finalization_check_summary": pr.get("finalization_check_summary", {}),
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_acknowledged(
    *,
    repo_root: str | Path = ".",
    source_complete_path: str = SOURCE_COMPLETE_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_complete_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_decision_record_complete_acknowledged_status = _STATUS_NOT_COMPUTABLE
    recommended_next_lane = _NEXT_LANE_FALLBACK
    acknowledgment_issued = False
    segment_closed = False
    acknowledgment_blockers: list[str] = []
    acknowledgment_checks: list[dict[str, Any]] = []
    acknowledgment_receipt: dict[str, Any] = {}
    terminal_provenance_snapshot: dict[str, Any] = {}

    if source_payload is None:
        acknowledgment_blockers = [
            "source_complete_missing_or_unreadable",
            f"source_path:{source_complete_path}",
        ]
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("finalization_decision_record_complete_status", "NOT_COMPUTABLE")
        )

        acknowledgment_checks = _run_acknowledgment_checks(source_payload)
        checks_all_pass = all(c.get("passed") is True for c in acknowledgment_checks)

        lock_violation = any(
            "must_be_false:found_true" in v
            for c in acknowledgment_checks
            if c.get("check_id") == "source_authority_locks_clean"
            for v in c.get("violations", [])
        )

        autonomous_fail = not any(
            c.get("passed") is True
            for c in acknowledgment_checks
            if c.get("check_id") == "source_autonomous_approval_false"
        )

        if lock_violation or autonomous_fail:
            finalization_decision_record_complete_acknowledged_status = _STATUS_FAILED
            acknowledgment_blockers = [
                f"acknowledgment_check_failed:{c['check_id']}"
                for c in acknowledgment_checks
                if not c.get("passed")
            ]
        elif source_status != _SOURCE_REQUIRED_STATUS:
            finalization_decision_record_complete_acknowledged_status = _STATUS_BLOCKED
            acknowledgment_blockers = [
                f"source_complete_status:{source_status}",
                "source_not_complete",
            ]
        elif not checks_all_pass:
            finalization_decision_record_complete_acknowledged_status = _STATUS_FAILED
            acknowledgment_blockers = [
                f"acknowledgment_check_failed:{c['check_id']}"
                for c in acknowledgment_checks
                if not c.get("passed")
            ]
        else:
            finalization_decision_record_complete_acknowledged_status = _STATUS_ACKNOWLEDGED
            recommended_next_lane = _NEXT_LANE_ON_ACKNOWLEDGED
            acknowledgment_issued = True
            segment_closed = True
            acknowledgment_receipt = _build_acknowledgment_receipt(source_payload)
            terminal_provenance_snapshot = _build_terminal_provenance_snapshot(source_payload)

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "finalization_decision_record_complete_acknowledged_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_acknowledged_001"
        ),
        "source_complete_path": source_complete_path,
        "source_complete_hash": source_hash,
        "source_complete_status": source_status,
        "source_complete_observed": source_observed,
        "finalization_decision_record_complete_acknowledged_status": finalization_decision_record_complete_acknowledged_status,
        "acknowledgment_issued": acknowledgment_issued,
        "segment_closed": segment_closed,
        "acknowledgment_blockers": sorted(acknowledgment_blockers),
        "blockers": sorted(acknowledgment_blockers),
        "acknowledgment_checks": acknowledgment_checks,
        "acknowledgment_receipt": acknowledgment_receipt,
        "terminal_provenance_snapshot": terminal_provenance_snapshot,
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "acknowledgment_receipt_only": True,
        "finalization_decision_record_complete_acknowledged_only": True,
        "decision_record_only": True,
        "segment_terminal": True,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_complete_acknowledged(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
