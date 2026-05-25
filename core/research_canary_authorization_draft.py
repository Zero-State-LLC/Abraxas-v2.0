from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P111 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT implement P112 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationDraft.v1"
LANE_ID = "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD"
REQUIRED_P110_ARTIFACT_TYPE = "ResearchCanaryPlanReviewRecord.v1"
REQUIRED_P110_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT_CONTINUE"

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
    "canary_authorization",
    "canary_authorization_execution",
)

P110_AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
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
    "canary_authorization",
)

REQUIRED_AUTHORIZATION_DRAFT_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "plan_review_complete_observed",
    "authorization_scope_defined",
    "authorization_conditions_defined",
    "rollback_binding_defined",
    "monitoring_binding_defined",
    "blast_radius_binding_defined",
    "exit_criteria_binding_defined",
    "operator_authorization_required",
    "execution_disabled_confirmed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

AUTHORIZATION_DRAFT_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "plan_review_complete_observed",
    "authorization_scope_defined",
    "authorization_conditions_defined",
    "rollback_binding_defined",
    "monitoring_binding_defined",
    "blast_radius_binding_defined",
    "exit_criteria_binding_defined",
    "operator_authorization_required",
    "execution_disabled_confirmed",
    "provenance_bundle_attached",
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


def _validate_p110_packet(p110_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p110_packet is None:
        return ["p110_packet_missing"], None
    if not isinstance(p110_packet, dict):
        return ["p110_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p110_packet.get("artifact_type") != REQUIRED_P110_ARTIFACT_TYPE:
        reasons.append(
            f"p110_artifact_type_mismatch:{p110_packet.get('artifact_type')!r}"
        )
    if p110_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p110_lane_id_mismatch:{p110_packet.get('lane_id')!r}")
    if p110_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p110_canonical_status_mismatch:{p110_packet.get('canonical_status')!r}"
        )
    if p110_packet.get("advisory_only") is not True:
        reasons.append("p110_advisory_only_not_true")
    if p110_packet.get("projection_only") is not True:
        reasons.append("p110_projection_only_not_true")

    p110_status = p110_packet.get("status")
    p110_review_status = p110_packet.get("canary_plan_review_record_status")
    if p110_status != "CANARY_PLAN_REVIEW_RECORD_EMITTED":
        reasons.append(f"p110_status_not_emitted:{p110_status!r}")
    if p110_review_status not in (
        "CANARY_PLAN_REVIEW_COMPLETE",
        "CANARY_PLAN_REVIEW_INCOMPLETE",
    ):
        reasons.append(
            "p110_canary_plan_review_record_status_not_pass_or_incomplete:"
            f"{p110_review_status!r}"
        )

    if p110_packet.get("recommended_next_lane") != REQUIRED_P110_RECOMMENDATION:
        reasons.append(
            "p110_recommendation_chain_mismatch:"
            f"{p110_packet.get('recommended_next_lane')!r}"
        )

    plan_review_complete_candidates = p110_packet.get("plan_review_complete_candidates")
    if not isinstance(plan_review_complete_candidates, list):
        reasons.append("p110_plan_review_complete_candidates_malformed")
    elif not plan_review_complete_candidates:
        reasons.append("p110_no_plan_review_complete_candidates")
    elif any(not isinstance(candidate, str) for candidate in plan_review_complete_candidates):
        reasons.append("p110_plan_review_complete_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p110_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p110_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p110_{field_name}_entry_malformed")

    authority_locks = p110_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p110_authority_locks_malformed")
    else:
        for key in P110_AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p110_authority_lock_missing:{key}")

    return sorted(set(reasons)), p110_packet


def _extract_candidate_lists(
    packet: dict[str, Any] | None,
) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "plan_review_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "plan_review_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p110(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p110_reports_authority_drift")

    if (
        packet.get("canary_plan_review_record_status")
        == "CANARY_PLAN_REVIEW_REJECTED_AUTHORITY_DRIFT"
    ):
        findings.append("p110_review_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in P110_AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p110_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_authorization_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_authorization_draft_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_authorization_draft_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "plan_review_complete_observed": False,
            "authorization_scope_defined": False,
            "authorization_conditions_defined": False,
            "rollback_binding_defined": False,
            "monitoring_binding_defined": False,
            "blast_radius_binding_defined": False,
            "exit_criteria_binding_defined": False,
            "operator_authorization_required": False,
            "execution_disabled_confirmed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_authorization_draft_requirements": [
                "authorization_draft_observations_missing"
            ],
            "canary_authorization_draft_status": "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE",
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    criteria: dict[str, bool] = {}
    for field in AUTHORIZATION_DRAFT_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_authorization_draft_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in AUTHORIZATION_DRAFT_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_authorization_draft_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_authorization_draft_requirements.append("authority_drift_observed")
        authority_findings.append(
            f"candidate_authorization_draft_authority_drift_observed:{candidate_id}"
        )
        canary_authorization_draft_status = (
            "CANARY_AUTHORIZATION_DRAFT_REJECTED_AUTHORITY_DRIFT"
        )
    elif not missing_authorization_draft_requirements:
        canary_authorization_draft_status = "CANARY_AUTHORIZATION_DRAFT_COMPLETE"
    else:
        canary_authorization_draft_status = "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "plan_review_complete_observed": criteria["plan_review_complete_observed"],
        "authorization_scope_defined": criteria["authorization_scope_defined"],
        "authorization_conditions_defined": criteria[
            "authorization_conditions_defined"
        ],
        "rollback_binding_defined": criteria["rollback_binding_defined"],
        "monitoring_binding_defined": criteria["monitoring_binding_defined"],
        "blast_radius_binding_defined": criteria["blast_radius_binding_defined"],
        "exit_criteria_binding_defined": criteria["exit_criteria_binding_defined"],
        "operator_authorization_required": criteria["operator_authorization_required"],
        "execution_disabled_confirmed": criteria["execution_disabled_confirmed"],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_authorization_draft_requirements": sorted(
            set(missing_authorization_draft_requirements)
        ),
        "canary_authorization_draft_status": canary_authorization_draft_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status_dict["notes"] = notes

    return status_dict, authority_findings


def _build_candidate_authorization_draft_statuses(
    *,
    plan_review_complete_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_statuses: list[dict[str, Any]] = []
    complete_candidates: list[str] = []
    incomplete_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in plan_review_complete_candidates:
        observation = _get_candidate_authorization_observation(
            observations_packet, candidate_id
        )
        candidate_status, candidate_authority_findings = (
            _build_candidate_authorization_draft_status(candidate_id, observation)
        )
        candidate_statuses.append(candidate_status)
        authority_findings.extend(candidate_authority_findings)

        missing = candidate_status["missing_authorization_draft_requirements"]
        if isinstance(missing, list) and missing:
            missing_requirements[candidate_id] = list(missing)

        if (
            candidate_status["canary_authorization_draft_status"]
            == "CANARY_AUTHORIZATION_DRAFT_COMPLETE"
        ):
            complete_candidates.append(candidate_id)
        else:
            incomplete_candidates.append(candidate_id)

    return (
        candidate_statuses,
        complete_candidates,
        incomplete_candidates,
        missing_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_authorization_draft(
    *,
    p110_packet: dict[str, Any] | None = None,
    authorization_draft_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p110 = _validate_p110_packet(p110_packet)
    candidate_lists = _extract_candidate_lists(normalized_p110)
    authority_drift_findings = _detect_authority_drift_p110(normalized_p110)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    plan_review_complete_candidates = candidate_lists["plan_review_complete_candidates"]

    candidate_statuses: list[dict[str, Any]] = []
    complete_candidates: list[str] = []
    incomplete_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            complete_candidates,
            incomplete_candidates,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_authorization_draft_statuses(
            plan_review_complete_candidates=plan_review_complete_candidates,
            observations_packet=authorization_draft_observations_packet,
        )

    all_authority_drift = sorted(
        set(authority_drift_findings + observation_drift_findings)
    )

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_authorization_draft_status = "CANARY_AUTHORIZATION_DRAFT_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P110 or authorization draft observations report authority drift or "
            "authority lock drift; P111 remains advisory-only and cannot proceed "
            "while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        canary_authorization_draft_status = "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P110 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, does not recommend P111, or has no "
            "plan_review_complete_candidates; P111 cannot compute."
        )
    else:
        status = "CANARY_AUTHORIZATION_DRAFT_EMITTED"
        all_candidates_complete = (
            len(plan_review_complete_candidates) > 0
            and len(complete_candidates) == len(plan_review_complete_candidates)
            and not incomplete_candidates
        )
        if all_candidates_complete:
            canary_authorization_draft_status = "CANARY_AUTHORIZATION_DRAFT_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete canary authorization draft "
                "observations, execution remains disabled, and no authority drift "
                "exists; proceed to advisory P112 authorization review record."
            )
        else:
            canary_authorization_draft_status = "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required canary "
                "authorization draft observations; continue P111."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_canary_plan_review_record_status": (
            normalized_p110.get("status")
            if isinstance(normalized_p110, dict)
            else None
        ),
        "canary_authorization_draft_status": canary_authorization_draft_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": plan_review_complete_candidates,
        "authorization_draft_complete_candidates": complete_candidates,
        "authorization_draft_incomplete_candidates": incomplete_candidates,
        "candidate_authorization_draft_statuses": candidate_statuses,
        "required_authorization_draft_observations": list(
            REQUIRED_AUTHORIZATION_DRAFT_OBSERVATION_FIELDS
        ),
        "missing_authorization_draft_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p110_research_canary_plan_review_record",
            "mapping_method": "deterministic_canary_authorization_draft",
            "required_authorization_draft_observation_fields": list(
                REQUIRED_AUTHORIZATION_DRAFT_OBSERVATION_FIELDS
            ),
            "authorization_draft_completeness_fields": list(
                AUTHORIZATION_DRAFT_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "canary_authorization_draft_is_not_canary_authorization",
                "canary_authorization_draft_is_not_canary_activation",
                "canary_authorization_draft_is_not_canary_plan_execution",
                "canary_authorization_draft_is_not_implementation_authority",
                "canary_authorization_draft_is_not_canon_promotion",
                "canary_authorization_draft_is_not_production_activation",
                "canary_authorization_draft_is_not_runtime_mutation",
                "canary_authorization_draft_is_not_scheduler_authority",
                "canary_authorization_draft_is_not_forecast_weight_authority",
                "canary_authorization_draft_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p112_only_when_every_analyzed_candidate_has_complete_"
                "authorization_draft_observations_and_no_authority_drift"
            ),
            "p110_status": (
                normalized_p110.get("status")
                if isinstance(normalized_p110, dict)
                else None
            ),
            "p110_artifact_type": (
                normalized_p110.get("artifact_type")
                if isinstance(normalized_p110, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_canary_authorization_draft(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
