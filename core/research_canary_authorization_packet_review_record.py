from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationPacketReviewRecord.v1"
LANE_ID = "P102_RESEARCH_CANARY_AUTHORIZATION_PACKET_REVIEW_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT"
UPSTREAM_ARTIFACT_TYPE = "ResearchCanaryAuthorizationPacketDraft.v1"
# Numbering-compatibility remap: historical references may call this P103,
# but the active repo lineage implements the review packet surface as P107.
RECOMMENDED_NEXT_LANE_ON_PASS = "P107_RESEARCH_CANARY_REVIEW_PACKET"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT_REGENERATION"


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "projection_only": True,
        "planning_only": True,
        "evidence_only": True,
        "review_record_only": True,
        "operator_review_required": True,
        "shadow_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "forecast_influence": False,
        "execution_authority": False,
        "repair_execution_authority": False,
        "regeneration_execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "activation_approved": False,
        "authorization_granted": False,
        "canonical_status": CANONICAL_STATUS,
    }


def _validate_p101_packet(p101_packet: Any) -> tuple[list[str], dict[str, Any]]:
    if p101_packet is None:
        return ["p101_artifact_missing"], {}
    if not isinstance(p101_packet, dict):
        return ["p101_artifact_malformed:not_a_dict"], {}

    blockers: list[str] = []
    if p101_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p101_packet.get('lane_id')!r}")
    if p101_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p101_packet.get('artifact_type')!r}")
    if p101_packet.get("authorization_packet_draft_status") != "PASS":
        blockers.append(
            "authorization_packet_draft_status_not_pass:"
            f"{p101_packet.get('authorization_packet_draft_status')!r}"
        )
    if p101_packet.get("authorization_packet_draft_ready") is not True:
        blockers.append(
            "authorization_packet_draft_ready_not_true:"
            f"{p101_packet.get('authorization_packet_draft_ready')!r}"
        )

    draft = p101_packet.get("authorization_packet_draft")
    if not isinstance(draft, dict):
        blockers.append("authorization_packet_draft_malformed:not_a_dict")
    else:
        if draft.get("authorization_posture") != "DRAFT_ONLY_NOT_GRANTED":
            blockers.append(f"authorization_posture_invalid:{draft.get('authorization_posture')!r}")
        if draft.get("review_required") is not True:
            blockers.append(f"review_required_not_true:{draft.get('review_required')!r}")
        if draft.get("activation_approved") is not False:
            blockers.append(f"draft_activation_approved_not_false:{draft.get('activation_approved')!r}")
        if draft.get("authorization_granted") is not False:
            blockers.append(
                f"draft_authorization_granted_not_false:{draft.get('authorization_granted')!r}"
            )

    locks = p101_packet.get("authority_locks")
    if not isinstance(locks, dict):
        blockers.append("authority_locks_malformed:not_a_dict")
    else:
        if locks.get("activation_approved") is not False:
            blockers.append(f"activation_approved_not_false:{locks.get('activation_approved')!r}")
        if locks.get("authorization_granted") is not False:
            blockers.append(f"authorization_granted_not_false:{locks.get('authorization_granted')!r}")
        if locks.get("execution_authority") is not False:
            blockers.append(f"execution_authority_not_false:{locks.get('execution_authority')!r}")
        if locks.get("runtime_authority") is not False:
            blockers.append(f"runtime_authority_not_false:{locks.get('runtime_authority')!r}")

    return blockers, p101_packet


def build_research_canary_authorization_packet_review_record(
    *, p101_packet: dict[str, Any] | None = None
) -> dict[str, Any]:
    blockers, normalized = _validate_p101_packet(p101_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        review_record: dict[str, Any] = {}
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
    else:
        draft = normalized["authorization_packet_draft"]
        status = "PASS"
        ready = True
        review_record = {
            "review_id": "DROP006_DROP007_RESEARCH_CANARY_AUTHORIZATION_PACKET_REVIEW_RECORD",
            "review_scope": "advisory_canary_authorization_packet_review_only",
            "source_draft_id": draft.get("draft_id"),
            "authorization_posture": "DRAFT_ONLY_NOT_GRANTED",
            "review_decision": "HOLD_FOR_OPERATOR_REVIEW",
            "review_recommendation": "READY_FOR_OPERATOR_REVIEW_NOT_AUTHORIZATION",
            "review_required": True,
            "activation_approved": False,
            "authorization_granted": False,
            "status": "REVIEW_READY_FOR_OPERATOR_DECISION",
        }
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "authorization_packet_review_status": status,
        "authorization_packet_review_ready": ready,
        "review_record": review_record,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p101_research_canary_authorization_packet_draft",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "deterministic_ordering": "single_review_record",
        },
        "recommended_next_lane": next_lane,
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_canary_authorization_packet_review_record(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
