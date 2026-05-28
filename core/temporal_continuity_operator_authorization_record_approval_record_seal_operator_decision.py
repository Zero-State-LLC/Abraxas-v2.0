from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealOperatorDecision.v1"

SOURCE_OPERATOR_REVIEW_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_operator_review/latest.json"
)
DEFAULT_HUMAN_DECISION_PATH = (
    "input/operator_authorization_record_approval_record_seal_decision.json"
)

ALLOWED_DECISIONS: tuple[str, ...] = (
    "approve_seal_record",
    "reject_seal_record",
    "hold_pending_further_review",
    "request_repair",
)

FORBIDDEN_DECISIONS: tuple[str, ...] = (
    "grant_execution_authority",
    "activate_production",
    "promote_canon",
    "mutate_scheduler",
    "mutate_baseline",
    "auto_approve",
    "bypass_operator_review",
    "seal_approval_record",
    "create_execution_token",
    "grant_authorization",
)

_DECISION_ROUTING: dict[str, str] = {
    "approve_seal_record": (
        "P97_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN"
    ),
    "reject_seal_record": (
        "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    ),
    "hold_pending_further_review": (
        "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    ),
    "request_repair": (
        "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    ),
}

_REQUIRED_ACKNOWLEDGEMENT_FIELDS: tuple[str, ...] = (
    "advisory_only_acknowledged",
    "no_execution_authority_granted_acknowledged",
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
        "approval_record_seal_operator_decision_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _run_decision_posture_audit(
    decision_artifact: dict[str, Any],
    p95_file_hash: str,
) -> list[dict[str, Any]]:
    audit: list[dict[str, Any]] = []

    decision_val = decision_artifact.get("decision", "")
    forbidden = decision_val in FORBIDDEN_DECISIONS
    audit.append({"check_id": "decision_not_in_forbidden_list", "passed": not forbidden})

    allowed = decision_val in ALLOWED_DECISIONS
    audit.append({"check_id": "decision_in_allowed_list", "passed": allowed})

    declared_hash = str(decision_artifact.get("upstream_review_hash", ""))
    hash_match = (
        declared_hash == p95_file_hash
        and declared_hash not in ("", "NOT_COMPUTABLE")
    )
    audit.append({"check_id": "upstream_review_hash_matches_p95_file", "passed": hash_match})

    for field in _REQUIRED_ACKNOWLEDGEMENT_FIELDS:
        audit.append({
            "check_id": f"{field}_is_true",
            "passed": decision_artifact.get(field) is True,
        })

    decision_id_present = bool(decision_artifact.get("decision_id", ""))
    audit.append({"check_id": "decision_id_present", "passed": decision_id_present})

    operator_id_present = bool(decision_artifact.get("operator_id", ""))
    audit.append({"check_id": "operator_id_present", "passed": operator_id_present})

    return audit


def _make_operator_decision_record(
    *,
    decision_observed: bool,
    decision_val: str,
    decision_id: str,
    operator_id: str,
    upstream_review_hash_match: bool,
    advisory_only_acknowledged: bool,
    no_execution_acknowledged: bool,
) -> dict[str, Any]:
    return {
        "decision_scope": "advisory_operator_seal_decision_record_only",
        "autonomous_approval": False,
        "decision_observed": decision_observed,
        "decision_value": decision_val,
        "decision_id": decision_id,
        "operator_id": operator_id,
        "upstream_review_hash_match": upstream_review_hash_match,
        "advisory_only_acknowledged": advisory_only_acknowledged,
        "no_execution_authority_granted_acknowledged": no_execution_acknowledged,
        "approval_granted": False,
        "authorization_granted": False,
        "execution_authority": False,
        "approval_record_sealed": False,
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision(
    *,
    repo_root: str | Path = ".",
    source_operator_review_path: str = SOURCE_OPERATOR_REVIEW_PATH,
    human_decision_packet: dict[str, Any] | None = None,
    human_decision_artifact_path: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_operator_review_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    approval_record_seal_operator_decision_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P95_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
    )
    decision_recorded = False
    decision_blockers: list[str] = []
    decision_posture_audit: list[dict[str, Any]] = []
    upstream_provenance: dict[str, Any] = {}

    if source_payload is None:
        decision_blockers = [
            "source_operator_review_missing_or_unreadable",
            f"source_path:{source_operator_review_path}",
        ]
        operator_decision_record = _make_operator_decision_record(
            decision_observed=False,
            decision_val="NOT_COMPUTABLE",
            decision_id="NOT_PROVIDED",
            operator_id="NOT_PROVIDED",
            upstream_review_hash_match=False,
            advisory_only_acknowledged=False,
            no_execution_acknowledged=False,
        )
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("approval_record_seal_operator_review_status", "NOT_COMPUTABLE")
        )
        source_review_passed = source_payload.get("review_passed") is True
        p95_artifact_hash = str(
            source_payload.get("approval_record_seal_operator_review_hash", "NOT_COMPUTABLE")
        )

        upstream_provenance = {
            "review_hash": p95_artifact_hash,
            "review_file_hash": source_hash,
            "review_id": source_payload.get(
                "approval_record_seal_operator_review_id", "NOT_COMPUTABLE"
            ),
            "dry_run_check_summary": source_payload.get("dry_run_check_summary", {}),
            "review_passed": source_review_passed,
        }

        ready = (
            source_status
            == "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY"
            and source_review_passed
        )

        if not ready:
            approval_record_seal_operator_decision_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW"
            )
            decision_blockers = [
                f"source_operator_review_status:{source_status}",
                f"source_review_passed:{source_review_passed}",
            ]
            operator_decision_record = _make_operator_decision_record(
                decision_observed=False,
                decision_val="NOT_COMPUTABLE",
                decision_id="NOT_PROVIDED",
                operator_id="NOT_PROVIDED",
                upstream_review_hash_match=False,
                advisory_only_acknowledged=False,
                no_execution_acknowledged=False,
            )
        elif human_decision_packet is None:
            approval_record_seal_operator_decision_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_PENDING"
            )
            recommended_next_lane = (
                "P96_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
            )
            decision_recorded = True
            operator_decision_record = _make_operator_decision_record(
                decision_observed=False,
                decision_val="PENDING_OPERATOR_INPUT",
                decision_id="NOT_PROVIDED",
                operator_id="NOT_PROVIDED",
                upstream_review_hash_match=False,
                advisory_only_acknowledged=False,
                no_execution_acknowledged=False,
            )
        else:
            decision_posture_audit = _run_decision_posture_audit(
                human_decision_packet, source_hash
            )
            audit_all_pass = all(item.get("passed") is True for item in decision_posture_audit)

            decision_val = str(human_decision_packet.get("decision", ""))
            decision_id = str(human_decision_packet.get("decision_id", "NOT_PROVIDED"))
            operator_id = str(human_decision_packet.get("operator_id", "NOT_PROVIDED"))
            upstream_review_hash_match = (
                str(human_decision_packet.get("upstream_review_hash", "")) == source_hash
                and source_hash != "NOT_COMPUTABLE"
            )
            advisory_ack = human_decision_packet.get("advisory_only_acknowledged") is True
            no_exec_ack = (
                human_decision_packet.get("no_execution_authority_granted_acknowledged") is True
            )

            operator_decision_record = _make_operator_decision_record(
                decision_observed=True,
                decision_val=decision_val,
                decision_id=decision_id,
                operator_id=operator_id,
                upstream_review_hash_match=upstream_review_hash_match,
                advisory_only_acknowledged=advisory_ack,
                no_execution_acknowledged=no_exec_ack,
            )

            if not audit_all_pass:
                approval_record_seal_operator_decision_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_FAILED"
                )
                decision_blockers = [
                    f"decision_posture_audit_check_failed:{item['check_id']}"
                    for item in decision_posture_audit
                    if not item.get("passed")
                ]
            elif decision_val == "approve_seal_record":
                approval_record_seal_operator_decision_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD"
                )
                recommended_next_lane = _DECISION_ROUTING["approve_seal_record"]
                decision_recorded = True
            elif decision_val in _DECISION_ROUTING:
                approval_record_seal_operator_decision_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_REJECTED_RECORD"
                )
                recommended_next_lane = _DECISION_ROUTING[decision_val]
                decision_recorded = True
            else:
                approval_record_seal_operator_decision_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_FAILED"
                )
                decision_blockers = [f"unrecognised_decision_value:{decision_val!r}"]

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_operator_decision_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision_001"
        ),
        "source_operator_review_path": source_operator_review_path,
        "source_operator_review_hash": source_hash,
        "source_operator_review_status": source_status,
        "source_operator_review_observed": source_observed,
        "approval_record_seal_operator_decision_status": approval_record_seal_operator_decision_status,
        "human_decision_artifact_present": human_decision_packet is not None,
        "human_decision_artifact_path": human_decision_artifact_path,
        "operator_decision_record": operator_decision_record,
        "decision_posture_audit": decision_posture_audit,
        "upstream_provenance": upstream_provenance,
        "decision_recorded": decision_recorded,
        "decision_blockers": sorted(decision_blockers),
        "blockers": sorted(decision_blockers),
        "recommended_next_lane": recommended_next_lane,
        "autonomous_approval": False,
        "advisory_only": True,
        "projection_only": True,
        "approval_record_seal_operator_decision_only": True,
        "operator_decision_record_only": True,
        "decision_record_only": True,
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


def write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_decision(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
