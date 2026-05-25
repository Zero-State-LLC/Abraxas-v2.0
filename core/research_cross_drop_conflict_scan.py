from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCrossDropConflictScan.v1"
LANE_ID = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"
RECOMMENDED_NEXT_LANE_ON_PASS = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
REQUIRED_P98_ARTIFACT_TYPE = "ResearchShadowStabilizationProofPlan.v1"

REQUIRED_DROPS: tuple[str, ...] = ("DROP006", "DROP007")

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "forecast_influence",
    "forecast_weight_allowed",
    "shadow_to_forecast_leakage",
    "scheduler_mutation",
    "autonomous_execution",
    "operator_bypass",
    "hidden_intent_claim_authority",
)

BOUNDARY_RESOLUTION_NOTES: tuple[dict[str, str], ...] = (
    {
        "boundary_id": "drop006_drop007_hidden_intent_endpoint_constraint",
        "left_surface": "HiddenIntentCandidate.v1",
        "right_surface": "IntendedEndpointConstraint.v1",
        "boundary_note": "ambiguity_or_missing_requirement_candidate_vs_latent_endpoint_planning_constraint",
        "resolution": "Hidden intent is never known intent; endpoint constraint is never known goal.",
    },
    {
        "boundary_id": "drop006_drop007_proactive_vs_inductive_planning_trace",
        "left_surface": "ProactiveResolutionTrace.v1",
        "right_surface": "InductivePlanningTrace.v1",
        "boundary_note": "operator_reviewed_proactive_resolution_trace_vs_replay_guided_planning_trace",
        "resolution": "Proactivity is never autonomous execution.",
    },
    {
        "boundary_id": "drop006_drop007_situation_continuity_vs_behavioral_graph",
        "left_surface": "SituationContinuityFrame.v1",
        "right_surface": "BehavioralIntentGraph.v1",
        "boundary_note": "operator_facing_context_continuity_vs_dependency_topology",
        "resolution": "Intent graph dependency is never confirmed intent.",
    },
    {
        "boundary_id": "drop006_drop007_interleaved_intent_vs_behavioral_graph",
        "left_surface": "InterleavedIntentTrace.v1",
        "right_surface": "BehavioralIntentGraph.v1",
        "boundary_note": "concurrent_ambiguity_trace_vs_structural_dependency_graph",
        "resolution": "Intent graph dependency is never confirmed intent.",
    },
    {
        "boundary_id": "drop006_drop007_intervention_window_vs_pruning_signal",
        "left_surface": "ContextualInterventionWindow.v1",
        "right_surface": "BlindAlleyPruningSignal.v1",
        "boundary_note": "timing_intervention_window_vs_branch_pruning_signal",
        "resolution": "Conflict scan is not repair authority.",
    },
    {
        "boundary_id": "drop006_drop007_coordination_threshold_vs_topology_concepts",
        "left_surface": "CoordinationThreshold.v1",
        "right_surface": "PhasePercolationRecursiveCognitionConcepts.v1",
        "boundary_note": "topology_abstraction_vs_phase_percolation_or_recursive_compression_surfaces",
        "resolution": "Conflict scan is not repair authority.",
    },
    {
        "boundary_id": "drop006_drop007_calibration_projection_vs_pse_calibration",
        "left_surface": "IsotonicCalibrationProjection.v1|DoubleRobustCalibrationGate.v1",
        "right_surface": "PSECalibrationSurfaces.v1",
        "boundary_note": "validation_only_calibration_projection_vs_forecast_weight_mutation",
        "resolution": "Calibration projection is never forecast-weight mutation; AAL-Viz is projection-only.",
    },
)


class _CandidateRecord(dict[str, Any]):
    @property
    def candidate_id(self) -> str:
        return str(self["candidate_id"])

    @property
    def schema_name(self) -> str:
        return str(self["schema_name"])

    @property
    def drop_id(self) -> str:
        return str(self["drop_id"])


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _collect_duplicate_values(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _candidate_records_from_p98(packet: dict[str, Any]) -> tuple[list[_CandidateRecord], list[str]]:
    reasons: list[str] = []
    raw_candidates = packet.get("drop_candidates")
    if not isinstance(raw_candidates, list):
        return [], ["p98_drop_candidates_malformed"]

    records: list[_CandidateRecord] = []
    for idx, item in enumerate(raw_candidates):
        if not isinstance(item, dict):
            reasons.append(f"p98_candidate_malformed:index_{idx}")
            continue
        if not all(key in item for key in ("drop_id", "candidate_id", "schema_name")):
            reasons.append(f"p98_candidate_missing_required_fields:index_{idx}")
            continue
        records.append(_CandidateRecord(item))

    return records, reasons


def _authority_drift_findings(
    p98_packet: dict[str, Any],
    candidates: list[_CandidateRecord],
) -> list[str]:
    findings: list[str] = []

    authority_locks = p98_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        findings.append("p98_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p98_authority_lock_drift:{key}")

    forbidden_candidate_flags = (
        ("promote_to_canon", "candidate_attempted_promotion"),
        ("runtime_mutation", "candidate_attempted_runtime_mutation"),
        ("autonomous_execution", "candidate_attempted_autonomous_execution"),
        ("forecast_weight_mutation", "candidate_attempted_forecast_weight_mutation"),
    )
    for candidate in candidates:
        for flag, label in forbidden_candidate_flags:
            if candidate.get(flag) is True:
                findings.append(f"{label}:{candidate.candidate_id}")

    return sorted(set(findings))


def _semantic_overlap_notes(candidates: list[_CandidateRecord]) -> list[str]:
    notes_to_candidates: dict[str, set[str]] = defaultdict(set)
    for candidate in candidates:
        raw_notes = candidate.get("semantic_overlap_notes")
        if isinstance(raw_notes, str) and raw_notes:
            notes_to_candidates[raw_notes].add(candidate.candidate_id)
        elif isinstance(raw_notes, list):
            for note in raw_notes:
                if isinstance(note, str) and note:
                    notes_to_candidates[note].add(candidate.candidate_id)

    notes: list[str] = []
    for note, ids in sorted(notes_to_candidates.items()):
        if len(ids) > 1:
            notes.append(f"semantic_overlap:{note}:candidates={sorted(ids)}")
    return notes


def _subsystem_overlap_notes(candidates: list[_CandidateRecord]) -> list[str]:
    mapping: dict[str, set[str]] = defaultdict(set)
    for candidate in candidates:
        target = candidate.get("target_subsystem")
        if isinstance(target, str) and target:
            mapping[target].add(candidate.candidate_id)

    notes: list[str] = []
    for subsystem, ids in sorted(mapping.items()):
        if len(ids) > 1:
            notes.append(f"subsystem_overlap:{subsystem}:candidates={sorted(ids)}")
    return notes


def _validate_p98_packet(p98_packet: Any) -> tuple[list[_CandidateRecord], list[str]]:
    if p98_packet is None:
        return [], ["p98_packet_missing"]
    if not isinstance(p98_packet, dict):
        return [], ["p98_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    artifact_type = p98_packet.get("artifact_type")
    if artifact_type != REQUIRED_P98_ARTIFACT_TYPE:
        reasons.append(f"p98_artifact_type_mismatch:{artifact_type!r}")

    lane_id = p98_packet.get("lane_id")
    if lane_id != UPSTREAM_LANE_ID:
        reasons.append(f"p98_lane_id_mismatch:{lane_id!r}")

    status = p98_packet.get("status")
    if status != "PASS":
        reasons.append(f"p98_status_not_pass:{status!r}")

    recommended_next_lane = p98_packet.get("recommended_next_lane")
    if recommended_next_lane != LANE_ID:
        reasons.append(
            f"p98_recommendation_chain_mismatch:{recommended_next_lane!r}"
        )

    candidates, candidate_reasons = _candidate_records_from_p98(p98_packet)
    reasons.extend(candidate_reasons)

    if candidates:
        drops_present = {candidate.drop_id for candidate in candidates}
        missing_drops = sorted(drop for drop in REQUIRED_DROPS if drop not in drops_present)
        if missing_drops:
            reasons.extend(
                f"missing_required_drop_candidates:{drop_id}" for drop_id in missing_drops
            )

    return candidates, reasons


def build_research_cross_drop_conflict_scan(
    *,
    p98_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates, not_computable_reasons = _validate_p98_packet(p98_packet)
    normalized_p98 = p98_packet if isinstance(p98_packet, dict) else None

    duplicate_id_conflicts: list[str] = []
    schema_conflicts: list[str] = []
    rune_conflicts: list[str] = []
    metric_conflicts: list[str] = []
    subsystem_overlap_notes: list[str] = []
    semantic_redundancy_notes: list[str] = []
    boundary_resolution_notes = [dict(note) for note in BOUNDARY_RESOLUTION_NOTES]
    authority_drift_findings: list[str] = []

    if not not_computable_reasons:
        duplicate_id_conflicts = _collect_duplicate_values(
            candidate.candidate_id for candidate in candidates
        )
        schema_conflicts = _collect_duplicate_values(
            candidate.schema_name for candidate in candidates
        )
        rune_conflicts = _collect_duplicate_values(
            str(candidate["rune_id"])
            for candidate in candidates
            if isinstance(candidate.get("rune_id"), str) and candidate.get("rune_id")
        )
        metric_conflicts = _collect_duplicate_values(
            str(candidate["metric_id"])
            for candidate in candidates
            if isinstance(candidate.get("metric_id"), str) and candidate.get("metric_id")
        )
        subsystem_overlap_notes = _subsystem_overlap_notes(candidates)
        semantic_redundancy_notes = _semantic_overlap_notes(candidates)

        authority_drift_findings = _authority_drift_findings(normalized_p98 or {}, candidates)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        scan_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Upstream P98 packet is missing, malformed, non-pass, structurally invalid, or on the wrong chain."
        )
        recommended_resolution = (
            "Provide a valid PASS P98 packet for P99 cross-drop conflict scanning."
        )
    elif authority_drift_findings:
        status = "REJECTED_AUTHORITY_DRIFT"
        scan_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Authority drift or prohibited candidate authority requests were detected; promotion remains blocked."
        )
        recommended_resolution = (
            "Clear all authority drift findings and keep every authority lock false."
        )
    else:
        has_hard_conflicts = any(
            [duplicate_id_conflicts, schema_conflicts, rune_conflicts, metric_conflicts]
        )
        has_advisory_conflicts = bool(subsystem_overlap_notes or semantic_redundancy_notes)
        if has_hard_conflicts:
            status = "NOT_COMPUTABLE"
            scan_status = "NOT_COMPUTABLE"
            recommended_next_lane = "NOT_COMPUTABLE"
            recommended_next_lane_reason = (
                "Duplicate identifiers or schema/rune/metric conflicts require upstream correction before deterministic scan pass."
            )
            recommended_resolution = (
                "Resolve duplicate identity and schema/rune/metric conflicts upstream, then rerun P99."
            )
        elif has_advisory_conflicts:
            status = "PASS_WITH_ADVISORY_CONFLICTS"
            scan_status = "COMPLETE_ADVISORY_CONFLICTS"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
            recommended_next_lane_reason = (
                "Conflicts are advisory and bounded by explicit Drop006/Drop007 boundary separation notes."
            )
            recommended_resolution = (
                "Maintain advisory boundaries and operator review separation without automatic conflict repair."
            )
        else:
            status = "PASS_CLEAN"
            scan_status = "COMPLETE_NO_CONFLICTS"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
            recommended_next_lane_reason = (
                "No duplicate/schema/rune/metric conflicts and no advisory semantic/subsystem overlaps were detected."
            )
            recommended_resolution = "No conflict remediation needed; preserve advisory-only posture."

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_stabilization_plan_status": (
            normalized_p98.get("status") if normalized_p98 is not None else None
        ),
        "scan_status": scan_status,
        "duplicate_id_conflicts": duplicate_id_conflicts,
        "schema_conflicts": schema_conflicts,
        "rune_conflicts": rune_conflicts,
        "metric_conflicts": metric_conflicts,
        "subsystem_overlap_notes": subsystem_overlap_notes,
        "semantic_redundancy_notes": semantic_redundancy_notes,
        "boundary_resolution_notes": boundary_resolution_notes,
        "authority_drift_findings": authority_drift_findings,
        "recommended_resolution": recommended_resolution,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p98_research_shadow_stabilization_proof_plan",
            "mapping_method": "deterministic_cross_drop_conflict_scan",
            "drop_order": list(REQUIRED_DROPS),
            "boundary_rules": [
                "hidden_intent_is_never_known_intent",
                "proactivity_is_never_autonomous_execution",
                "intent_graph_dependency_is_never_confirmed_intent",
                "endpoint_constraint_is_never_known_goal",
                "calibration_projection_is_never_forecast_weight_mutation",
                "aal_viz_is_projection_only",
                "conflict_scan_is_not_repair_authority",
            ],
            "gated_recommendation_rule": "recommend_p100_only_when_status_pass_clean_or_pass_with_advisory_conflicts",
            "candidate_count": len(candidates),
        },
    }
    return _finalize(packet_base)


def write_research_cross_drop_conflict_scan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
