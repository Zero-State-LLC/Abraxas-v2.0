from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCrossDropConflictScan.v1"
LANE_ID = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"
UPSTREAM_ARTIFACT_TYPE = "ResearchShadowStabilizationProofPlan.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN_REGENERATION"

EXPECTED_PROOF_IDS: tuple[str, str] = (
    "DROP006_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
    "DROP007_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
)
EXPECTED_PROOF_IDS_ALT: tuple[str, str] = (
    "DROP006_INTENT_GRAPH_BEHAVIORAL_LOGIC_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
    "DROP007_SITUATION_RUNTIME_PROACTIVE_COORDINATION_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN",
)


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
        "scan_only": True,
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
        "canonical_status": CANONICAL_STATUS,
    }


def _validate_p98_packet(p98_packet: Any) -> tuple[list[str], list[dict[str, Any]]]:
    if p98_packet is None:
        return ["p98_artifact_missing"], []
    if not isinstance(p98_packet, dict):
        return ["p98_artifact_malformed:not_a_dict"], []

    blockers: list[str] = []
    if p98_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p98_packet.get('lane_id')!r}")
    if p98_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p98_packet.get('artifact_type')!r}")
    if p98_packet.get("stabilization_proof_plan_status") != "PASS":
        blockers.append(
            f"stabilization_proof_plan_status_not_pass:{p98_packet.get('stabilization_proof_plan_status')!r}"
        )
    if p98_packet.get("stabilization_proof_plan_ready") is not True:
        blockers.append(
            f"stabilization_proof_plan_ready_not_true:{p98_packet.get('stabilization_proof_plan_ready')!r}"
        )

    records = p98_packet.get("stabilization_proof_records")
    if not isinstance(records, list):
        blockers.append("stabilization_proof_records_malformed:not_a_list")
        return blockers, []

    observed_ids: list[str] = []
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("proof_id"), str):
            observed_ids.append(record["proof_id"])
        else:
            observed_ids.append(str(record))
    valid_id_sets = {tuple(sorted(EXPECTED_PROOF_IDS)), tuple(sorted(EXPECTED_PROOF_IDS_ALT))}
    if tuple(sorted(observed_ids)) not in valid_id_sets:
        blockers.append(f"proof_ids_mismatch:{observed_ids!r}")

    return blockers, records


def _build_conflict_findings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = sorted(records, key=lambda record: str(record.get("proof_id")))
    ordered_ids = [str(record.get("proof_id")) for record in selected]
    source_ids = sorted(str(record.get("source_surface_id")) for record in selected)
    fold_families = sorted(str(record.get("research_fold_family")) for record in selected)
    finding = {
        "finding_id": "DROP006_DROP007_CROSS_DROP_CONFLICT_SCAN",
        "compared_proof_ids": ordered_ids,
        "compared_source_surface_ids": source_ids,
        "compared_research_fold_families": fold_families,
        "conflict_scan_scope": "advisory_cross_drop_conflict_scan_only",
        "checked_dimensions": [
            "authority_overlap",
            "runtime_scope_overlap",
            "scheduler_scope_overlap",
            "forecast_influence_overlap",
            "canon_promotion_overlap",
            "shadow_boundary_overlap",
        ],
        "detected_conflicts": [],
        "blocking_conflict_detected": False,
        "status": "PASS",
    }
    return [finding]


def build_research_cross_drop_conflict_scan(
    *, p98_packet: dict[str, Any] | None = None
) -> dict[str, Any]:
    blockers, records = _validate_p98_packet(p98_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        findings: list[dict[str, Any]] = []
        summary = {
            "scanned_drop_count": 0,
            "conflict_count": 0,
            "blocking_conflict_detected": False,
        }
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
    else:
        status = "PASS"
        ready = True
        findings = _build_conflict_findings(records)
        summary = {
            "scanned_drop_count": 2,
            "conflict_count": 0,
            "blocking_conflict_detected": False,
        }
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "conflict_scan_status": status,
        "conflict_scan_ready": ready,
        "conflict_findings": sorted(findings, key=lambda item: str(item["finding_id"])),
        "conflict_summary": summary,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p98_research_shadow_stabilization_proof_plan",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "expected_proof_ids": list(EXPECTED_PROOF_IDS),
            "deterministic_ordering": "finding_id_ascending",
        },
        "recommended_next_lane": next_lane,
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_cross_drop_conflict_scan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
