from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationAuthorizationRecord.v1"
)

SOURCE_GATE_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization/latest.json"
)

DEFAULT_HUMAN_ARTIFACT_PATH = (
    "input/operator_authorization_record_approval_record_seal_finalization_authorization.json"
)

_VALID_AUTHORIZATION_VALUES: frozenset[str] = frozenset(
    {"authorize_finalization_record", "reject_finalization_authorization"}
)

_REQUIRED_ACKNOWLEDGEMENTS: tuple[str, ...] = (
    "advisory_only_acknowledged",
    "no_execution_authority_granted_acknowledged",
    "no_seal_executed_acknowledged",
    "finalization_not_executed_acknowledged",
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
        "finalization_authorization_record_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _validate_human_authorization_artifact(
    artifact: dict[str, Any],
    source_gate_file_hash: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    audit: list[dict[str, Any]] = []
    violations: list[str] = []

    gate_hash_match = str(artifact.get("upstream_gate_hash", "")) == source_gate_file_hash
    audit.append({"check_id": "upstream_gate_hash_matches_p99_file", "passed": gate_hash_match})
    if not gate_hash_match:
        violations.append(
            f"upstream_gate_hash_mismatch:declared={artifact.get('upstream_gate_hash')!r}"
        )

    for ack in _REQUIRED_ACKNOWLEDGEMENTS:
        ok = artifact.get(ack) is True
        audit.append({"check_id": f"{ack}_true", "passed": ok})
        if not ok:
            violations.append(f"{ack}_must_be_true:found_{artifact.get(ack)!r}")

    auth_val = str(artifact.get("authorization", ""))
    auth_recognized = auth_val in _VALID_AUTHORIZATION_VALUES
    audit.append({"check_id": "authorization_value_recognized", "passed": auth_recognized})
    if not auth_recognized:
        violations.append(f"unrecognized_authorization_value:{auth_val!r}")

    locks_clean = True
    for field in _FORBIDDEN_AUTHORITY_FIELDS:
        if artifact.get(field) is True:
            locks_clean = False
            violations.append(f"human_artifact_{field}_must_be_false:found_true")
    audit.append({"check_id": "human_artifact_authority_locks_clean", "passed": locks_clean})

    return audit, violations


def _check_p99_posture_violations(p99: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for field in _FORBIDDEN_AUTHORITY_FIELDS:
        if p99.get(field) is True:
            violations.append(f"p99_{field}_must_be_false:found_true")
    return violations


def _build_finalization_authorization_record(
    artifact: dict[str, Any],
    gate_hash_match: bool,
) -> dict[str, Any]:
    return {
        "authorization_value": str(artifact.get("authorization", "NOT_PROVIDED")),
        "authorization_id": str(artifact.get("authorization_id", "NOT_PROVIDED")),
        "authorization_scope": str(artifact.get("authorization_scope", "NOT_PROVIDED")),
        "operator_id": str(artifact.get("operator_id", "NOT_PROVIDED")),
        "upstream_gate_hash_match": gate_hash_match,
        "advisory_only_acknowledged": artifact.get("advisory_only_acknowledged") is True,
        "no_execution_authority_granted_acknowledged": (
            artifact.get("no_execution_authority_granted_acknowledged") is True
        ),
        "no_seal_executed_acknowledged": artifact.get("no_seal_executed_acknowledged") is True,
        "finalization_not_executed_acknowledged": (
            artifact.get("finalization_not_executed_acknowledged") is True
        ),
        "approval_record_sealed": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_mutation": False,
        "baseline_mutation": False,
        "governance_authority_mutation": False,
        "note": str(artifact.get("note", "")),
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record(
    *,
    repo_root: str | Path = ".",
    source_gate_path: str = SOURCE_GATE_PATH,
    human_authorization_artifact_path: str | None = None,
    human_authorization_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    gate_path = root / source_gate_path
    source_observed = gate_path.exists()
    source_payload = _load_json_dict(gate_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_authorization_record_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P99_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION"
    )
    authorization_recorded = False
    authorization_value = "NOT_COMPUTABLE"
    authorization_id = "NOT_COMPUTABLE"
    operator_id = "NOT_COMPUTABLE"
    authorization_scope = "NOT_PROVIDED"
    human_artifact_present = human_authorization_packet is not None
    artifact_path_label = human_authorization_artifact_path or "NOT_PROVIDED"
    blockers: list[str] = []
    decision_audit: list[dict[str, Any]] = []
    finalization_authorization_record: dict[str, Any] = {}
    upstream_gate_hash_match = False
    advisory_only_acknowledged = False
    no_execution_authority_granted_acknowledged = False
    no_seal_executed_acknowledged = False
    finalization_not_executed_acknowledged = False
    p99_gate_hash_anchor = "NOT_COMPUTABLE"
    p96_decision_provenance_reanchor: dict[str, Any] = {}

    if source_payload is None:
        blockers = [
            "source_gate_missing_or_unreadable",
            f"source_path:{source_gate_path}",
        ]
    else:
        source_hash = _file_sha256(gate_path)
        source_status = str(
            source_payload.get("finalization_authorization_status", "NOT_COMPUTABLE")
        )
        p99_gate_hash_anchor = str(
            source_payload.get("finalization_authorization_hash", "NOT_COMPUTABLE")
        )
        p96_decision_provenance_reanchor = source_payload.get(
            "decision_provenance_reanchor", {}
        )
        if not isinstance(p96_decision_provenance_reanchor, dict):
            p96_decision_provenance_reanchor = {}

        posture_violations = _check_p99_posture_violations(source_payload)
        if posture_violations:
            finalization_authorization_record_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_FAILED"
            )
            blockers = sorted(posture_violations)
        elif source_status != (
            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE"
        ) or source_payload.get("finalization_authorization_eligible") is not True:
            finalization_authorization_record_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION"
            )
            blockers = [f"source_gate_status:{source_status}"]
        elif human_authorization_packet is None:
            if human_authorization_artifact_path is not None:
                loaded = _load_json_dict(root / human_authorization_artifact_path)
                if loaded is not None:
                    human_authorization_packet = loaded
                    human_artifact_present = True

        if (
            source_payload is not None
            and not posture_violations
            and source_status == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE"
            and source_payload.get("finalization_authorization_eligible") is True
        ):
            if human_authorization_packet is None:
                finalization_authorization_record_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_PENDING"
                )
                authorization_value = "PENDING_OPERATOR_INPUT"
                authorization_id = "PENDING_OPERATOR_INPUT"
                operator_id = "PENDING_OPERATOR_INPUT"
                recommended_next_lane = (
                    "P100_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD"
                )
            else:
                human_artifact_present = True
                audit, violations = _validate_human_authorization_artifact(
                    human_authorization_packet, source_hash
                )
                decision_audit = audit
                gate_hash_match = str(
                    human_authorization_packet.get("upstream_gate_hash", "")
                ) == source_hash
                upstream_gate_hash_match = gate_hash_match
                advisory_only_acknowledged = (
                    human_authorization_packet.get("advisory_only_acknowledged") is True
                )
                no_execution_authority_granted_acknowledged = (
                    human_authorization_packet.get("no_execution_authority_granted_acknowledged")
                    is True
                )
                no_seal_executed_acknowledged = (
                    human_authorization_packet.get("no_seal_executed_acknowledged") is True
                )
                finalization_not_executed_acknowledged = (
                    human_authorization_packet.get("finalization_not_executed_acknowledged")
                    is True
                )
                authorization_value = str(
                    human_authorization_packet.get("authorization", "NOT_PROVIDED")
                )
                authorization_id = str(
                    human_authorization_packet.get("authorization_id", "NOT_PROVIDED")
                )
                operator_id = str(
                    human_authorization_packet.get("operator_id", "NOT_PROVIDED")
                )
                authorization_scope = str(
                    human_authorization_packet.get("authorization_scope", "NOT_PROVIDED")
                )

                if violations:
                    has_lock_violation = any(
                        "must_be_false:found_true" in v for v in violations
                    )
                    if has_lock_violation:
                        finalization_authorization_record_status = (
                            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_FAILED"
                        )
                    else:
                        finalization_authorization_record_status = (
                            "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION"
                        )
                    blockers = sorted(violations)
                else:
                    finalization_authorization_record = _build_finalization_authorization_record(
                        human_authorization_packet, gate_hash_match
                    )
                    if authorization_value == "authorize_finalization_record":
                        finalization_authorization_record_status = (
                            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD"
                        )
                        recommended_next_lane = (
                            "P101_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN"
                        )
                        authorization_recorded = True
                    else:
                        finalization_authorization_record_status = (
                            "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_REJECTED_RECORD"
                        )
                        recommended_next_lane = (
                            "P99_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION"
                        )
                        authorization_recorded = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "finalization_authorization_record_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record_001"
        ),
        "source_gate_path": source_gate_path,
        "source_gate_hash": source_hash,
        "source_gate_status": source_status,
        "source_gate_observed": source_observed,
        "human_authorization_artifact_present": human_artifact_present,
        "human_authorization_artifact_path": artifact_path_label,
        "finalization_authorization_record_status": finalization_authorization_record_status,
        "authorization_recorded": authorization_recorded,
        "authorization_value": authorization_value,
        "authorization_id": authorization_id,
        "operator_id": operator_id,
        "authorization_scope": authorization_scope,
        "upstream_gate_hash_match": upstream_gate_hash_match,
        "advisory_only_acknowledged": advisory_only_acknowledged,
        "no_execution_authority_granted_acknowledged": no_execution_authority_granted_acknowledged,
        "no_seal_executed_acknowledged": no_seal_executed_acknowledged,
        "finalization_not_executed_acknowledged": finalization_not_executed_acknowledged,
        "finalization_authorization_record": finalization_authorization_record,
        "decision_audit": decision_audit,
        "p99_gate_hash_anchor": p99_gate_hash_anchor,
        "p96_decision_provenance_reanchor": p96_decision_provenance_reanchor,
        "blockers": sorted(blockers),
        "recommended_next_lane": recommended_next_lane,
        "advisory_only": True,
        "projection_only": True,
        "authorization_record_only": True,
        "finalization_authorization_record_only": True,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_authorization_record(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
