from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationAuthorization.v1"
)

SOURCE_EXECUTION_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json"
)

_FINALIZATION_CHAIN_SOURCES: tuple[dict[str, str], ...] = (
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
    {
        "check_id": "p98_seal_execution_simulated_complete",
        "source": "out/temporal_continuity_operator_authorization_record_approval_record_seal_execution/latest.json",
        "status_field": "approval_record_seal_execution_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE",
    },
)

_AUTHORITY_LOCK_FIELDS: tuple[str, ...] = (
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
        "finalization_authorization_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _check_p98_execution_attestation(p98: dict[str, Any]) -> dict[str, Any]:
    simulated_only = p98.get("simulated_only") is True
    actual_not_executed = p98.get("actual_seal_executed") is False
    execution_recorded = p98.get("execution_recorded") is True
    sentinel_ok = False
    sentinel_raw = p98.get("simulated_sentinel_check")
    if isinstance(sentinel_raw, dict):
        sentinel_ok = sentinel_raw.get("check_passed") is True
    step_count = 0
    summary = p98.get("simulated_execution_summary")
    if isinstance(summary, dict):
        raw = summary.get("step_count_verified", 0)
        step_count = int(raw) if isinstance(raw, int) else 0
    attestation_valid = simulated_only and actual_not_executed and execution_recorded and sentinel_ok
    return {
        "simulated_only": simulated_only,
        "actual_seal_executed": not actual_not_executed,
        "execution_recorded": execution_recorded,
        "sentinel_check_passed": sentinel_ok,
        "step_count_verified": step_count,
        "attestation_valid": attestation_valid,
    }


def _build_decision_provenance_reanchor(p98: dict[str, Any]) -> dict[str, Any]:
    chain = p98.get("full_provenance_chain", {})
    if not isinstance(chain, dict):
        chain = {}
    decision_value = str(chain.get("decision_value", "NOT_COMPUTABLE"))
    autonomous_approval = chain.get("autonomous_approval")
    provenance_anchor_valid = (
        decision_value == "approve_seal_record" and autonomous_approval is False
    )
    return {
        "decision_id": str(chain.get("decision_id", "NOT_PROVIDED")),
        "operator_id": str(chain.get("operator_id", "NOT_PROVIDED")),
        "decision_value": decision_value,
        "autonomous_approval": autonomous_approval if autonomous_approval is not None else True,
        "p96_decision_hash": str(chain.get("p96_seal_operator_decision_hash", "NOT_COMPUTABLE")),
        "p97_execution_plan_hash": str(chain.get("p97_seal_execution_plan_hash", "NOT_COMPUTABLE")),
        "p98_execution_hash": str(p98.get("approval_record_seal_execution_hash", "NOT_COMPUTABLE")),
        "provenance_anchor_valid": provenance_anchor_valid,
    }


def _finalization_chain_verification(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in _FINALIZATION_CHAIN_SOURCES:
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


def _finalization_authority_invariant_checks(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in _FINALIZATION_CHAIN_SOURCES:
        p = root / spec["source"]
        payload = _load_json_dict(p)
        if payload is None:
            for field in _AUTHORITY_LOCK_FIELDS:
                results.append({
                    "check_id": f"{spec['check_id']}__{field}_is_false",
                    "passed": True,
                })
        else:
            for field in _AUTHORITY_LOCK_FIELDS:
                val = payload.get(field)
                results.append({
                    "check_id": f"{spec['check_id']}__{field}_is_false",
                    "passed": val is not True,
                })
    return results


def _check_p98_posture_violations(p98: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for field in _AUTHORITY_LOCK_FIELDS:
        if p98.get(field) is True:
            violations.append(f"p98_{field}_must_be_false:found_true")
    if p98.get("actual_seal_executed") is True:
        violations.append("p98_actual_seal_executed_must_be_false:found_true")
    return violations


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization(
    *,
    repo_root: str | Path = ".",
    source_execution_path: str = SOURCE_EXECUTION_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_execution_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_authorization_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P98_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION"
    )
    finalization_authorization_eligible = False
    eligibility_reasons: list[str] = []
    denial_reasons: list[str] = []
    blockers: list[str] = []
    finalization_chain_ver: list[dict[str, Any]] = []
    authority_invariant_checks: list[dict[str, Any]] = []
    p98_attestation: dict[str, Any] = {
        "simulated_only": False,
        "actual_seal_executed": True,
        "execution_recorded": False,
        "sentinel_check_passed": False,
        "step_count_verified": 0,
        "attestation_valid": False,
    }
    provenance_reanchor: dict[str, Any] = {}
    eligibility_summary: dict[str, Any] = {
        "eligible": False,
        "gate_only": True,
        "authorization_not_granted": True,
        "no_authority_elevated": True,
        "full_chain_verified_count": 0,
    }

    if source_payload is None:
        denial_reasons = [
            "source_execution_missing_or_unreadable",
            f"source_path:{source_execution_path}",
        ]
        blockers = list(denial_reasons)
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("approval_record_seal_execution_status", "NOT_COMPUTABLE")
        )

        posture_violations = _check_p98_posture_violations(source_payload)
        if posture_violations:
            finalization_authorization_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_FAILED"
            )
            denial_reasons = sorted(posture_violations)
            blockers = list(denial_reasons)
        elif source_status != (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE"
        ):
            finalization_authorization_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION"
            )
            denial_reasons = [f"source_execution_status:{source_status}"]
            blockers = list(denial_reasons)
        else:
            p98_attestation = _check_p98_execution_attestation(source_payload)
            provenance_reanchor = _build_decision_provenance_reanchor(source_payload)
            finalization_chain_ver = _finalization_chain_verification(root)
            authority_invariant_checks = _finalization_authority_invariant_checks(root)

            attestation_failures: list[str] = []
            if not p98_attestation["attestation_valid"]:
                if not p98_attestation["simulated_only"]:
                    attestation_failures.append("p98_simulated_only_must_be_true")
                if p98_attestation["actual_seal_executed"]:
                    attestation_failures.append("p98_actual_seal_executed_must_be_false")
                if not p98_attestation["execution_recorded"]:
                    attestation_failures.append("p98_execution_recorded_must_be_true")
                if not p98_attestation["sentinel_check_passed"]:
                    attestation_failures.append("p98_sentinel_check_must_pass")

            provenance_failures: list[str] = []
            if not provenance_reanchor.get("provenance_anchor_valid"):
                if provenance_reanchor.get("autonomous_approval") is not False:
                    provenance_failures.append(
                        "decision_provenance_autonomous_approval_must_be_false"
                    )
                if provenance_reanchor.get("decision_value") != "approve_seal_record":
                    provenance_failures.append(
                        f"decision_value_must_be_approve_seal_record:found_{provenance_reanchor.get('decision_value')}"
                    )

            invariant_failures = [
                c["check_id"] for c in authority_invariant_checks if not c.get("passed")
            ]

            all_failures = attestation_failures + provenance_failures + [
                f"invariant_failed:{f}" for f in invariant_failures
            ]

            if all_failures:
                finalization_authorization_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_FAILED"
                    if invariant_failures or p98_attestation.get("actual_seal_executed")
                    else "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION"
                )
                denial_reasons = sorted(all_failures)
                blockers = list(denial_reasons)
            else:
                full_chain_verified_count = sum(
                    1 for c in finalization_chain_ver if c.get("passed")
                )
                eligibility_summary = {
                    "eligible": True,
                    "gate_only": True,
                    "authorization_not_granted": True,
                    "no_authority_elevated": True,
                    "full_chain_verified_count": full_chain_verified_count,
                }
                eligibility_reasons = [
                    "P98_SIMULATED_COMPLETE",
                    "P98_EXECUTION_RECORDED",
                    "P98_SIMULATED_ONLY_CONFIRMED",
                    "P98_ACTUAL_SEAL_NOT_EXECUTED",
                    "P98_SENTINEL_CHECK_PASSED",
                    "DECISION_PROVENANCE_VALID",
                    "AUTHORITY_LOCKS_ALL_FALSE",
                ]
                finalization_authorization_eligible = True
                finalization_authorization_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE"
                )
                recommended_next_lane = (
                    "P100_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
                )

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "finalization_authorization_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_001"
        ),
        "source_execution_path": source_execution_path,
        "source_execution_hash": source_hash,
        "source_execution_status": source_status,
        "source_execution_observed": source_observed,
        "finalization_authorization_status": finalization_authorization_status,
        "finalization_authorization_eligible": finalization_authorization_eligible,
        "finalization_authorization_gate_only": True,
        "p98_execution_attestation": p98_attestation,
        "decision_provenance_reanchor": provenance_reanchor,
        "finalization_chain_verification": finalization_chain_ver,
        "finalization_authority_invariant_checks": authority_invariant_checks,
        "finalization_authorization_eligibility_summary": eligibility_summary,
        "eligibility_reasons": eligibility_reasons,
        "denial_reasons": sorted(denial_reasons),
        "blockers": sorted(blockers),
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
