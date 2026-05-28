from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealExecution.v1"

SOURCE_EXECUTION_PLAN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan/latest.json"
)

_SIMULATED_SEAL_EXECUTION_RECORD: dict[str, Any] = {
    "simulated_execution_id": "SIMULATED_EXECUTION_ONLY",
    "simulated_execution_hash": "SIMULATED_EXECUTION_HASH_ONLY",
    "simulated_execution_token": "SIMULATED_EXECUTION_TOKEN_ONLY",
    "simulated_execution_signature": "SIMULATED_EXECUTION_SIGNATURE_ONLY",
    "simulated_execution_completed_at": "SIMULATED_ONLY",
    "simulated_operator_id": "SIMULATED_OPERATOR",
    "simulated_operator_attestation": "SIMULATED_ATTESTED",
    "approval_record_sealed": False,
    "approval_granted": False,
    "execution_authority": False,
    "token_minting_allowed": False,
    "valid_for_execution": False,
    "actual_seal_executed": False,
    "simulated_only": True,
}

_SIMULATED_SENTINEL_FIELDS: tuple[str, ...] = (
    "simulated_execution_id",
    "simulated_execution_hash",
    "simulated_execution_token",
    "simulated_execution_signature",
    "simulated_execution_completed_at",
)

_EXECUTION_CHAIN_SOURCES: tuple[dict[str, str], ...] = (
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
    {
        "check_id": "p96_seal_operator_decision_approved",
        "source": "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision/latest.json",
        "status_field": "approval_record_seal_operator_decision_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
    },
    {
        "check_id": "p97_seal_execution_plan_ready",
        "source": "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution_plan/latest.json",
        "status_field": "approval_record_seal_execution_plan_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY",
    },
)

_AUTHORITY_LOCK_FIELDS_TO_CHECK: tuple[str, ...] = (
    "approval_granted",
    "approval_record_sealed",
    "authorization_granted",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
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
        "approval_record_seal_execution_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _check_simulated_sentinels(record: dict[str, Any]) -> dict[str, Any]:
    sentinel_strings_ok = all(
        isinstance(record.get(f), str) and "SIMULATED" in record.get(f, "")
        for f in _SIMULATED_SENTINEL_FIELDS
    )
    simulated_only_set = record.get("simulated_only") is True
    actual_not_executed = record.get("actual_seal_executed") is False
    approval_not_sealed = record.get("approval_record_sealed") is False
    all_pass = sentinel_strings_ok and simulated_only_set and actual_not_executed and approval_not_sealed
    return {
        "sentinel_strings_all_contain_simulated_marker": sentinel_strings_ok,
        "simulated_only_flag_set": simulated_only_set,
        "actual_seal_executed_is_false": actual_not_executed,
        "approval_record_sealed_is_false": approval_not_sealed,
        "check_passed": all_pass,
    }


def _execution_chain_verification(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in _EXECUTION_CHAIN_SOURCES:
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


def _execution_authority_invariant_checks(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in _EXECUTION_CHAIN_SOURCES:
        p = root / spec["source"]
        payload = _load_json_dict(p)
        if payload is None:
            for field in _AUTHORITY_LOCK_FIELDS_TO_CHECK:
                results.append({
                    "check_id": f"{spec['check_id']}__{field}_is_false",
                    "passed": True,
                })
        else:
            for field in _AUTHORITY_LOCK_FIELDS_TO_CHECK:
                val = payload.get(field)
                results.append({
                    "check_id": f"{spec['check_id']}__{field}_is_false",
                    "passed": val is not True,
                })
    return results


def _check_p97_posture(p97: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for field in _AUTHORITY_LOCK_FIELDS_TO_CHECK:
        if p97.get(field) is True:
            violations.append(f"p97_{field}_must_be_false:found_true")
    summary = p97.get("seal_execution_plan_summary", {})
    if not isinstance(summary, dict):
        violations.append("p97_seal_execution_plan_summary_malformed")
    else:
        if summary.get("seal_not_executed") is not True:
            violations.append("p97_seal_execution_plan_summary_seal_not_executed_must_be_true")
        if summary.get("all_steps_advisory") is not True:
            violations.append("p97_seal_execution_plan_summary_all_steps_advisory_must_be_true")
    att = p97.get("plan_only_attestation", {})
    if not isinstance(att, dict):
        violations.append("p97_plan_only_attestation_malformed")
    else:
        if att.get("no_seal_executed") is not True:
            violations.append("p97_plan_only_attestation_no_seal_executed_must_be_true")
        if att.get("no_approval_granted") is not True:
            violations.append("p97_plan_only_attestation_no_approval_granted_must_be_true")
    return violations


def _build_full_provenance_chain(p97: dict[str, Any], p97_file_hash: str) -> dict[str, Any]:
    anchor = p97.get("decision_provenance_anchor", {})
    if not isinstance(anchor, dict):
        anchor = {}
    return {
        "p93_seal_plan_hash": "NOT_COMPUTABLE",
        "p94_seal_dry_run_hash": "NOT_COMPUTABLE",
        "p95_seal_operator_review_hash": anchor.get("review_hash", "NOT_COMPUTABLE"),
        "p96_seal_operator_decision_hash": anchor.get("decision_hash", "NOT_COMPUTABLE"),
        "p97_seal_execution_plan_hash": str(
            p97.get("approval_record_seal_execution_plan_hash", "NOT_COMPUTABLE")
        ),
        "p97_seal_execution_plan_file_hash": p97_file_hash,
        "decision_id": anchor.get("decision_id", "NOT_PROVIDED"),
        "operator_id": anchor.get("operator_id", "NOT_PROVIDED"),
        "decision_value": anchor.get("decision_value", "NOT_COMPUTABLE"),
        "autonomous_approval": False,
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_execution(
    *,
    repo_root: str | Path = ".",
    source_execution_plan_path: str = SOURCE_EXECUTION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_execution_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    approval_record_seal_execution_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P97_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN"
    )
    execution_recorded = False
    execution_blockers: list[str] = []
    simulated_seal_execution_record: dict[str, Any] = {}
    simulated_sentinel_check: dict[str, Any] = {}
    execution_chain_ver: list[dict[str, Any]] = []
    authority_invariant_checks: list[dict[str, Any]] = []
    full_provenance_chain: dict[str, Any] = {}
    simulated_execution_summary: dict[str, Any] = {
        "simulated_only": True,
        "actual_seal_executed": False,
        "approval_record_sealed": False,
        "execution_authority_granted": False,
        "step_count_verified": 0,
    }

    if source_payload is None:
        execution_blockers = [
            "source_execution_plan_missing_or_unreadable",
            f"source_path:{source_execution_plan_path}",
        ]
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("approval_record_seal_execution_plan_status", "NOT_COMPUTABLE")
        )
        full_provenance_chain = _build_full_provenance_chain(source_payload, source_hash)

        posture_violations = _check_p97_posture(source_payload)
        if posture_violations:
            approval_record_seal_execution_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_FAILED"
            )
            execution_blockers = sorted(posture_violations)
        elif source_status != (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY"
        ):
            approval_record_seal_execution_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN"
            )
            execution_blockers = [f"source_execution_plan_status:{source_status}"]
        elif source_payload.get("plan_ready") is not True:
            approval_record_seal_execution_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN"
            )
            execution_blockers = ["source_plan_ready:false"]
        else:
            execution_chain_ver = _execution_chain_verification(root)
            authority_invariant_checks = _execution_authority_invariant_checks(root)

            simulated_seal_execution_record = dict(_SIMULATED_SEAL_EXECUTION_RECORD)
            simulated_sentinel_check = _check_simulated_sentinels(simulated_seal_execution_record)

            if not simulated_sentinel_check.get("check_passed"):
                approval_record_seal_execution_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_FAILED"
                )
                execution_blockers = [
                    f"simulated_sentinel_check_failed:{k}"
                    for k, v in simulated_sentinel_check.items()
                    if v is False
                ]
            else:
                invariant_failures = [
                    c["check_id"] for c in authority_invariant_checks if not c.get("passed")
                ]
                if invariant_failures:
                    approval_record_seal_execution_status = (
                        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_FAILED"
                    )
                    execution_blockers = [
                        f"execution_authority_invariant_failed:{f}" for f in invariant_failures
                    ]
                else:
                    step_count_verified = sum(
                        1 for c in execution_chain_ver if c.get("passed")
                    )
                    simulated_execution_summary = {
                        "simulated_only": True,
                        "actual_seal_executed": False,
                        "approval_record_sealed": False,
                        "execution_authority_granted": False,
                        "step_count_verified": step_count_verified,
                    }
                    approval_record_seal_execution_status = (
                        "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE"
                    )
                    recommended_next_lane = (
                        "P99_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION"
                    )
                    execution_recorded = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_execution_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_execution_001"
        ),
        "source_execution_plan_path": source_execution_plan_path,
        "source_execution_plan_hash": source_hash,
        "source_execution_plan_status": source_status,
        "source_execution_plan_observed": source_observed,
        "approval_record_seal_execution_status": approval_record_seal_execution_status,
        "simulated_only": True,
        "actual_seal_executed": False,
        "execution_recorded": execution_recorded,
        "simulated_seal_execution_record": simulated_seal_execution_record,
        "simulated_sentinel_check": simulated_sentinel_check,
        "execution_chain_verification": execution_chain_ver,
        "execution_authority_invariant_checks": authority_invariant_checks,
        "full_provenance_chain": full_provenance_chain,
        "simulated_execution_summary": simulated_execution_summary,
        "execution_blockers": sorted(execution_blockers),
        "blockers": sorted(execution_blockers),
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "simulated_execution_only": True,
        "approval_record_seal_execution_only": True,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_execution(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
