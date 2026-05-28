from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryOperatorDispositionRecord.v1"
LANE_ID = "RESEARCH_CANARY_OPERATOR_DISPOSITION_RECORD"
UPSTREAM_LANE_ID = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD"
UPSTREAM_ARTIFACT_TYPE = "ResearchCanaryFinalActivationAuthorizationReviewHold.v1"

ALLOWED_DISPOSITIONS: frozenset[str] = frozenset(
    ["defer_hold_indefinitely", "deny_activation_path", "request_further_evidence"]
)
DISPOSITION_STATUS_MAP: dict[str, str] = {
    "defer_hold_indefinitely": "HOLD_DEFERRED_INDEFINITELY",
    "deny_activation_path": "ACTIVATION_PATH_DENIED",
    "request_further_evidence": "FURTHER_EVIDENCE_REQUESTED",
}

REQUIRED_ACK_FIELDS: tuple[str, ...] = (
    "operator_disposition_acknowledged",
    "no_activation_acknowledged",
    "no_authorization_granted_acknowledged",
    "no_p131_acknowledged",
    "advisory_only_acknowledged",
)

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "production_activation",
    "execution_authority",
    "runtime_authority",
    "scheduler_mutation",
    "canon_promotion",
    "forecast_influence",
    "repair_execution_authority",
    "regeneration_execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _authority_locks() -> dict[str, bool]:
    return {key: False for key in AUTHORITY_LOCK_KEYS}


def _detect_hold_authority_drift(hold_packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    locks = hold_packet.get("authority_locks")
    if isinstance(locks, dict):
        for key, value in sorted(locks.items()):
            if value is not False:
                findings.append(f"hold_authority_lock_drift:{key}")
    return sorted(findings)


def _not_computable(
    base: dict[str, Any], missing: list[str]
) -> dict[str, Any]:
    return _finalize({
        **base,
        "status": "NOT_COMPUTABLE",
        "lane_status": "NOT_COMPUTABLE",
        "b002_status": "NOT_COMPUTABLE",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "missing_or_invalid_inputs": sorted(set(missing)),
    })


def _disposition_record(
    candidate_id: str, obs: dict[str, Any]
) -> dict[str, Any]:
    disposition = obs.get("disposition", "defer_hold_indefinitely")
    return {
        "candidate_id": candidate_id,
        "disposition": disposition,
        "disposition_status": DISPOSITION_STATUS_MAP.get(disposition, "UNKNOWN"),
        "rationale": obs.get("rationale", ""),
        "activation_approved": False,
        "authorization_granted": False,
        "production_activation": False,
        "valid_for_execution": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
    }


def build_research_canary_operator_disposition_record(
    *,
    hold_packet: dict[str, Any] | None,
    observations: dict[str, Any] | None,
) -> dict[str, Any]:
    missing: list[str] = []

    if hold_packet is None:
        missing.append("hold_packet_missing")
    elif not isinstance(hold_packet, dict):
        missing.append("hold_packet_malformed")

    if observations is None:
        missing.append("observations_missing")
    elif not isinstance(observations, dict):
        missing.append("observations_malformed")

    upstream_packet_hash = (
        hold_packet.get("packet_hash") if isinstance(hold_packet, dict) else None
    )
    operator_id = (
        observations.get("operator_id") if isinstance(observations, dict) else None
    )
    disposition_batch_id = (
        observations.get("disposition_batch_id") if isinstance(observations, dict) else None
    )

    base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_artifact_type": UPSTREAM_ARTIFACT_TYPE,
        "upstream_packet_hash": upstream_packet_hash,
        "disposition_batch_id": disposition_batch_id,
        "operator_id": operator_id,
        "dispositioned_candidates": [],
        "disposition_records": [],
        "missing_or_invalid_inputs": [],
        "authority_locks": _authority_locks(),
        "governance_posture": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "p131_created": False,
        "activation_approved": False,
        "authorization_granted": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "governance_authority_mutation": False,
        "authority_change": "none",
    }

    if missing:
        return _not_computable(base, missing)

    assert isinstance(hold_packet, dict)
    assert isinstance(observations, dict)

    drift = _detect_hold_authority_drift(hold_packet)
    if drift:
        return _finalize({
            **base,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "lane_status": "REJECTED_AUTHORITY_DRIFT",
            "b002_status": "NOT_COMPUTABLE",
            "recommended_next_lane": "NOT_COMPUTABLE",
            "missing_or_invalid_inputs": drift,
        })

    if hold_packet.get("lane_id") != UPSTREAM_LANE_ID:
        missing.append("hold_lane_id_mismatch")
    if hold_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        missing.append("hold_artifact_type_mismatch")
    if hold_packet.get("status") != "FORMAL_HOLD_RECORD_EMITTED":
        missing.append("hold_status_not_emitted")
    if hold_packet.get("p131_created") is not False:
        missing.append("hold_p131_created_drift")

    for ack_field in REQUIRED_ACK_FIELDS:
        if observations.get(ack_field) is not True:
            missing.append(f"observations_ack_missing:{ack_field}")

    if observations.get("authority_change") != "none":
        missing.append("observations_authority_change_not_none")

    upstream_hash_in_obs = observations.get("upstream_hold_artifact_hash")
    if upstream_hash_in_obs != upstream_packet_hash:
        missing.append("observations_upstream_hash_mismatch")

    held_candidates = hold_packet.get("held_candidates")
    if not isinstance(held_candidates, list) or not held_candidates:
        missing.append("hold_held_candidates_missing")
        held_candidates = []

    candidate_dispositions = observations.get("candidate_dispositions")
    if not isinstance(candidate_dispositions, dict):
        missing.append("observations_candidate_dispositions_malformed")
        candidate_dispositions = {}

    obs_keys = set(candidate_dispositions.keys())
    hold_keys = set(held_candidates)

    extra = obs_keys - hold_keys
    if extra:
        for k in sorted(extra):
            missing.append(f"observations_extra_candidate:{k}")

    absent = hold_keys - obs_keys
    if absent:
        for k in sorted(absent):
            missing.append(f"observations_missing_candidate:{k}")

    for cid, entry in sorted(candidate_dispositions.items()):
        if not isinstance(entry, dict):
            missing.append(f"observations_candidate_malformed:{cid}")
            continue
        disp = entry.get("disposition")
        if disp not in ALLOWED_DISPOSITIONS:
            missing.append(f"observations_candidate_invalid_disposition:{cid}:{disp}")
        if entry.get("activation_approved") is not False:
            missing.append(f"observations_candidate_activation_approved_drift:{cid}")
        if entry.get("authorization_granted") is not False:
            missing.append(f"observations_candidate_authorization_granted_drift:{cid}")
        if entry.get("production_activation") is not False:
            missing.append(f"observations_candidate_production_activation_drift:{cid}")

    if missing:
        return _not_computable(base, missing)

    sorted_candidates = sorted(held_candidates)
    disposition_records = [
        _disposition_record(cid, candidate_dispositions[cid])
        for cid in sorted_candidates
    ]
    disposition_statuses = {r["disposition_status"] for r in disposition_records}
    all_deferred = disposition_statuses == {"HOLD_DEFERRED_INDEFINITELY"}
    b002_status = "RESOLVED_BY_OPERATOR_DEFER_ALL" if all_deferred else "RESOLVED_BY_OPERATOR_MIXED_DISPOSITION"

    return _finalize({
        **base,
        "status": "RESEARCH_CANARY_OPERATOR_DISPOSITION_RECORD_READY",
        "lane_status": "OPERATOR_DISPOSITION_RECORD_EMITTED",
        "b002_status": b002_status,
        "recommended_next_lane": "OPERATOR_DISPOSITION_COMPLETE_ADVISORY_HOLD_CLOSED",
        "dispositioned_candidates": sorted_candidates,
        "disposition_records": disposition_records,
        "disposition_batch_id": disposition_batch_id,
        "operator_id": operator_id,
        "disposition_scope": observations.get("disposition_scope", ""),
        "disposition_mode": observations.get("disposition_mode", ""),
    })


def write_research_canary_operator_disposition_record(
    out_path: Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(out_path, packet)
