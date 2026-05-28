from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryFinalActivationAuthorizationReviewHold.v1"
LANE_ID = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD"
UPSTREAM_LANE_ID = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
REQUIRED_P130_ARTIFACT_TYPE = "ResearchCanaryFinalActivationAuthorizationReview.v1"
RECOMMENDED_NEXT_LANE = "OPERATOR_DISPOSITION_REQUIRED"
HOLD_REASON = "final_authorization_review_required_pending_operator_decision"

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


def _detect_upstream_authority_drift(p130_packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    upstream_locks = p130_packet.get("authority_locks")
    if isinstance(upstream_locks, dict):
        for key, value in sorted(upstream_locks.items()):
            if value is not False:
                findings.append(f"p130_authority_lock_drift:{key}")
    if p130_packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p130_status_reports_authority_drift")
    if p130_packet.get("lane_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p130_lane_status_reports_authority_drift")
    return sorted(set(findings))


def _hold_candidate_record(candidate_id: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "hold_status": "FORMAL_HOLD_RECORD_EMITTED",
        "operator_disposition_required": True,
        "hold_reason": HOLD_REASON,
        "activation_approved": False,
        "authorization_granted": False,
        "production_activation": False,
        "execution_authority": False,
        "runtime_authority": False,
        "scheduler_mutation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "valid_for_execution": False,
        "token_minting_allowed": False,
        "notes": "Formal hold record. Operator disposition required before any activation path.",
    }


def build_research_canary_final_activation_authorization_review_hold(
    *, p130_packet: dict[str, Any] | None
) -> dict[str, Any]:
    missing_or_invalid_inputs: list[str] = []
    if p130_packet is None:
        missing_or_invalid_inputs.append("p130_packet_missing")
    elif not isinstance(p130_packet, dict):
        missing_or_invalid_inputs.append("p130_packet_malformed")

    upstream_packet_hash = (
        p130_packet.get("packet_hash") if isinstance(p130_packet, dict) else None
    )

    base = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_artifact_type": REQUIRED_P130_ARTIFACT_TYPE,
        "upstream_packet_hash": upstream_packet_hash,
        "held_candidates": [],
        "hold_records": [],
        "missing_or_invalid_inputs": missing_or_invalid_inputs,
        "authority_locks": _authority_locks(),
        "governance_posture": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "p131_created": False,
    }

    if missing_or_invalid_inputs:
        return _finalize({
            **base,
            "status": "NOT_COMPUTABLE",
            "lane_status": "NOT_COMPUTABLE",
            "recommended_next_lane": "NOT_COMPUTABLE",
        })

    assert isinstance(p130_packet, dict)
    drift = _detect_upstream_authority_drift(p130_packet)
    if drift:
        return _finalize({
            **base,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "lane_status": "REJECTED_AUTHORITY_DRIFT",
            "missing_or_invalid_inputs": drift,
            "recommended_next_lane": "NOT_COMPUTABLE",
        })

    if p130_packet.get("lane_id") != UPSTREAM_LANE_ID:
        missing_or_invalid_inputs.append("p130_lane_id_mismatch")
    if p130_packet.get("artifact_type") != REQUIRED_P130_ARTIFACT_TYPE:
        missing_or_invalid_inputs.append("p130_artifact_type_mismatch")
    if p130_packet.get("status") != "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_RECORD_EMITTED":
        missing_or_invalid_inputs.append("p130_status_not_emitted")
    if p130_packet.get("lane_status") != "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR":
        missing_or_invalid_inputs.append("p130_lane_status_not_held")
    if p130_packet.get("recommended_next_lane") != LANE_ID:
        missing_or_invalid_inputs.append("p130_recommended_next_lane_mismatch")

    candidates = p130_packet.get("analyzed_candidates")
    if not isinstance(candidates, list) or any(not isinstance(c, str) for c in candidates):
        missing_or_invalid_inputs.append("p130_candidates_malformed")
        candidates = []

    final_records = p130_packet.get("final_review_records")
    if not isinstance(final_records, list):
        missing_or_invalid_inputs.append("p130_final_review_records_malformed")
    else:
        held = {
            r.get("candidate_id")
            for r in final_records
            if isinstance(r, dict) and r.get("status") == "HELD_FOR_OPERATOR_REVIEW"
        }
        if set(candidates) != held:
            missing_or_invalid_inputs.append("p130_held_candidate_mismatch")

    if missing_or_invalid_inputs:
        return _finalize({
            **base,
            "status": "NOT_COMPUTABLE",
            "lane_status": "NOT_COMPUTABLE",
            "missing_or_invalid_inputs": sorted(set(missing_or_invalid_inputs)),
            "recommended_next_lane": "NOT_COMPUTABLE",
        })

    sorted_candidates = sorted(candidates)
    hold_records = [_hold_candidate_record(c) for c in sorted_candidates]
    return _finalize({
        **base,
        "status": "FORMAL_HOLD_RECORD_EMITTED",
        "lane_status": "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD_FORMAL_RECORD_EMITTED",
        "held_candidates": sorted_candidates,
        "hold_records": hold_records,
        "hold_reason": HOLD_REASON,
        "recommended_next_lane": RECOMMENDED_NEXT_LANE,
    })


def write_research_canary_final_activation_authorization_review_hold(
    out_path: Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(out_path, packet)
