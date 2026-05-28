from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationDecisionRecord.v1"
)

SOURCE_FINALIZATION_DECISION_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision/latest.json"
)

_SOURCE_REQUIRED_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_APPROVED_RECORD"
)

_STATUS_RECORD_READY = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_READY"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_FAILED"
)

_NEXT_LANE_ON_READY = (
    "P106_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION_RECORD_COMPLETE"
)
_NEXT_LANE_FALLBACK = (
    "P104_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION"
)

_REQUIRED_PROVENANCE_KEYS: tuple[str, ...] = (
    "finalization_review_hash",
    "finalization_review_file_hash",
    "finalization_review_id",
    "review_passed",
    "p102_finalization_execution_hash_anchor",
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
    "autonomous_approval",
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
        "finalization_decision_record_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _run_posture_checks(
    p104: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append({
        "check_id": "source_decision_status_is_approved_record",
        "passed": p104.get("approval_record_seal_finalization_decision_status") == _SOURCE_REQUIRED_STATUS,
    })

    decision_hash = str(p104.get("approval_record_seal_finalization_decision_hash", ""))
    checks.append({
        "check_id": "source_decision_hash_present",
        "passed": bool(decision_hash) and decision_hash != "NOT_COMPUTABLE",
    })

    checks.append({
        "check_id": "source_decision_recorded_true",
        "passed": p104.get("decision_recorded") is True,
    })

    checks.append({
        "check_id": "source_advisory_only_true",
        "passed": p104.get("advisory_only") is True,
    })

    checks.append({
        "check_id": "source_autonomous_approval_false",
        "passed": p104.get("autonomous_approval") is not True,
    })

    lock_violations: list[str] = []
    for field in _FORBIDDEN_AUTHORITY_FIELDS:
        if p104.get(field) is True:
            lock_violations.append(f"p104_{field}_must_be_false:found_true")
    checks.append({
        "check_id": "source_authority_locks_clean",
        "passed": len(lock_violations) == 0,
        "violations": lock_violations,
    })

    odr = p104.get("operator_decision_record", {})
    if not isinstance(odr, dict):
        odr = {}
    checks.append({
        "check_id": "odr_decision_value_is_approve",
        "passed": odr.get("decision_value") == _REQUIRED_ODR_DECISION_VALUE,
    })

    checks.append({
        "check_id": "odr_upstream_review_hash_match_true",
        "passed": odr.get("upstream_review_hash_match") is True,
    })

    provenance = p104.get("upstream_provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}
    missing_keys = [k for k in _REQUIRED_PROVENANCE_KEYS if k not in provenance]
    checks.append({
        "check_id": "provenance_chain_complete",
        "passed": len(missing_keys) == 0,
        "missing_keys": missing_keys,
    })

    checks.append({
        "check_id": "odr_autonomous_approval_false",
        "passed": odr.get("autonomous_approval") is not True,
    })

    return checks


def _build_decision_record_struct(
    p104: dict[str, Any],
) -> dict[str, Any]:
    odr = p104.get("operator_decision_record", {})
    if not isinstance(odr, dict):
        odr = {}
    return {
        "decision_value": str(odr.get("decision_value", "NOT_PROVIDED")),
        "decision_id": str(odr.get("decision_id", "NOT_PROVIDED")),
        "operator_id": str(odr.get("operator_id", "NOT_PROVIDED")),
        "decision_scope": str(odr.get("decision_scope", "NOT_PROVIDED")),
        "upstream_review_hash_match": odr.get("upstream_review_hash_match") is True,
        "advisory_only_acknowledged": odr.get("advisory_only_acknowledged") is True,
        "no_execution_authority_granted_acknowledged": odr.get("no_execution_authority_granted_acknowledged") is True,
        "no_seal_executed_acknowledged": odr.get("no_seal_executed_acknowledged") is True,
        "finalization_not_executed_acknowledged": odr.get("finalization_not_executed_acknowledged") is True,
        "finalization_decision_record_only_acknowledged": odr.get("finalization_decision_record_only_acknowledged") is True,
        "p104_decision_hash_anchor": str(p104.get("approval_record_seal_finalization_decision_hash", "NOT_COMPUTABLE")),
        "autonomous_approval": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "approval_record_sealed": False,
        "execution_authority": False,
        "actual_finalization_executed": False,
    }


def _build_provenance_chain(p104: dict[str, Any]) -> dict[str, Any]:
    provenance = p104.get("upstream_provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}
    return {
        "p104_decision_hash": str(p104.get("approval_record_seal_finalization_decision_hash", "NOT_COMPUTABLE")),
        "p103_review_hash": str(provenance.get("finalization_review_hash", "NOT_COMPUTABLE")),
        "p103_review_file_hash": str(provenance.get("finalization_review_file_hash", "NOT_COMPUTABLE")),
        "p103_review_id": str(provenance.get("finalization_review_id", "NOT_COMPUTABLE")),
        "p103_review_passed": provenance.get("review_passed") is True,
        "p102_execution_hash_anchor": str(provenance.get("p102_finalization_execution_hash_anchor", "NOT_COMPUTABLE")),
        "finalization_check_summary": provenance.get("finalization_check_summary", {}),
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record(
    *,
    repo_root: str | Path = ".",
    source_finalization_decision_path: str = SOURCE_FINALIZATION_DECISION_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_finalization_decision_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_decision_record_status = _STATUS_NOT_COMPUTABLE
    recommended_next_lane = _NEXT_LANE_FALLBACK
    decision_record_ready = False
    record_blockers: list[str] = []
    posture_checks: list[dict[str, Any]] = []
    finalization_decision_record: dict[str, Any] = {}
    finalization_decision_provenance_chain: dict[str, Any] = {}

    if source_payload is None:
        record_blockers = [
            "source_decision_missing_or_unreadable",
            f"source_path:{source_finalization_decision_path}",
        ]
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("approval_record_seal_finalization_decision_status", "NOT_COMPUTABLE")
        )

        posture_checks = _run_posture_checks(source_payload)
        checks_all_pass = all(c.get("passed") is True for c in posture_checks)

        lock_violation = any(
            "must_be_false:found_true" in v
            for c in posture_checks
            if c.get("check_id") == "source_authority_locks_clean"
            for v in c.get("violations", [])
        )

        autonomous_fail = not any(
            c.get("passed") is True
            for c in posture_checks
            if c.get("check_id") == "source_autonomous_approval_false"
        ) or not any(
            c.get("passed") is True
            for c in posture_checks
            if c.get("check_id") == "odr_autonomous_approval_false"
        )

        if lock_violation or autonomous_fail:
            finalization_decision_record_status = _STATUS_FAILED
            record_blockers = [
                f"posture_check_failed:{c['check_id']}"
                for c in posture_checks
                if not c.get("passed")
            ]
        elif source_status != _SOURCE_REQUIRED_STATUS:
            finalization_decision_record_status = _STATUS_BLOCKED
            record_blockers = [
                f"source_decision_status:{source_status}",
                "source_decision_not_approved_record",
            ]
        elif not checks_all_pass:
            finalization_decision_record_status = _STATUS_FAILED
            record_blockers = [
                f"posture_check_failed:{c['check_id']}"
                for c in posture_checks
                if not c.get("passed")
            ]
        else:
            finalization_decision_record_status = _STATUS_RECORD_READY
            recommended_next_lane = _NEXT_LANE_ON_READY
            decision_record_ready = True
            finalization_decision_record = _build_decision_record_struct(source_payload)
            finalization_decision_provenance_chain = _build_provenance_chain(source_payload)

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "finalization_decision_record_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record_001"
        ),
        "source_finalization_decision_path": source_finalization_decision_path,
        "source_finalization_decision_hash": source_hash,
        "source_finalization_decision_status": source_status,
        "source_finalization_decision_observed": source_observed,
        "finalization_decision_record_status": finalization_decision_record_status,
        "decision_record_ready": decision_record_ready,
        "record_blockers": sorted(record_blockers),
        "blockers": sorted(record_blockers),
        "posture_checks": posture_checks,
        "finalization_decision_record": finalization_decision_record,
        "finalization_decision_provenance_chain": finalization_decision_provenance_chain,
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "finalization_decision_record_only": True,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_decision_record(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
