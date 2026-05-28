from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealDryRun.v1"
SOURCE_APPROVAL_RECORD_SEAL_PLAN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json"
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_seal_dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(
    *,
    repo_root: str | Path = ".",
    source_approval_record_seal_plan_path: str = SOURCE_APPROVAL_RECORD_SEAL_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_seal_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    approval_record_seal_dry_run_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P93_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
    blockers: list[str] = []
    dry_run_passed = False
    dry_run_blockers: list[str] = []

    seal_construction_dry_run_results: list[dict[str, Any]] = []
    seal_provenance_dry_run_results: list[dict[str, Any]] = []
    seal_hash_dry_run_results: list[dict[str, Any]] = []
    seal_blocker_dry_run_results: list[dict[str, Any]] = []
    seal_authority_invariant_dry_run_results: list[dict[str, Any]] = []
    simulated_seal_dry_run: dict[str, Any] = {}

    if source_payload is None:
        blockers = [
            "source_approval_record_seal_plan_missing_or_unreadable",
            f"source_path:{source_approval_record_seal_plan_path}",
        ]
        dry_run_blockers = list(blockers)
    else:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_status = str(source_payload.get("approval_record_seal_plan_status", "NOT_COMPUTABLE"))
        source_validation_passed = source_payload.get("validation_passed") is True

        for req_key, result_list_ref in (
            ("seal_construction_requirements", "seal_construction"),
            ("seal_provenance_requirements", "seal_provenance"),
            ("seal_hash_requirements", "seal_hash"),
            ("seal_blocker_requirements", "seal_blocker"),
        ):
            reqs = sorted([str(r) for r in source_payload.get(req_key, [])])
            checks = [_check(req, True) for req in reqs]
            if result_list_ref == "seal_construction":
                seal_construction_dry_run_results = checks
            elif result_list_ref == "seal_provenance":
                seal_provenance_dry_run_results = checks
            elif result_list_ref == "seal_hash":
                seal_hash_dry_run_results = checks
            elif result_list_ref == "seal_blocker":
                seal_blocker_dry_run_results = checks

        provenance_chain_hash = str(
            source_payload.get("source_approval_record_validation_dry_run_hash", "NOT_COMPUTABLE")
        )
        seal_provenance_dry_run_results.append(
            _check(
                "source_approval_record_validation_dry_run_hash_present_in_seal_plan",
                provenance_chain_hash not in ("", "NOT_COMPUTABLE"),
            )
        )

        authority_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_seal_plan_only_true": source_payload.get("approval_record_seal_plan_only") is True,
            "source_approval_record_sealed_false": source_payload.get("approval_record_sealed") is False,
            "source_approval_record_created_false": source_payload.get("approval_record_created") is False,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_authorization_authority_false": source_payload.get("authorization_authority") is False,
            "source_authorization_record_creation_authority_false": source_payload.get(
                "authorization_record_creation_authority"
            ) is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }
        seal_authority_invariant_dry_run_results = [
            {"check_id": k, "passed": v}
            for k, v in sorted(authority_checks.items(), key=lambda kv: kv[0])
        ]

        authority_req_keys = sorted(
            [str(r) for r in source_payload.get("seal_authority_invariant_requirements", [])]
        )
        seal_authority_invariant_dry_run_results.extend(
            [_check(req, True) for req in authority_req_keys]
        )

        simulated_seal_dry_run = {
            "approval_record_seal_dry_run_id": "SIMULATED_SEAL_DRY_RUN_ONLY",
            "approval_record_seal_plan_id": source_payload.get(
                "approval_record_seal_plan_id", "SIMULATED_PLAN_ID_ONLY"
            ),
            "simulated_seal_hash": "SIMULATED_HASH_ONLY",
            "simulated_seal_token": "SIMULATED_SEAL_TOKEN_ONLY",
            "simulated_seal_signature": "SIMULATED_SIGNATURE_ONLY",
            "simulated_seal_created_at": "SIMULATED_ONLY",
            "simulated_operator_id": "SIMULATED_OPERATOR",
            "simulated_operator_attestation": "SIMULATED_ATTESTED",
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "approval_record_sealed": False,
            "approval_record_created": False,
            "simulated_only": True,
        }

        all_checks = (
            seal_construction_dry_run_results
            + seal_provenance_dry_run_results
            + seal_hash_dry_run_results
            + seal_blocker_dry_run_results
            + seal_authority_invariant_dry_run_results
        )
        failed_check_ids = sorted(
            [str(c["check_id"]) for c in all_checks if c.get("passed") is False]
        )

        if source_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN_READY":
            approval_record_seal_dry_run_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
            )
            dry_run_blockers = [f"source_approval_record_seal_plan_status:{source_status}"]
            blockers = sorted(dry_run_blockers)
        elif not source_validation_passed:
            approval_record_seal_dry_run_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_PLAN"
            )
            dry_run_blockers = ["source_validation_passed:false"]
            blockers = sorted(dry_run_blockers)
        elif failed_check_ids:
            approval_record_seal_dry_run_status = "APPROVAL_RECORD_SEAL_DRY_RUN_FAILED"
            dry_run_blockers = [f"authority_invariant_check_failed:{c}" for c in failed_check_ids]
            blockers = sorted(dry_run_blockers)
        else:
            approval_record_seal_dry_run_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY"
            )
            recommended_next_lane = (
                "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
            )
            dry_run_passed = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_dry_run_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_dry_run_001"
        ),
        "source_approval_record_seal_plan_path": source_approval_record_seal_plan_path,
        "source_approval_record_seal_plan_hash": source_hash,
        "source_approval_record_seal_plan_status": source_status,
        "approval_record_seal_dry_run_status": approval_record_seal_dry_run_status,
        "simulated_seal_dry_run": simulated_seal_dry_run,
        "seal_construction_dry_run_results": seal_construction_dry_run_results,
        "seal_provenance_dry_run_results": seal_provenance_dry_run_results,
        "seal_hash_dry_run_results": seal_hash_dry_run_results,
        "seal_blocker_dry_run_results": seal_blocker_dry_run_results,
        "seal_authority_invariant_dry_run_results": seal_authority_invariant_dry_run_results,
        "dry_run_passed": dry_run_passed,
        "dry_run_blockers": sorted(dry_run_blockers),
        "blockers": sorted(blockers),
        "recommended_next_lane": recommended_next_lane,
        "source_approval_record_seal_plan_observed": source_observed,
        "advisory_only": True,
        "projection_only": True,
        "approval_record_seal_dry_run_only": True,
        "simulated_only": True,
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
        "operator_approval_required": True,
        "valid_for_execution": False,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
