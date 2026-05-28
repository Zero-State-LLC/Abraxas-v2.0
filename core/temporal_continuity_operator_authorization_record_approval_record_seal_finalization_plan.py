from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationPlan.v1"
)

SOURCE_P100_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record/latest.json"
)

_SOURCE_REQUIRED_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD"
)

_FORBIDDEN_AUTHORITY_FIELDS: tuple[str, ...] = (
    "authorization_granted",
    "finalization_authorized",
    "approval_record_sealed",
    "valid_for_execution",
    "execution_authority",
    "token_minting_allowed",
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
        "approval_record_seal_finalization_plan_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan(
    *,
    repo_root: str | Path = ".",
    source_p100_path: str = SOURCE_P100_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p100_path = root / source_p100_path
    source_observed = p100_path.exists()
    source_payload = _load_json_dict(p100_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_plan_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P100_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
    )
    plan_ready = False
    plan_blockers: list[str] = []
    p100_authorization_record_hash_anchor = "NOT_COMPUTABLE"
    p100_authorization_id_anchor = "NOT_COMPUTABLE"
    p100_operator_id_anchor = "NOT_COMPUTABLE"
    p100_authorization_value_anchor = "NOT_COMPUTABLE"
    p96_decision_provenance_reanchor: dict[str, Any] = {}

    finalization_plan_summary: dict[str, Any] = {
        "all_steps_advisory": True,
        "finalization_authority_required_externally": True,
        "finalization_plan_only": True,
        "seal_not_executed": True,
        "finalization_not_executed": True,
        "step_count": 5,
    }
    plan_only_attestation: dict[str, Any] = {
        "no_finalization_executed": True,
        "no_execution_authority_created": True,
        "no_seal_executed": True,
        "plan_preparation_only": True,
    }

    if source_payload is None:
        plan_blockers = [
            "source_p100_missing_or_unreadable",
            f"source_path:{source_p100_path}",
        ]
    else:
        source_hash = _file_sha256(p100_path)
        source_status = str(
            source_payload.get("finalization_authorization_record_status", "NOT_COMPUTABLE")
        )
        p100_authorization_record_hash_anchor = str(
            source_payload.get("finalization_authorization_record_hash", "NOT_COMPUTABLE")
        )
        p100_authorization_id_anchor = str(
            source_payload.get("authorization_id", "NOT_COMPUTABLE")
        )
        p100_operator_id_anchor = str(
            source_payload.get("operator_id", "NOT_COMPUTABLE")
        )
        p100_authorization_value_anchor = str(
            source_payload.get("authorization_value", "NOT_COMPUTABLE")
        )
        reanchor = source_payload.get("p96_decision_provenance_reanchor", {})
        p96_decision_provenance_reanchor = reanchor if isinstance(reanchor, dict) else {}

        lock_violations: list[str] = []
        for field in _FORBIDDEN_AUTHORITY_FIELDS:
            if source_payload.get(field) is True:
                lock_violations.append(f"source_p100_{field}_must_be_false:found_true")

        if lock_violations:
            finalization_plan_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_FAILED"
            )
            plan_blockers = sorted(lock_violations)
        else:
            autonomous = (
                p96_decision_provenance_reanchor.get("autonomous_approval") is True
            )
            authorization_recorded_ok = source_payload.get("authorization_recorded") is True
            status_ok = source_status == _SOURCE_REQUIRED_STATUS

            if not status_ok or not authorization_recorded_ok:
                finalization_plan_status = (
                    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
                )
                if not status_ok:
                    plan_blockers.append(f"source_p100_status:{source_status}")
                if not authorization_recorded_ok:
                    plan_blockers.append(
                        f"authorization_recorded_must_be_true:found_{source_payload.get('authorization_recorded')!r}"
                    )
                plan_blockers = sorted(plan_blockers)
            elif autonomous:
                finalization_plan_status = (
                    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
                )
                plan_blockers = ["p96_autonomous_approval_must_be_false:found_true"]
            else:
                finalization_plan_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_READY"
                )
                recommended_next_lane = (
                    "P102_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
                )
                plan_ready = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_finalization_plan_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan_001"
        ),
        "source_p100_path": source_p100_path,
        "source_p100_hash": source_hash,
        "source_p100_status": source_status,
        "source_p100_observed": source_observed,
        "finalization_plan_status": finalization_plan_status,
        "plan_ready": plan_ready,
        "plan_blockers": sorted(plan_blockers),
        "finalization_plan_summary": finalization_plan_summary,
        "plan_only_attestation": plan_only_attestation,
        "p100_authorization_record_hash_anchor": p100_authorization_record_hash_anchor,
        "p100_authorization_id_anchor": p100_authorization_id_anchor,
        "p100_operator_id_anchor": p100_operator_id_anchor,
        "p100_authorization_value_anchor": p100_authorization_value_anchor,
        "p96_decision_provenance_reanchor": p96_decision_provenance_reanchor,
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "finalization_plan_only": True,
        "approval_record_seal_finalization_plan_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "execution_authority": False,
        "authorization_authority": False,
        "plan_creation_authority": False,
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
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
