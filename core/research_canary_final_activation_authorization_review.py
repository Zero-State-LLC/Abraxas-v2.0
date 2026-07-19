from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

ARTIFACT_TYPE = "ResearchCanaryFinalActivationAuthorizationReview.v1"
LANE_ID = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
UPSTREAM_LANE_ID = "P129_RESEARCH_CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD"
REQUIRED_P129_ARTIFACT_TYPE = "ResearchCanaryActivationReadinessEvidenceRecord.v1"
RECOMMENDED_NEXT_LANE = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HOLD"

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


def _detect_upstream_authority_drift(p129_packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    upstream_locks = p129_packet.get("authority_locks")
    if isinstance(upstream_locks, dict):
        for key, value in sorted(upstream_locks.items()):
            if value is not False:
                findings.append(f"p129_authority_lock_drift:{key}")
    if p129_packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p129_status_reports_authority_drift")
    if p129_packet.get("lane_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p129_lane_status_reports_authority_drift")
    return sorted(set(findings))


def _candidate_record(candidate_id: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "readiness_evidence_complete_observed": True,
        "final_authorization_review_required": True,
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
        "status": "HELD_FOR_OPERATOR_REVIEW",
        "notes": "P130 is an advisory review boundary only and does not authorize activation or execution.",
    }


def build_research_canary_final_activation_authorization_review(
    *, p129_packet: dict[str, Any] | None
) -> dict[str, Any]:
    missing_or_invalid_inputs: list[str] = []
    if p129_packet is None:
        missing_or_invalid_inputs.append("p129_packet_missing")
    elif not isinstance(p129_packet, dict):
        missing_or_invalid_inputs.append("p129_packet_malformed")

    base = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_artifact_type": REQUIRED_P129_ARTIFACT_TYPE,
        "upstream_packet_hash": p129_packet.get("packet_hash") if isinstance(p129_packet, dict) else None,
        "analyzed_candidates": [],
        "final_review_records": [],
        "missing_or_invalid_inputs": missing_or_invalid_inputs,
        "authority_locks": _authority_locks(),
        "governance_posture": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
    }

    if missing_or_invalid_inputs:
        return _finalize({
            **base,
            "status": "NOT_COMPUTABLE",
            "lane_status": "NOT_COMPUTABLE",
            "recommended_next_lane": "NOT_COMPUTABLE",
        })

    assert isinstance(p129_packet, dict)
    drift = _detect_upstream_authority_drift(p129_packet)
    if drift:
        return _finalize({
            **base,
            "status": "REJECTED_AUTHORITY_DRIFT",
            "lane_status": "REJECTED_AUTHORITY_DRIFT",
            "missing_or_invalid_inputs": drift,
            "recommended_next_lane": "NOT_COMPUTABLE",
        })

    if p129_packet.get("lane_id") != UPSTREAM_LANE_ID:
        missing_or_invalid_inputs.append("p129_lane_id_mismatch")
    if p129_packet.get("artifact_type") != REQUIRED_P129_ARTIFACT_TYPE:
        missing_or_invalid_inputs.append("p129_artifact_type_mismatch")
    if p129_packet.get("status") != "CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD_EMITTED":
        missing_or_invalid_inputs.append("p129_status_not_emitted")
    if p129_packet.get("lane_status") != "CANARY_ACTIVATION_READINESS_EVIDENCE_COMPLETE":
        missing_or_invalid_inputs.append("p129_lane_status_not_complete")
    if p129_packet.get("recommended_next_lane") != LANE_ID:
        missing_or_invalid_inputs.append("p129_recommended_next_lane_mismatch")

    candidates = p129_packet.get("activation_readiness_evidence_complete_candidates")
    if not isinstance(candidates, list) or any(not isinstance(c, str) for c in candidates):
        missing_or_invalid_inputs.append("p129_candidates_malformed")
        candidates = []

    statuses = p129_packet.get("candidate_statuses")
    if not isinstance(statuses, list):
        missing_or_invalid_inputs.append("p129_candidate_statuses_malformed")
    else:
        complete = {r.get("candidate_id") for r in statuses if isinstance(r, dict) and r.get("canary_activation_readiness_evidence_status") == "CANARY_ACTIVATION_READINESS_EVIDENCE_COMPLETE"}
        if set(candidates) != complete:
            missing_or_invalid_inputs.append("p129_candidate_readiness_evidence_incomplete_or_mismatch")

    if missing_or_invalid_inputs:
        return _finalize({
            **base,
            "status": "NOT_COMPUTABLE",
            "lane_status": "NOT_COMPUTABLE",
            "missing_or_invalid_inputs": sorted(set(missing_or_invalid_inputs)),
            "recommended_next_lane": "NOT_COMPUTABLE",
        })

    final_records = [_candidate_record(candidate_id) for candidate_id in sorted(candidates)]
    return _finalize({
        **base,
        "status": "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_RECORD_EMITTED",
        "lane_status": "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR",
        "analyzed_candidates": sorted(candidates),
        "final_review_records": final_records,
        "recommended_next_lane": RECOMMENDED_NEXT_LANE,
    })


# TD Wave 1: publication removed from core.
# Use core.canonical.json.write_canonical_json from scripts/run_*.py.
