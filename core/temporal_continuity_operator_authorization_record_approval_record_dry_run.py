from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordDryRun.v1"
SOURCE_APPROVAL_RECORD_PLAN_PATH = "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.json"


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_dry_run_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _bool_check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_temporal_continuity_operator_authorization_record_approval_record_dry_run(
    *, repo_root: str | Path = ".", source_approval_record_plan_path: str = SOURCE_APPROVAL_RECORD_PLAN_PATH
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_plan_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_approval_record_plan_hash = "NOT_COMPUTABLE"
    source_approval_record_plan_status = "NOT_COMPUTABLE"
    approval_record_dry_run_status = "NOT_COMPUTABLE"
    recommended_next_lane = "P89_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN"
    blockers: list[str] = []

    simulated_approval_record: dict[str, Any] = {}
    record_construction_dry_run_results: list[dict[str, Any]] = []
    provenance_hash_seal_dry_run_results: list[dict[str, Any]] = []
    approval_record_blockers: list[str] = []

    if source_payload is None:
        blockers = [
            "source_approval_record_plan_missing_or_unreadable",
            f"source_path:{source_approval_record_plan_path}",
        ]
    else:
        source_approval_record_plan_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_approval_record_plan_status = str(source_payload.get("approval_record_plan_status", "NOT_COMPUTABLE"))

        required_fields = source_payload.get("required_approval_record_fields", {})
        simulated_approval_record = {
            "approval_record_id": "SIMULATED_APPROVAL_RECORD_ONLY",
            "approval_record_schema_version": "simulated.v1",
            "approval_record_created_at": "SIMULATED_ONLY",
            "source_approval_validation_dry_run_path": source_payload.get("source_approval_validation_dry_run_path"),
            "source_approval_validation_dry_run_hash": source_payload.get("source_approval_validation_dry_run_hash"),
            "source_approval_validation_dry_run_status": source_payload.get("source_approval_validation_dry_run_status"),
            "operator_id": "SIMULATED_OPERATOR",
            "operator_acknowledgement": "SIMULATED_ACKNOWLEDGED",
            "operator_attestation": "SIMULATED_ATTESTED",
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "approval_record_hash": "SIMULATED_HASH_ONLY",
            "approval_record_seal": "SIMULATED_SEAL_ONLY",
            "approval_record_signature": "SIMULATED_SIGNATURE_ONLY",
        }

        record_construction_dry_run_results = sorted(
            [
                _bool_check("required_field_groups_present", isinstance(required_fields, dict) and len(required_fields) > 0),
                _bool_check("simulated_approval_record_generated", bool(simulated_approval_record)),
                _bool_check("approval_record_created_false", source_payload.get("approval_record_created") is False),
                _bool_check(
                    "approval_record_creation_authority_false",
                    source_payload.get("approval_record_creation_authority") is False,
                ),
            ],
            key=lambda item: str(item["check_id"]),
        )

        provenance_hash_seal_dry_run_results = sorted(
            [
                _bool_check("source_approval_record_plan_hash_present", source_approval_record_plan_hash != "NOT_COMPUTABLE"),
                _bool_check(
                    "source_approval_validation_dry_run_hash_present",
                    str(source_payload.get("source_approval_validation_dry_run_hash", "")).strip() not in {"", "NOT_COMPUTABLE"},
                ),
                _bool_check("approval_record_plan_hash_present", str(source_payload.get("approval_record_plan_hash", "")).strip() != ""),
            ],
            key=lambda item: str(item["check_id"]),
        )

        governance_checks = {
            "source_advisory_only_true": source_payload.get("advisory_only") is True,
            "source_projection_only_true": source_payload.get("projection_only") is True,
            "source_approval_record_plan_only_true": source_payload.get("approval_record_plan_only") is True,
            "source_approval_record_created_false": source_payload.get("approval_record_created") is False,
            "source_approval_granted_false": source_payload.get("approval_granted") is False,
            "source_authorization_granted_false": source_payload.get("authorization_granted") is False,
            "source_execution_authority_false": source_payload.get("execution_authority") is False,
            "source_token_minting_allowed_false": source_payload.get("token_minting_allowed") is False,
            "source_valid_for_execution_false": source_payload.get("valid_for_execution") is False,
        }
        provenance_hash_seal_dry_run_results.extend(
            [{"check_id": k, "passed": v} for k, v in sorted(governance_checks.items(), key=lambda kv: kv[0])]
        )

        if source_approval_record_plan_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN_READY":
            approval_record_dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN"
            blockers = [f"source_approval_record_plan_status:{source_approval_record_plan_status}"]
            approval_record_blockers = list(blockers)
        elif not all(governance_checks.values()):
            approval_record_dry_run_status = "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_PLAN"
            approval_record_blockers = [
                f"governance_invariant_failed:{k}" for k, v in sorted(governance_checks.items()) if not v
            ]
            blockers = sorted(approval_record_blockers)
        else:
            approval_record_dry_run_status = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_DRY_RUN_READY"
            recommended_next_lane = "P91_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_VALIDATION_PLAN"

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_dry_run_id": "temporal_continuity_operator_authorization_record_approval_record_dry_run_001",
        "source_approval_record_plan_path": source_approval_record_plan_path,
        "source_approval_record_plan_hash": source_approval_record_plan_hash,
        "source_approval_record_plan_status": source_approval_record_plan_status,
        "approval_record_dry_run_status": approval_record_dry_run_status,
        "simulated_approval_record": simulated_approval_record,
        "record_construction_dry_run_results": record_construction_dry_run_results,
        "provenance_hash_seal_dry_run_results": provenance_hash_seal_dry_run_results,
        "approval_record_blockers": sorted(approval_record_blockers),
        "recommended_next_lane": recommended_next_lane,
        "blockers": sorted(blockers),
        "advisory_only": True,
        "projection_only": True,
        "approval_record_dry_run_only": True,
        "simulated_only": True,
        "approval_record_created": False,
        "approval_record_creation_authority": False,
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
        "source_approval_record_plan_observed": source_observed,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
