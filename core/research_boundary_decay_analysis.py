from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchBoundaryDecayAnalysis.v1"
LANE_ID = "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P103_RESEARCH_SHADOW_REPLAY_AUDIT"
REQUIRED_P103_ARTIFACT_TYPE = "ResearchShadowReplayAudit.v1"
REQUIRED_P103_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS_CONTINUE"
SEMANTIC_DRIFT_MAX_STABLE = 0.15
MIN_DECAY_WINDOW_CYCLES = 3

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

BOUNDARY_DECAY_STATUSES: tuple[str, ...] = (
    "BOUNDARY_DECAY_NOT_OBSERVED",
    "BOUNDARY_DECAY_IN_PROGRESS",
    "BOUNDARY_STABLE",
    "BOUNDARY_DECAY_DETECTED",
    "BOUNDARY_DECAY_BLOCKED_MISSING_OBSERVATIONS",
    "BOUNDARY_REJECTED_AUTHORITY_DRIFT",
)

_REQUIRED_BOUNDARY_FIELDS: tuple[str, ...] = (
    "boundary_definition_present",
    "overlap_with_other_candidates",
    "semantic_drift_score",
    "authority_boundary_leakage_observed",
    "forecast_boundary_leakage_observed",
    "runtime_boundary_leakage_observed",
    "aal_viz_projection_only_observed",
    "operator_review_observed",
    "decay_window_cycles_observed",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _validate_candidate_list(
    packet: dict[str, Any], field_name: str, reasons: list[str]
) -> list[str]:
    value = packet.get(field_name)
    if not isinstance(value, list):
        reasons.append(f"p103_{field_name}_malformed")
        return []

    normalized: list[str] = []
    for candidate in value:
        if not isinstance(candidate, str):
            reasons.append(f"p103_{field_name}_entry_malformed")
            continue
        normalized.append(candidate)
    return normalized


def _validate_p103_packet(p103_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p103_packet is None:
        return ["p103_packet_missing"], None
    if not isinstance(p103_packet, dict):
        return ["p103_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p103_packet.get("artifact_type") != REQUIRED_P103_ARTIFACT_TYPE:
        reasons.append(
            f"p103_artifact_type_mismatch:{p103_packet.get('artifact_type')!r}"
        )
    if p103_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p103_lane_id_mismatch:{p103_packet.get('lane_id')!r}")
    if p103_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p103_canonical_status_mismatch:{p103_packet.get('canonical_status')!r}"
        )
    if p103_packet.get("advisory_only") is not True:
        reasons.append("p103_advisory_only_not_true")
    if p103_packet.get("projection_only") is not True:
        reasons.append("p103_projection_only_not_true")

    p103_status = p103_packet.get("status")
    p103_replay_status = p103_packet.get("shadow_replay_audit_status")
    valid_emitted_status = (
        p103_status == "SHADOW_REPLAY_AUDIT_EMITTED"
        and p103_replay_status == "EMITTED"
    )
    valid_rejected_drift_status = (
        p103_status == "REJECTED_AUTHORITY_DRIFT"
        and p103_replay_status == "REJECTED_AUTHORITY_DRIFT"
    )

    if not (valid_emitted_status or valid_rejected_drift_status):
        reasons.append(f"p103_status_not_emitted_or_rejected_drift:{p103_status!r}")
        reasons.append(
            "p103_shadow_replay_audit_status_not_emitted_or_rejected_drift:"
            f"{p103_replay_status!r}"
        )

    if valid_emitted_status:
        if p103_packet.get("recommended_next_lane") != REQUIRED_P103_RECOMMENDATION:
            reasons.append(
                "p103_recommendation_chain_mismatch:"
                f"{p103_packet.get('recommended_next_lane')!r}"
            )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "replay_pass_candidates",
    ):
        _validate_candidate_list(p103_packet, field_name, reasons)

    authority_locks = p103_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p103_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p103_authority_lock_missing:{key}")

    return sorted(set(reasons)), p103_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "replay_pass_candidates": [],
        }

    out: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "replay_pass_candidates",
    ):
        value = packet.get(field_name)
        out[field_name] = (
            [v for v in value if isinstance(v, str)] if isinstance(value, list) else []
        )
    return out


def _detect_authority_drift_p103(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p103_reports_authority_drift")

    if packet.get("shadow_replay_audit_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p103_shadow_replay_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p103_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_boundary_observation(
    observations_packet: dict[str, Any] | None, candidate_id: str
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_boundary_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _normalize_overlap_entries(raw_overlap: Any) -> tuple[list[str], bool]:
    if raw_overlap is None:
        return [], True
    if not isinstance(raw_overlap, list):
        return [], False

    normalized: list[str] = []
    for item in raw_overlap:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            classification = item.get("classification")
            if isinstance(classification, str):
                normalized.append(classification)
            else:
                return [], False
        else:
            return [], False
    return normalized, True


def _overlap_conflict_exists(overlap_entries: list[str]) -> bool:
    return any(entry != "advisory_non_conflicting" for entry in overlap_entries)


def _to_bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _to_float_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _to_int_or_none(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _build_candidate_boundary_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    boundary_definition_present = _to_bool_or_none(
        observation.get("boundary_definition_present")
    )
    overlap_with_other_candidates, overlap_ok = _normalize_overlap_entries(
        observation.get("overlap_with_other_candidates")
    )
    semantic_drift_score = _to_float_or_none(observation.get("semantic_drift_score"))
    authority_boundary_leakage_observed = _to_bool_or_none(
        observation.get("authority_boundary_leakage_observed")
    )
    forecast_boundary_leakage_observed = _to_bool_or_none(
        observation.get("forecast_boundary_leakage_observed")
    )
    runtime_boundary_leakage_observed = _to_bool_or_none(
        observation.get("runtime_boundary_leakage_observed")
    )
    aal_viz_projection_only_observed = _to_bool_or_none(
        observation.get("aal_viz_projection_only_observed")
    )
    operator_review_observed = _to_bool_or_none(observation.get("operator_review_observed"))
    decay_window_cycles_observed = _to_int_or_none(
        observation.get("decay_window_cycles_observed")
    )

    missing_boundary_requirements: list[str] = []

    if not observation:
        boundary_decay_status = "BOUNDARY_DECAY_NOT_OBSERVED"
        missing_boundary_requirements = list(_REQUIRED_BOUNDARY_FIELDS)
    else:
        if boundary_definition_present is None:
            missing_boundary_requirements.append("boundary_definition_present")
        if not overlap_ok:
            missing_boundary_requirements.append("overlap_with_other_candidates")
        if semantic_drift_score is None:
            missing_boundary_requirements.append("semantic_drift_score")
        elif not 0.0 <= semantic_drift_score <= 1.0:
            missing_boundary_requirements.append("semantic_drift_score_out_of_range")

        if authority_boundary_leakage_observed is None:
            missing_boundary_requirements.append("authority_boundary_leakage_observed")
        if forecast_boundary_leakage_observed is None:
            missing_boundary_requirements.append("forecast_boundary_leakage_observed")
        if runtime_boundary_leakage_observed is None:
            missing_boundary_requirements.append("runtime_boundary_leakage_observed")
        if aal_viz_projection_only_observed is None:
            missing_boundary_requirements.append("aal_viz_projection_only_observed")
        if operator_review_observed is None:
            missing_boundary_requirements.append("operator_review_observed")
        if decay_window_cycles_observed is None or decay_window_cycles_observed < 0:
            missing_boundary_requirements.append("decay_window_cycles_observed")

        leakage_flags = (
            authority_boundary_leakage_observed,
            forecast_boundary_leakage_observed,
            runtime_boundary_leakage_observed,
        )

        if any(flag is True for flag in leakage_flags):
            boundary_decay_status = "BOUNDARY_REJECTED_AUTHORITY_DRIFT"
        elif missing_boundary_requirements:
            boundary_decay_status = "BOUNDARY_DECAY_BLOCKED_MISSING_OBSERVATIONS"
        elif (
            isinstance(decay_window_cycles_observed, int)
            and 0 <= decay_window_cycles_observed < MIN_DECAY_WINDOW_CYCLES
        ):
            boundary_decay_status = "BOUNDARY_DECAY_IN_PROGRESS"
            missing_boundary_requirements.append(
                "decay_window_cycles_observed_below_threshold"
            )
        else:
            stable = (
                boundary_definition_present is True
                and semantic_drift_score is not None
                and semantic_drift_score <= SEMANTIC_DRIFT_MAX_STABLE
                and not _overlap_conflict_exists(overlap_with_other_candidates)
                and authority_boundary_leakage_observed is False
                and forecast_boundary_leakage_observed is False
                and runtime_boundary_leakage_observed is False
                and aal_viz_projection_only_observed is True
                and operator_review_observed is True
                and decay_window_cycles_observed is not None
                and decay_window_cycles_observed >= MIN_DECAY_WINDOW_CYCLES
            )
            boundary_decay_status = "BOUNDARY_STABLE" if stable else "BOUNDARY_DECAY_DETECTED"

            if boundary_definition_present is not True:
                missing_boundary_requirements.append("boundary_definition_present_false")
            if semantic_drift_score is not None and semantic_drift_score > SEMANTIC_DRIFT_MAX_STABLE:
                missing_boundary_requirements.append("semantic_drift_score_above_threshold")
            if _overlap_conflict_exists(overlap_with_other_candidates):
                missing_boundary_requirements.append("overlap_with_other_candidates_conflicting")
            if aal_viz_projection_only_observed is not True:
                missing_boundary_requirements.append(
                    "aal_viz_projection_only_observed_not_true"
                )
            if operator_review_observed is not True:
                missing_boundary_requirements.append("operator_review_observed_not_true")

    status = {
        "candidate_id": candidate_id,
        "boundary_definition_present": boundary_definition_present,
        "overlap_with_other_candidates": overlap_with_other_candidates,
        "semantic_drift_score": semantic_drift_score,
        "authority_boundary_leakage_observed": authority_boundary_leakage_observed,
        "forecast_boundary_leakage_observed": forecast_boundary_leakage_observed,
        "runtime_boundary_leakage_observed": runtime_boundary_leakage_observed,
        "aal_viz_projection_only_observed": aal_viz_projection_only_observed,
        "operator_review_observed": operator_review_observed,
        "decay_window_cycles_observed": decay_window_cycles_observed,
        "missing_boundary_requirements": sorted(set(missing_boundary_requirements)),
        "boundary_decay_status": boundary_decay_status,
    }

    authority_findings: list[str] = []
    if authority_boundary_leakage_observed is True:
        authority_findings.append(
            f"boundary_authority_leakage_observed_candidate:{candidate_id}"
        )
    if forecast_boundary_leakage_observed is True:
        authority_findings.append(
            f"boundary_forecast_leakage_observed_candidate:{candidate_id}"
        )
    if runtime_boundary_leakage_observed is True:
        authority_findings.append(
            f"boundary_runtime_leakage_observed_candidate:{candidate_id}"
        )

    return status, sorted(set(authority_findings))


def _build_candidate_boundary_statuses(
    *,
    replay_pass_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_boundary_statuses: list[dict[str, Any]] = []
    boundary_stable_candidates: list[str] = []
    boundary_decay_candidates: list[str] = []
    boundary_incomplete_candidates: list[str] = []
    missing_boundary_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in replay_pass_candidates:
        observation = _get_candidate_boundary_observation(observations_packet, candidate_id)
        status, candidate_authority_findings = _build_candidate_boundary_status(
            candidate_id,
            observation,
        )
        candidate_boundary_statuses.append(status)
        authority_findings.extend(candidate_authority_findings)

        missing = status["missing_boundary_requirements"]
        if isinstance(missing, list) and missing:
            missing_boundary_requirements[candidate_id] = list(missing)

        decay_status = status["boundary_decay_status"]
        if decay_status == "BOUNDARY_STABLE":
            boundary_stable_candidates.append(candidate_id)
        elif decay_status in (
            "BOUNDARY_DECAY_DETECTED",
            "BOUNDARY_REJECTED_AUTHORITY_DRIFT",
        ):
            boundary_decay_candidates.append(candidate_id)
        else:
            boundary_incomplete_candidates.append(candidate_id)

    return (
        candidate_boundary_statuses,
        boundary_stable_candidates,
        boundary_decay_candidates,
        boundary_incomplete_candidates,
        missing_boundary_requirements,
        sorted(set(authority_findings)),
    )


def build_research_boundary_decay_analysis(
    *,
    p103_packet: dict[str, Any] | None = None,
    boundary_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p103 = _validate_p103_packet(p103_packet)
    candidate_lists = _extract_candidate_lists(normalized_p103)
    authority_drift_findings = _detect_authority_drift_p103(normalized_p103)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    replay_pass_candidates = candidate_lists["replay_pass_candidates"]

    if not not_computable_reasons and not replay_pass_candidates:
        not_computable_reasons = ["p103_no_replay_pass_candidates"]

    candidate_boundary_statuses: list[dict[str, Any]] = []
    boundary_stable_candidates: list[str] = []
    boundary_decay_candidates: list[str] = []
    boundary_incomplete_candidates: list[str] = []
    missing_boundary_requirements: dict[str, list[str]] = {}

    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_boundary_statuses,
            boundary_stable_candidates,
            boundary_decay_candidates,
            boundary_incomplete_candidates,
            missing_boundary_requirements,
            observation_drift_findings,
        ) = _build_candidate_boundary_statuses(
            replay_pass_candidates=replay_pass_candidates,
            observations_packet=boundary_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        boundary_decay_analysis_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P103 or boundary observations report authority drift or leakage; "
            "P104 remains advisory-only and cannot advance while any authority drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        boundary_decay_analysis_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P103 is missing, malformed, non-emitted, wrong-chain, structurally invalid, "
            "non-pass, or has no replay_pass_candidates; P104 cannot compute boundary "
            "decay analysis."
        )
    else:
        all_stable = (
            len(replay_pass_candidates) > 0
            and len(boundary_stable_candidates) == len(replay_pass_candidates)
            and not boundary_decay_candidates
            and not boundary_incomplete_candidates
        )
        status = "BOUNDARY_DECAY_ANALYSIS_EMITTED"
        if all_stable:
            boundary_decay_analysis_status = "BOUNDARY_STABLE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "All replay-pass candidates are boundary-stable with no overlap conflicts, "
                "no leakage, semantic drift <= 0.15, and required review/projection proofs; "
                "proceed to P105 research promotion blocker ledger."
            )
        else:
            if boundary_decay_candidates:
                boundary_decay_analysis_status = "BOUNDARY_DECAY_DETECTED"
            elif boundary_incomplete_candidates:
                boundary_decay_analysis_status = "BOUNDARY_DECAY_INCOMPLETE"
            else:
                boundary_decay_analysis_status = "BOUNDARY_DECAY_IN_PROGRESS"

            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more replay-pass candidates remain incomplete or show decay/conflict "
                "signals; continue deterministic P104 boundary decay analysis."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_shadow_replay_audit_status": (
            normalized_p103.get("status") if isinstance(normalized_p103, dict) else None
        ),
        "boundary_decay_analysis_status": boundary_decay_analysis_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": replay_pass_candidates,
        "boundary_stable_candidates": boundary_stable_candidates,
        "boundary_decay_candidates": boundary_decay_candidates,
        "boundary_incomplete_candidates": boundary_incomplete_candidates,
        "candidate_boundary_statuses": candidate_boundary_statuses,
        "missing_boundary_requirements": missing_boundary_requirements,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p103_research_shadow_replay_audit",
            "mapping_method": "deterministic_boundary_decay_analysis",
            "semantic_drift_max_stable": SEMANTIC_DRIFT_MAX_STABLE,
            "minimum_decay_window_cycles": MIN_DECAY_WINDOW_CYCLES,
            "required_boundary_fields": list(_REQUIRED_BOUNDARY_FIELDS),
            "boundary_rules": [
                "boundary_decay_analysis_is_observation_only",
                "boundary_decay_analysis_is_not_implementation_authority",
                "boundary_decay_analysis_is_not_canon_promotion",
                "boundary_decay_analysis_is_not_production_activation",
                "boundary_decay_analysis_is_not_runtime_mutation",
                "boundary_decay_analysis_is_not_autonomous_execution",
                "boundary_decay_analysis_is_not_forecast_weight_authority",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p105_only_when_every_replay_pass_candidate_is_boundary_stable_and_no_authority_drift_exists"
            ),
            "p103_status": (
                normalized_p103.get("status") if isinstance(normalized_p103, dict) else None
            ),
            "p103_artifact_type": (
                normalized_p103.get("artifact_type")
                if isinstance(normalized_p103, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_boundary_decay_analysis(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
