from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.research_shadow_stabilization_receipt import CANDIDATE_IDS

ARTIFACT_TYPE = "ResearchOperatorStabilizationDecisionRecord.v1"
LANE_ID = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"
UPSTREAM_ARTIFACT_TYPE = "ResearchCrossDropConflictScan.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P101_RESEARCH_CANARY_AUTHORIZATION_PACKET_DRAFT"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN_REGENERATION"
REQUIRED_FINDING_ID = "DROP006_DROP007_CROSS_DROP_CONFLICT_SCAN"


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
        "decision_record_only": True,
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


def _validate_p99_packet(p99_packet: Any) -> tuple[list[str], dict[str, Any]]:
    if p99_packet is None:
        return ["p99_artifact_missing"], {}
    if not isinstance(p99_packet, dict):
        return ["p99_artifact_malformed:not_a_dict"], {}

    blockers: list[str] = []
    if p99_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p99_packet.get('lane_id')!r}")
    if p99_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p99_packet.get('artifact_type')!r}")
    if p99_packet.get("conflict_scan_status") != "PASS":
        blockers.append(f"conflict_scan_status_not_pass:{p99_packet.get('conflict_scan_status')!r}")
    if p99_packet.get("conflict_scan_ready") is not True:
        blockers.append(f"conflict_scan_ready_not_true:{p99_packet.get('conflict_scan_ready')!r}")

    summary = p99_packet.get("conflict_summary")
    if not isinstance(summary, dict):
        blockers.append("conflict_summary_malformed:not_a_dict")
    else:
        if summary.get("blocking_conflict_detected") is not False:
            blockers.append(
                f"blocking_conflict_detected_not_false:{summary.get('blocking_conflict_detected')!r}"
            )
        if summary.get("conflict_count") != 0:
            blockers.append(f"conflict_count_not_zero:{summary.get('conflict_count')!r}")

    findings = p99_packet.get("conflict_findings")
    if not isinstance(findings, list):
        blockers.append("conflict_findings_malformed:not_a_list")
    else:
        finding_ids = [
            finding.get("finding_id")
            for finding in findings
            if isinstance(finding, dict)
        ]
        if REQUIRED_FINDING_ID not in finding_ids:
            blockers.append(f"required_finding_missing:{REQUIRED_FINDING_ID}")

    return blockers, p99_packet if isinstance(p99_packet, dict) else {}


def build_research_operator_stabilization_decision_record(
    *, p99_packet: dict[str, Any] | None = None
) -> dict[str, Any]:
    blockers, normalized = _validate_p99_packet(p99_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        decision_record: dict[str, Any] = {}
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
        shadow_compatibility_status = "NOT_COMPUTABLE"
        shadow_compatibility_reasons = list(blockers)
        shadow_candidate_decisions: dict[str, Any] = {}
    else:
        status = "PASS"
        ready = True
        decision_record = {
            "decision_id": "DROP006_DROP007_RESEARCH_STABILIZATION_DECISION_RECORD",
            "decision_scope": "advisory_operator_stabilization_review_only",
            "reviewed_findings": [REQUIRED_FINDING_ID],
            "conflict_summary": dict(normalized["conflict_summary"]),
            "operator_decision": "HOLD_FOR_OPERATOR_REVIEW",
            "stabilization_recommendation": "READY_FOR_OPERATOR_REVIEW_NOT_ACTIVATION",
            "status": "PASS",
        }
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
        shadow_compatibility_status = "EMITTED"
        shadow_compatibility_reasons = []
        shadow_candidate_decisions = {
            candidate_id: {
                "candidate_id": candidate_id,
                "decision": "advance_to_shadow_stabilization",
                "decision_scope": "shadow_stabilization_compatibility_only",
                "authority_class": "NON_OPERATIVE",
                "status": "DECISION_EMITTED",
            }
            for candidate_id in CANDIDATE_IDS
        }

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "stabilization_decision_status": status,
        "decision_record_ready": ready,
        "decision_record": decision_record,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p99_research_cross_drop_conflict_scan",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "required_finding_id": REQUIRED_FINDING_ID,
            "deterministic_ordering": "single_decision_record",
        },
        "recommended_next_lane": next_lane,
        "shadow_stabilization_compatibility": {
            "compatibility_status": shadow_compatibility_status,
            "target_lane_id": "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT",
            "operator_decision_record_status": shadow_compatibility_status,
            "candidate_decisions": shadow_candidate_decisions,
            "not_computable_reasons": shadow_compatibility_reasons,
        },
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_operator_stabilization_decision_record(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
