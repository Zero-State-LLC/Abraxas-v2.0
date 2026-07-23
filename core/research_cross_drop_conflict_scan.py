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

# Dimension key families inspected on each proof record (nested authority_locks included)
_DIMENSION_KEYS: dict[str, tuple[str, ...]] = {
    "authority_overlap": (
        "execution_authority",
        "runtime_authority",
        "valid_for_execution",
        "production_activation",
    ),
    "runtime_scope_overlap": (
        "runtime_authority",
        "runtime_scope",
        "scheduler_mutation",
    ),
    "scheduler_scope_overlap": (
        "scheduler_mutation",
        "scheduler_scope",
        "token_minting_allowed",
    ),
    "forecast_influence_overlap": (
        "forecast_influence",
        "forecast_weight_allowed",
    ),
    "canon_promotion_overlap": (
        "canon_promotion",
        "canon_mutation",
        "canon_mutation_allowed",
    ),
    "shadow_boundary_overlap": (
        "shadow_only",
        "advisory_only",
        "projection_only",
    ),
}


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


def _flatten_flags(record: dict[str, Any]) -> dict[str, bool]:
    """Collect boolean authority/scope flags from record and nested authority_locks."""
    flags: dict[str, bool] = {}
    for key, value in record.items():
        if isinstance(value, bool):
            flags[key] = value
    locks = record.get("authority_locks")
    if isinstance(locks, dict):
        for key, value in locks.items():
            if isinstance(value, bool):
                flags[key] = value
    return flags


def _scan_dimension_overlaps(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Advisory overlap detection across declared dimensions. Never resolves."""
    detected: list[dict[str, Any]] = []
    if len(records) < 2:
        return detected

    flag_maps = [(str(r.get("proof_id", f"r{i}")), _flatten_flags(r)) for i, r in enumerate(records)]

    for dimension, keys in sorted(_DIMENSION_KEYS.items()):
        # For exclusive-authority dimensions: conflict if ≥2 records claim True on same key
        exclusive = dimension != "shadow_boundary_overlap"
        for key in keys:
            claimants = sorted(pid for pid, flags in flag_maps if flags.get(key) is True)
            if exclusive and len(claimants) >= 2:
                detected.append(
                    {
                        "dimension": dimension,
                        "key": key,
                        "claimants": claimants,
                        "severity": "high" if key in {
                            "execution_authority",
                            "production_activation",
                            "canon_promotion",
                            "canon_mutation",
                        } else "medium",
                        "detail": (
                            f"Multiple drops claim {key}=True under {dimension}; "
                            "operator review required — no auto-resolve"
                        ),
                        "resolution_required": True,
                    }
                )

    # Surface / fold-family collision (same non-empty id claimed by both)
    surface_ids = [
        (str(r.get("proof_id", "")), str(r.get("source_surface_id", "")))
        for r in records
        if r.get("source_surface_id")
    ]
    by_surface: dict[str, list[str]] = {}
    for pid, sid in surface_ids:
        by_surface.setdefault(sid, []).append(pid)
    for sid, pids in sorted(by_surface.items()):
        if len(pids) >= 2:
            detected.append(
                {
                    "dimension": "runtime_scope_overlap",
                    "key": "source_surface_id",
                    "claimants": sorted(pids),
                    "severity": "medium",
                    "detail": f"Shared source_surface_id {sid!r} across drops",
                    "resolution_required": True,
                }
            )

    detected.sort(key=lambda d: (d["dimension"], d["key"], ",".join(d["claimants"])))
    return detected


def _build_conflict_findings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = sorted(
        [r for r in records if isinstance(r, dict)],
        key=lambda record: str(record.get("proof_id")),
    )
    ordered_ids = [str(record.get("proof_id")) for record in selected]
    source_ids = sorted(str(record.get("source_surface_id")) for record in selected)
    fold_families = sorted(str(record.get("research_fold_family")) for record in selected)

    detected = _scan_dimension_overlaps(selected)
    blocking = any(
        d.get("severity") in ("high", "severe") and d.get("resolution_required")
        for d in detected
    )
    status = "CONFLICTS_DETECTED" if detected else "PASS"

    finding = {
        "finding_id": "DROP006_DROP007_CROSS_DROP_CONFLICT_SCAN",
        "compared_proof_ids": ordered_ids,
        "compared_source_surface_ids": source_ids,
        "compared_research_fold_families": fold_families,
        "conflict_scan_scope": "advisory_cross_drop_conflict_scan_only",
        "checked_dimensions": sorted(_DIMENSION_KEYS.keys()),
        "detected_conflicts": detected,
        "blocking_conflict_detected": blocking,
        "status": status,
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
        findings = _build_conflict_findings(records)
        conflict_count = sum(len(f.get("detected_conflicts", [])) for f in findings)
        blocking = any(f.get("blocking_conflict_detected") for f in findings)
        status = "CONFLICTS_DETECTED" if conflict_count else "PASS"
        ready = True
        summary = {
            "scanned_drop_count": 2,
            "conflict_count": conflict_count,
            "blocking_conflict_detected": blocking,
        }
        # Still advisory: even with conflicts, recommend operator path — never auto-resolve
        next_lane = (
            RECOMMENDED_NEXT_LANE_ON_PASS
            if not blocking
            else RECOMMENDED_NEXT_LANE_ON_PASS  # operator decision record still the disposition path
        )

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
