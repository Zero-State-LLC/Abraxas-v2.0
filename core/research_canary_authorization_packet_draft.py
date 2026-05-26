from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationPacketDraft.v1"
LANE_ID = "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
UPSTREAM_ARTIFACT_TYPE = "ResearchOperatorStabilizationDecisionRecord.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P102_RESEARCH_CANARY_AUTHORIZATION_PACKET_REVIEW_RECORD"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD_REGENERATION"


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
        "draft_only": True,
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


def _validate_p100_packet(p100_packet: Any) -> tuple[list[str], dict[str, Any]]:
    if p100_packet is None:
        return ["p100_artifact_missing"], {}
    if not isinstance(p100_packet, dict):
        return ["p100_artifact_malformed:not_a_dict"], {}

    blockers: list[str] = []
    if p100_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p100_packet.get('lane_id')!r}")
    if p100_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p100_packet.get('artifact_type')!r}")
    if p100_packet.get("stabilization_decision_status") != "PASS":
        blockers.append(
            f"stabilization_decision_status_not_pass:{p100_packet.get('stabilization_decision_status')!r}"
        )
    if p100_packet.get("decision_record_ready") is not True:
        blockers.append(f"decision_record_ready_not_true:{p100_packet.get('decision_record_ready')!r}")

    decision_record = p100_packet.get("decision_record")
    if not isinstance(decision_record, dict):
        blockers.append("decision_record_malformed:not_a_dict")
    else:
        if decision_record.get("operator_decision") != "HOLD_FOR_OPERATOR_REVIEW":
            blockers.append(f"operator_decision_invalid:{decision_record.get('operator_decision')!r}")
        if (
            decision_record.get("stabilization_recommendation")
            != "READY_FOR_OPERATOR_REVIEW_NOT_ACTIVATION"
        ):
            blockers.append(
                "stabilization_recommendation_invalid:"
                f"{decision_record.get('stabilization_recommendation')!r}"
            )

    locks = p100_packet.get("authority_locks")
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

    return blockers, p100_packet


def build_research_canary_authorization_packet_draft(
    *, p100_packet: dict[str, Any] | None = None
) -> dict[str, Any]:
    blockers, normalized = _validate_p100_packet(p100_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        draft: dict[str, Any] = {}
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
    else:
        decision_record = normalized["decision_record"]
        status = "PASS"
        ready = True
        draft = {
            "draft_id": "DROP006_DROP007_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT",
            "draft_scope": "advisory_canary_authorization_packet_draft_only",
            "source_decision_id": decision_record.get("decision_id"),
            "operator_decision": "HOLD_FOR_OPERATOR_REVIEW",
            "stabilization_recommendation": "READY_FOR_OPERATOR_REVIEW_NOT_ACTIVATION",
            "candidate_scope": "DROP006_DROP007_RESEARCH_CANARY",
            "authorization_posture": "DRAFT_ONLY_NOT_GRANTED",
            "review_required": True,
            "activation_approved": False,
            "authorization_granted": False,
            "status": "DRAFT_READY_FOR_REVIEW",
        }
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "authorization_packet_draft_status": status,
        "authorization_packet_draft_ready": ready,
        "authorization_packet_draft": draft,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p100_research_operator_stabilization_decision_record",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "deterministic_ordering": "single_draft_record",
        },
        "recommended_next_lane": next_lane,
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_canary_authorization_packet_draft(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
