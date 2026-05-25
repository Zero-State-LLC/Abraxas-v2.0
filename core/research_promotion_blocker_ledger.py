from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchPromotionBlockerLedger.v1"
LANE_ID = "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
REQUIRED_P104_ARTIFACT_TYPE = "ResearchBoundaryDecayAnalysis.v1"
REQUIRED_P104_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER_CONTINUE"

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

MANDATORY_BLOCKER_CATEGORIES: tuple[str, ...] = (
    "implementation_authority_blocker",
    "runtime_mutation_blocker",
    "canon_promotion_blocker",
    "forecast_influence_blocker",
    "scheduler_mutation_blocker",
    "autonomous_execution_blocker",
    "aal_viz_inference_authority_blocker",
    "operator_review_blocker",
    "provenance_completeness_blocker",
    "replay_stability_blocker",
    "boundary_stability_blocker",
    "safety_case_blocker",
)

AUTHORITY_BLOCKER_CATEGORIES: frozenset[str] = frozenset(
    {
        "implementation_authority_blocker",
        "runtime_mutation_blocker",
        "canon_promotion_blocker",
        "forecast_influence_blocker",
        "scheduler_mutation_blocker",
        "autonomous_execution_blocker",
        "aal_viz_inference_authority_blocker",
    }
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, str)]


def _validate_p104_packet(p104_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p104_packet is None:
        return ["p104_packet_missing"], None
    if not isinstance(p104_packet, dict):
        return ["p104_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p104_packet.get("artifact_type") != REQUIRED_P104_ARTIFACT_TYPE:
        reasons.append(
            f"p104_artifact_type_mismatch:{p104_packet.get('artifact_type')!r}"
        )
    if p104_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p104_lane_id_mismatch:{p104_packet.get('lane_id')!r}")
    if p104_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p104_canonical_status_mismatch:{p104_packet.get('canonical_status')!r}"
        )
    if p104_packet.get("advisory_only") is not True:
        reasons.append("p104_advisory_only_not_true")
    if p104_packet.get("projection_only") is not True:
        reasons.append("p104_projection_only_not_true")

    p104_status = p104_packet.get("status")
    p104_boundary_status = p104_packet.get("boundary_decay_analysis_status")
    if not (
        p104_status == "BOUNDARY_DECAY_ANALYSIS_EMITTED"
        and p104_boundary_status == "BOUNDARY_STABLE"
    ):
        reasons.append(f"p104_status_not_emitted_stable:{p104_status!r}")
        reasons.append(
            "p104_boundary_decay_analysis_status_not_stable:"
            f"{p104_boundary_status!r}"
        )

    if p104_packet.get("recommended_next_lane") != REQUIRED_P104_RECOMMENDATION:
        reasons.append(
            "p104_recommendation_chain_mismatch:"
            f"{p104_packet.get('recommended_next_lane')!r}"
        )

    boundary_stable_candidates = p104_packet.get("boundary_stable_candidates")
    if not isinstance(boundary_stable_candidates, list):
        reasons.append("p104_boundary_stable_candidates_malformed")
    else:
        for candidate in boundary_stable_candidates:
            if not isinstance(candidate, str):
                reasons.append("p104_boundary_stable_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p104_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p104_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p104_{field_name}_entry_malformed")

    authority_locks = p104_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p104_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p104_authority_lock_missing:{key}")

    return sorted(set(reasons)), p104_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "boundary_stable_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "boundary_stable_candidates",
    ):
        value = packet.get(field_name)
        extracted[field_name] = (
            [entry for entry in value if isinstance(entry, str)]
            if isinstance(value, list)
            else []
        )
    return extracted


def _detect_authority_drift_p104(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p104_reports_authority_drift")

    if packet.get("boundary_decay_analysis_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p104_boundary_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p104_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_blocker_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _to_bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _build_candidate_blocker_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        reviewed_blocker_categories: list[str] = []
        active_blocker_categories = list(MANDATORY_BLOCKER_CATEGORIES)
        waived_blocker_categories: list[str] = []
        blocker_review_complete = False
        operator_review_observed = False
        provenance_complete_observed = False
        replay_stability_observed = False
        boundary_stability_observed = False
        authority_drift_observed = False
        notes = ""
    else:
        candidate_id_observed = observation.get("candidate_id")
        reviewed_blocker_categories = [
            category
            for category in _normalize_string_list(observation.get("reviewed_blocker_categories"))
            if category in MANDATORY_BLOCKER_CATEGORIES
        ]
        active_input = [
            category
            for category in _normalize_string_list(observation.get("active_blocker_categories"))
            if category in MANDATORY_BLOCKER_CATEGORIES
        ]
        waived_blocker_categories = [
            category
            for category in _normalize_string_list(observation.get("waived_blocker_categories"))
            if category in MANDATORY_BLOCKER_CATEGORIES
        ]

        blocker_review_complete_raw = _to_bool_or_none(observation.get("blocker_review_complete"))
        operator_review_observed_raw = _to_bool_or_none(observation.get("operator_review_observed"))
        provenance_complete_observed_raw = _to_bool_or_none(
            observation.get("provenance_complete_observed")
        )
        replay_stability_observed_raw = _to_bool_or_none(
            observation.get("replay_stability_observed")
        )
        boundary_stability_observed_raw = _to_bool_or_none(
            observation.get("boundary_stability_observed")
        )
        authority_drift_observed_raw = _to_bool_or_none(
            observation.get("authority_drift_observed")
        )

        blocker_review_complete = blocker_review_complete_raw is True
        operator_review_observed = operator_review_observed_raw is True
        provenance_complete_observed = provenance_complete_observed_raw is True
        replay_stability_observed = replay_stability_observed_raw is True
        boundary_stability_observed = boundary_stability_observed_raw is True
        authority_drift_observed = authority_drift_observed_raw is True
        notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""

        unreviewed_mandatory = {
            category
            for category in MANDATORY_BLOCKER_CATEGORIES
            if category not in reviewed_blocker_categories
        }
        active_set = set(active_input).union(unreviewed_mandatory)

        waiver_allowed_for_authority = blocker_review_complete and operator_review_observed
        for waived_category in waived_blocker_categories:
            if (
                waived_category in AUTHORITY_BLOCKER_CATEGORIES
                and not waiver_allowed_for_authority
            ):
                continue
            active_set.discard(waived_category)

        active_blocker_categories = sorted(active_set)

        if candidate_id_observed is not None and candidate_id_observed != candidate_id:
            notes = f"{notes} [candidate_id_mismatch]".strip()

    missing_blocker_requirements: list[str] = []

    for category in MANDATORY_BLOCKER_CATEGORIES:
        if category not in reviewed_blocker_categories:
            missing_blocker_requirements.append(
                f"mandatory_blocker_not_reviewed:{category}"
            )

    if not blocker_review_complete:
        missing_blocker_requirements.append("blocker_review_complete_not_true")
    if not operator_review_observed:
        missing_blocker_requirements.append("operator_review_observed_not_true")
    if not provenance_complete_observed:
        missing_blocker_requirements.append("provenance_complete_observed_not_true")
    if not replay_stability_observed:
        missing_blocker_requirements.append("replay_stability_observed_not_true")
    if not boundary_stability_observed:
        missing_blocker_requirements.append("boundary_stability_observed_not_true")

    if authority_drift_observed:
        missing_blocker_requirements.append("authority_drift_observed")
        promotion_blocker_status = "PROMOTION_REJECTED_AUTHORITY_DRIFT"
    else:
        if (
            blocker_review_complete
            and operator_review_observed
            and provenance_complete_observed
            and replay_stability_observed
            and boundary_stability_observed
            and all(
                category in reviewed_blocker_categories
                for category in MANDATORY_BLOCKER_CATEGORIES
            )
            and not active_blocker_categories
        ):
            promotion_blocker_status = "BLOCKER_REVIEW_COMPLETE"
        elif reviewed_blocker_categories:
            promotion_blocker_status = "BLOCKER_REVIEW_IN_PROGRESS"
        else:
            promotion_blocker_status = "PROMOTION_BLOCKED"

    status: dict[str, Any] = {
        "candidate_id": candidate_id,
        "reviewed_blocker_categories": sorted(set(reviewed_blocker_categories)),
        "active_blocker_categories": sorted(set(active_blocker_categories)),
        "waived_blocker_categories": sorted(set(waived_blocker_categories)),
        "blocker_review_complete": blocker_review_complete,
        "operator_review_observed": operator_review_observed,
        "provenance_complete_observed": provenance_complete_observed,
        "replay_stability_observed": replay_stability_observed,
        "boundary_stability_observed": boundary_stability_observed,
        "authority_drift_observed": authority_drift_observed,
        "missing_blocker_requirements": sorted(set(missing_blocker_requirements)),
        "promotion_blocker_status": promotion_blocker_status,
    }
    if notes:
        status["notes"] = notes

    authority_findings: list[str] = []
    if authority_drift_observed:
        authority_findings.append(f"candidate_authority_drift_observed:{candidate_id}")

    return status, authority_findings


def _build_candidate_blocker_statuses(
    *,
    boundary_stable_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_blocker_statuses: list[dict[str, Any]] = []
    promotion_blocked_candidates: list[str] = []
    blocker_review_complete_candidates: list[str] = []
    blocker_review_incomplete_candidates: list[str] = []
    missing_blocker_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in boundary_stable_candidates:
        observation = _get_candidate_observation(observations_packet, candidate_id)
        status, candidate_authority_findings = _build_candidate_blocker_status(
            candidate_id,
            observation,
        )
        candidate_blocker_statuses.append(status)
        authority_findings.extend(candidate_authority_findings)

        missing = status["missing_blocker_requirements"]
        if isinstance(missing, list) and missing:
            missing_blocker_requirements[candidate_id] = list(missing)

        blocker_status = status["promotion_blocker_status"]
        if blocker_status == "BLOCKER_REVIEW_COMPLETE":
            blocker_review_complete_candidates.append(candidate_id)
        else:
            promotion_blocked_candidates.append(candidate_id)
            blocker_review_incomplete_candidates.append(candidate_id)

    return (
        candidate_blocker_statuses,
        promotion_blocked_candidates,
        blocker_review_complete_candidates,
        blocker_review_incomplete_candidates,
        missing_blocker_requirements,
        sorted(set(authority_findings)),
    )


def build_research_promotion_blocker_ledger(
    *,
    p104_packet: dict[str, Any] | None = None,
    blocker_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p104 = _validate_p104_packet(p104_packet)
    candidate_lists = _extract_candidate_lists(normalized_p104)
    authority_drift_findings = _detect_authority_drift_p104(normalized_p104)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    boundary_stable_candidates = candidate_lists["boundary_stable_candidates"]

    if not not_computable_reasons and not boundary_stable_candidates:
        not_computable_reasons = ["p104_no_boundary_stable_candidates"]

    candidate_blocker_statuses: list[dict[str, Any]] = []
    promotion_blocked_candidates: list[str] = []
    blocker_review_complete_candidates: list[str] = []
    blocker_review_incomplete_candidates: list[str] = []
    missing_blocker_requirements: dict[str, list[str]] = {}

    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_blocker_statuses,
            promotion_blocked_candidates,
            blocker_review_complete_candidates,
            blocker_review_incomplete_candidates,
            missing_blocker_requirements,
            observation_drift_findings,
        ) = _build_candidate_blocker_statuses(
            boundary_stable_candidates=boundary_stable_candidates,
            observations_packet=blocker_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        promotion_blocker_ledger_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P104 or blocker observations report authority drift; P105 remains anti-promotion "
            "advisory governance and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        promotion_blocker_ledger_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P104 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, or has no boundary_stable_candidates; P105 cannot compute."
        )
    else:
        status = "PROMOTION_BLOCKER_LEDGER_EMITTED"
        promotion_blocker_ledger_status = "EMITTED"

        all_candidates_complete = (
            len(boundary_stable_candidates) > 0
            and len(blocker_review_complete_candidates) == len(boundary_stable_candidates)
            and not blocker_review_incomplete_candidates
        )

        if all_candidates_complete:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every boundary-stable candidate has complete blocker review with explicit "
                "operator/provenance/replay/boundary confirmations and no authority drift; "
                "proceed to advisory P106 eligibility dossier evaluation."
            )
        else:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more boundary-stable candidates still have active or incomplete "
                "promotion blockers; continue P105 anti-promotion governance review."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_boundary_decay_analysis_status": (
            normalized_p104.get("status") if isinstance(normalized_p104, dict) else None
        ),
        "promotion_blocker_ledger_status": promotion_blocker_ledger_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": boundary_stable_candidates,
        "promotion_blocked_candidates": promotion_blocked_candidates,
        "blocker_review_complete_candidates": blocker_review_complete_candidates,
        "blocker_review_incomplete_candidates": blocker_review_incomplete_candidates,
        "candidate_blocker_statuses": candidate_blocker_statuses,
        "mandatory_blocker_categories": list(MANDATORY_BLOCKER_CATEGORIES),
        "missing_blocker_requirements": missing_blocker_requirements,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p104_research_boundary_decay_analysis",
            "mapping_method": "deterministic_promotion_blocker_ledger",
            "required_blocker_observation_fields": [
                "candidate_id",
                "reviewed_blocker_categories",
                "active_blocker_categories",
                "waived_blocker_categories",
                "blocker_review_complete",
                "operator_review_observed",
                "provenance_complete_observed",
                "replay_stability_observed",
                "boundary_stability_observed",
                "authority_drift_observed",
                "notes",
            ],
            "mandatory_blocker_categories": list(MANDATORY_BLOCKER_CATEGORIES),
            "boundary_rules": [
                "promotion_blocker_ledger_is_anti_promotion_governance",
                "promotion_blocker_ledger_is_not_implementation_authority",
                "promotion_blocker_ledger_is_not_canon_promotion",
                "promotion_blocker_ledger_is_not_production_activation",
                "promotion_blocker_ledger_is_not_runtime_mutation",
                "promotion_blocker_ledger_is_not_scheduler_authority",
                "promotion_blocker_ledger_is_not_forecast_weight_authority",
                "promotion_blocker_ledger_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p106_only_when_every_boundary_stable_candidate_has_full_blocker_review_complete_with_operator_provenance_replay_boundary_observations_and_no_authority_drift"
            ),
            "p104_status": (
                normalized_p104.get("status") if isinstance(normalized_p104, dict) else None
            ),
            "p104_artifact_type": (
                normalized_p104.get("artifact_type")
                if isinstance(normalized_p104, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_promotion_blocker_ledger(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
