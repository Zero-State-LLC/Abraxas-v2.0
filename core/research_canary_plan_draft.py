from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryPlanDraft.v1"
LANE_ID = "P109_RESEARCH_CANARY_PLAN_DRAFT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P108_RESEARCH_CANARY_DECISION_RECORD"
REQUIRED_P108_ARTIFACT_TYPE = "ResearchCanaryDecisionRecord.v1"
REQUIRED_P108_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P109_RESEARCH_CANARY_PLAN_DRAFT_CONTINUE"

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
    "canary_activation",
    "canary_authority",
    "canary_plan_execution",
)

P108_AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
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
    "canary_activation",
    "canary_authority",
)

REQUIRED_PLAN_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "canary_scope_defined",
    "rollback_plan_defined",
    "monitoring_plan_defined",
    "blast_radius_defined",
    "exit_criteria_defined",
    "operator_review_required",
    "provenance_bundle_attached",
    "safety_notes_attached",
    "execution_disabled_confirmed",
    "authority_drift_observed",
    "notes",
)

PLAN_DRAFT_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "canary_scope_defined",
    "rollback_plan_defined",
    "monitoring_plan_defined",
    "blast_radius_defined",
    "exit_criteria_defined",
    "operator_review_required",
    "provenance_bundle_attached",
    "safety_notes_attached",
    "execution_disabled_confirmed",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _to_bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, str)]


def _validate_p108_packet(p108_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p108_packet is None:
        return ["p108_packet_missing"], None
    if not isinstance(p108_packet, dict):
        return ["p108_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p108_packet.get("artifact_type") != REQUIRED_P108_ARTIFACT_TYPE:
        reasons.append(
            f"p108_artifact_type_mismatch:{p108_packet.get('artifact_type')!r}"
        )
    if p108_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p108_lane_id_mismatch:{p108_packet.get('lane_id')!r}")
    if p108_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p108_canonical_status_mismatch:{p108_packet.get('canonical_status')!r}"
        )
    if p108_packet.get("advisory_only") is not True:
        reasons.append("p108_advisory_only_not_true")
    if p108_packet.get("projection_only") is not True:
        reasons.append("p108_projection_only_not_true")

    p108_status = p108_packet.get("status")
    p108_record_status = p108_packet.get("canary_decision_record_status")
    if not (
        p108_status == "CANARY_DECISION_RECORD_EMITTED"
        and p108_record_status == "EMITTED"
    ):
        reasons.append(f"p108_status_not_emitted:{p108_status!r}")
        reasons.append(
            "p108_canary_decision_record_status_not_emitted:"
            f"{p108_record_status!r}"
        )

    if p108_packet.get("recommended_next_lane") != REQUIRED_P108_RECOMMENDATION:
        reasons.append(
            "p108_recommendation_chain_mismatch:"
            f"{p108_packet.get('recommended_next_lane')!r}"
        )

    approved_candidates = p108_packet.get("approved_for_future_canary_plan_candidates")
    if not isinstance(approved_candidates, list):
        reasons.append("p108_approved_for_future_canary_plan_candidates_malformed")
    elif not approved_candidates:
        reasons.append("p108_no_approved_for_future_canary_plan_candidates")
    elif any(not isinstance(candidate, str) for candidate in approved_candidates):
        reasons.append("p108_approved_for_future_canary_plan_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p108_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p108_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p108_{field_name}_entry_malformed")

    authority_locks = p108_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p108_authority_locks_malformed")
    else:
        for key in P108_AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p108_authority_lock_missing:{key}")

    return sorted(set(reasons)), p108_packet


def _extract_candidate_lists(
    packet: dict[str, Any] | None,
) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "approved_for_future_canary_plan_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "approved_for_future_canary_plan_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p108(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p108_reports_authority_drift")

    if packet.get("canary_decision_record_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p108_record_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in P108_AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p108_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_plan_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_plan_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "canary_scope_defined": False,
            "rollback_plan_defined": False,
            "monitoring_plan_defined": False,
            "blast_radius_defined": False,
            "exit_criteria_defined": False,
            "operator_review_required": False,
            "provenance_bundle_attached": False,
            "safety_notes_attached": False,
            "execution_disabled_confirmed": False,
            "authority_drift_observed": False,
            "missing_plan_requirements": ["plan_observations_missing"],
            "canary_plan_draft_status": "CANARY_PLAN_DRAFT_INCOMPLETE",
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    criteria: dict[str, bool] = {}
    for field in PLAN_DRAFT_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_plan_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in PLAN_DRAFT_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_plan_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_plan_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_plan_authority_drift_observed:{candidate_id}")
        canary_plan_draft_status = "CANARY_PLAN_DRAFT_REJECTED_AUTHORITY_DRIFT"
    elif not missing_plan_requirements:
        canary_plan_draft_status = "CANARY_PLAN_DRAFT_COMPLETE"
    else:
        canary_plan_draft_status = "CANARY_PLAN_DRAFT_INCOMPLETE"

    status: dict[str, Any] = {
        "candidate_id": candidate_id,
        "canary_scope_defined": criteria["canary_scope_defined"],
        "rollback_plan_defined": criteria["rollback_plan_defined"],
        "monitoring_plan_defined": criteria["monitoring_plan_defined"],
        "blast_radius_defined": criteria["blast_radius_defined"],
        "exit_criteria_defined": criteria["exit_criteria_defined"],
        "operator_review_required": criteria["operator_review_required"],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "safety_notes_attached": criteria["safety_notes_attached"],
        "execution_disabled_confirmed": criteria["execution_disabled_confirmed"],
        "authority_drift_observed": authority_drift_observed,
        "missing_plan_requirements": sorted(set(missing_plan_requirements)),
        "canary_plan_draft_status": canary_plan_draft_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status["notes"] = notes

    return status, authority_findings


def _build_candidate_plan_statuses(
    *,
    approved_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_plan_statuses: list[dict[str, Any]] = []
    complete_candidates: list[str] = []
    incomplete_candidates: list[str] = []
    missing_plan_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in approved_candidates:
        observation = _get_candidate_observation(observations_packet, candidate_id)
        status, candidate_authority_findings = _build_candidate_plan_status(
            candidate_id,
            observation,
        )
        candidate_plan_statuses.append(status)
        authority_findings.extend(candidate_authority_findings)

        missing = status["missing_plan_requirements"]
        if isinstance(missing, list) and missing:
            missing_plan_requirements[candidate_id] = list(missing)

        if status["canary_plan_draft_status"] == "CANARY_PLAN_DRAFT_COMPLETE":
            complete_candidates.append(candidate_id)
        else:
            incomplete_candidates.append(candidate_id)

    return (
        candidate_plan_statuses,
        complete_candidates,
        incomplete_candidates,
        missing_plan_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_plan_draft(
    *,
    p108_packet: dict[str, Any] | None = None,
    plan_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p108 = _validate_p108_packet(p108_packet)
    candidate_lists = _extract_candidate_lists(normalized_p108)
    authority_drift_findings = _detect_authority_drift_p108(normalized_p108)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    approved_candidates = candidate_lists["approved_for_future_canary_plan_candidates"]

    candidate_plan_statuses: list[dict[str, Any]] = []
    complete_candidates: list[str] = []
    incomplete_candidates: list[str] = []
    missing_plan_requirements: dict[str, list[str]] = {}

    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_plan_statuses,
            complete_candidates,
            incomplete_candidates,
            missing_plan_requirements,
            observation_drift_findings,
        ) = _build_candidate_plan_statuses(
            approved_candidates=approved_candidates,
            observations_packet=plan_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_plan_draft_status = "CANARY_PLAN_DRAFT_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P108 or plan observations report authority drift or authority lock drift; "
            "P109 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        canary_plan_draft_status = "CANARY_PLAN_DRAFT_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P108 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, does not recommend P109, or has no approved candidates; "
            "P109 cannot compute."
        )
    else:
        status = "CANARY_PLAN_DRAFT_EMITTED"
        all_candidates_complete = (
            len(approved_candidates) > 0
            and len(complete_candidates) == len(approved_candidates)
            and not incomplete_candidates
        )

        if all_candidates_complete:
            canary_plan_draft_status = "CANARY_PLAN_DRAFT_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete advisory canary plan draft "
                "observations and execution remains disabled; proceed to advisory P110 "
                "plan review record."
            )
        else:
            canary_plan_draft_status = "CANARY_PLAN_DRAFT_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required plan draft "
                "observations or execution-disabled confirmation; continue P109."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_canary_decision_record_status": (
            normalized_p108.get("status") if isinstance(normalized_p108, dict) else None
        ),
        "canary_plan_draft_status": canary_plan_draft_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": approved_candidates,
        "plan_draft_complete_candidates": complete_candidates,
        "plan_draft_incomplete_candidates": incomplete_candidates,
        "candidate_plan_statuses": candidate_plan_statuses,
        "required_plan_observations": list(REQUIRED_PLAN_OBSERVATION_FIELDS),
        "missing_plan_requirements": {
            key: sorted(set(values))
            for key, values in sorted(missing_plan_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p108_research_canary_decision_record",
            "mapping_method": "deterministic_canary_plan_draft",
            "required_plan_observation_fields": list(
                REQUIRED_PLAN_OBSERVATION_FIELDS
            ),
            "plan_draft_completeness_fields": list(PLAN_DRAFT_COMPLETENESS_FIELDS),
            "boundary_rules": [
                "canary_plan_draft_is_not_canary_activation",
                "canary_plan_draft_is_not_plan_execution",
                "canary_plan_draft_is_not_implementation_authority",
                "canary_plan_draft_is_not_canon_promotion",
                "canary_plan_draft_is_not_production_activation",
                "canary_plan_draft_is_not_runtime_mutation",
                "canary_plan_draft_is_not_scheduler_authority",
                "canary_plan_draft_is_not_forecast_weight_authority",
                "canary_plan_draft_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p110_only_when_every_analyzed_candidate_has_complete_"
                "plan_draft_observations_and_no_authority_drift"
            ),
            "p108_status": (
                normalized_p108.get("status")
                if isinstance(normalized_p108, dict)
                else None
            ),
            "p108_artifact_type": (
                normalized_p108.get("artifact_type")
                if isinstance(normalized_p108, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_canary_plan_draft(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
