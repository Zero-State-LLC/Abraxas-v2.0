from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P113 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT authorize canary execution.
# It does NOT grant canary final-precheck authority.
# It does NOT grant canary package authority.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT implement P114 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryFinalPrecheckRecord.v1"
LANE_ID = "P113_RESEARCH_CANARY_FINAL_PRECHECK_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
REQUIRED_P112_ARTIFACT_TYPE = "ResearchCanaryAuthorizationReviewRecord.v1"
REQUIRED_P112_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P113_RESEARCH_CANARY_FINAL_PRECHECK_RECORD_CONTINUE"

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
    "canary_final_precheck_authority",
    "canary_package_authority",
)

P112_AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
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
    "canary_final_precheck_authority",
)

REQUIRED_FINAL_PRECHECK_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "authorization_review_complete_observed",
    "rollback_binding_final_checked",
    "monitoring_binding_final_checked",
    "blast_radius_final_checked",
    "exit_criteria_final_checked",
    "provenance_final_checked",
    "safety_final_checked",
    "execution_disabled_final_confirmed",
    "operator_final_review_observed",
    "authority_drift_observed",
    "notes",
)

FINAL_PRECHECK_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "authorization_review_complete_observed",
    "rollback_binding_final_checked",
    "monitoring_binding_final_checked",
    "blast_radius_final_checked",
    "exit_criteria_final_checked",
    "provenance_final_checked",
    "safety_final_checked",
    "execution_disabled_final_confirmed",
    "operator_final_review_observed",
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


def _validate_p112_packet(p112_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p112_packet is None:
        return ["p112_packet_missing"], None
    if not isinstance(p112_packet, dict):
        return ["p112_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p112_packet.get("artifact_type") != REQUIRED_P112_ARTIFACT_TYPE:
        reasons.append(
            f"p112_artifact_type_mismatch:{p112_packet.get('artifact_type')!r}"
        )
    if p112_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p112_lane_id_mismatch:{p112_packet.get('lane_id')!r}")
    if p112_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p112_canonical_status_mismatch:{p112_packet.get('canonical_status')!r}"
        )
    if p112_packet.get("advisory_only") is not True:
        reasons.append("p112_advisory_only_not_true")
    if p112_packet.get("projection_only") is not True:
        reasons.append("p112_projection_only_not_true")

    p112_status = p112_packet.get("status")
    p112_review_record_status = p112_packet.get("canary_authorization_review_record_status")
    if p112_status != "CANARY_AUTHORIZATION_REVIEW_RECORD_EMITTED":
        reasons.append(f"p112_status_not_emitted:{p112_status!r}")
    if p112_review_record_status not in (
        "CANARY_AUTHORIZATION_REVIEW_COMPLETE",
        "CANARY_AUTHORIZATION_REVIEW_INCOMPLETE",
    ):
        reasons.append(
            "p112_canary_authorization_review_record_status_not_pass_or_incomplete:"
            f"{p112_review_record_status!r}"
        )

    if p112_packet.get("recommended_next_lane") != REQUIRED_P112_RECOMMENDATION:
        reasons.append(
            "p112_recommendation_chain_mismatch:"
            f"{p112_packet.get('recommended_next_lane')!r}"
        )

    authorization_review_complete_candidates = p112_packet.get(
        "authorization_review_complete_candidates"
    )
    if not isinstance(authorization_review_complete_candidates, list):
        reasons.append("p112_authorization_review_complete_candidates_malformed")
    elif not authorization_review_complete_candidates:
        reasons.append("p112_no_authorization_review_complete_candidates")
    elif any(
        not isinstance(candidate, str)
        for candidate in authorization_review_complete_candidates
    ):
        reasons.append("p112_authorization_review_complete_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p112_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p112_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p112_{field_name}_entry_malformed")

    authority_locks = p112_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p112_authority_locks_malformed")
    else:
        for key in P112_AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p112_authority_lock_missing:{key}")

    return sorted(set(reasons)), p112_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "authorization_review_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "authorization_review_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p112(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p112_reports_authority_drift")

    if (
        packet.get("canary_authorization_review_record_status")
        == "CANARY_AUTHORIZATION_REVIEW_REJECTED_AUTHORITY_DRIFT"
    ):
        findings.append("p112_review_record_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"p112_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_final_precheck_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_final_precheck_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_final_precheck_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "authorization_review_complete_observed": False,
            "rollback_binding_final_checked": False,
            "monitoring_binding_final_checked": False,
            "blast_radius_final_checked": False,
            "exit_criteria_final_checked": False,
            "provenance_final_checked": False,
            "safety_final_checked": False,
            "execution_disabled_final_confirmed": False,
            "operator_final_review_observed": False,
            "authority_drift_observed": False,
            "missing_final_precheck_requirements": [
                "final_precheck_observations_missing"
            ],
            "canary_final_precheck_status": "CANARY_FINAL_PRECHECK_INCOMPLETE",
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    criteria: dict[str, bool] = {}
    for field in FINAL_PRECHECK_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_final_precheck_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in FINAL_PRECHECK_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_final_precheck_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_final_precheck_requirements.append("authority_drift_observed")
        authority_findings.append(
            f"candidate_final_precheck_authority_drift_observed:{candidate_id}"
        )
        canary_final_precheck_status = "CANARY_FINAL_PRECHECK_REJECTED_AUTHORITY_DRIFT"
    elif not missing_final_precheck_requirements:
        canary_final_precheck_status = "CANARY_FINAL_PRECHECK_COMPLETE"
    else:
        canary_final_precheck_status = "CANARY_FINAL_PRECHECK_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "authorization_review_complete_observed": criteria[
            "authorization_review_complete_observed"
        ],
        "rollback_binding_final_checked": criteria["rollback_binding_final_checked"],
        "monitoring_binding_final_checked": criteria[
            "monitoring_binding_final_checked"
        ],
        "blast_radius_final_checked": criteria["blast_radius_final_checked"],
        "exit_criteria_final_checked": criteria["exit_criteria_final_checked"],
        "provenance_final_checked": criteria["provenance_final_checked"],
        "safety_final_checked": criteria["safety_final_checked"],
        "execution_disabled_final_confirmed": criteria[
            "execution_disabled_final_confirmed"
        ],
        "operator_final_review_observed": criteria["operator_final_review_observed"],
        "authority_drift_observed": authority_drift_observed,
        "missing_final_precheck_requirements": sorted(
            set(missing_final_precheck_requirements)
        ),
        "canary_final_precheck_status": canary_final_precheck_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status_dict["notes"] = notes

    return status_dict, authority_findings


def _build_candidate_final_precheck_statuses(
    *,
    authorization_review_complete_candidates: list[str],
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

    for candidate_id in authorization_review_complete_candidates:
        observation = _get_candidate_final_precheck_observation(
            observations_packet, candidate_id
        )
        candidate_status, candidate_authority_findings = (
            _build_candidate_final_precheck_status(candidate_id, observation)
        )
        candidate_statuses.append(candidate_status)
        authority_findings.extend(candidate_authority_findings)

        missing = candidate_status["missing_final_precheck_requirements"]
        if isinstance(missing, list) and missing:
            missing_requirements[candidate_id] = list(missing)

        if (
            candidate_status["canary_final_precheck_status"]
            == "CANARY_FINAL_PRECHECK_COMPLETE"
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


def build_research_canary_final_precheck_record(
    *,
    p112_packet: dict[str, Any] | None = None,
    final_precheck_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p112 = _validate_p112_packet(p112_packet)
    candidate_lists = _extract_candidate_lists(normalized_p112)
    authority_drift_findings = _detect_authority_drift_p112(normalized_p112)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    authorization_review_complete_candidates = candidate_lists[
        "authorization_review_complete_candidates"
    ]

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
        ) = _build_candidate_final_precheck_statuses(
            authorization_review_complete_candidates=authorization_review_complete_candidates,
            observations_packet=final_precheck_observations_packet,
        )

    all_authority_drift = sorted(
        set(authority_drift_findings + observation_drift_findings)
    )

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_final_precheck_record_status = (
            "CANARY_FINAL_PRECHECK_REJECTED_AUTHORITY_DRIFT"
        )
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P112 or final precheck observations report authority drift or authority "
            "lock drift; P113 remains advisory-only and cannot proceed while drift "
            "exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        canary_final_precheck_record_status = "CANARY_FINAL_PRECHECK_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P112 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, does not recommend P113, or has no "
            "authorization_review_complete_candidates; P113 cannot compute."
        )
    else:
        status = "CANARY_FINAL_PRECHECK_RECORD_EMITTED"
        all_candidates_complete = (
            len(authorization_review_complete_candidates) > 0
            and len(complete_candidates) == len(authorization_review_complete_candidates)
            and not incomplete_candidates
        )
        if all_candidates_complete:
            canary_final_precheck_record_status = "CANARY_FINAL_PRECHECK_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete canary final precheck "
                "observations and no authority drift exists; proceed to advisory "
                "P114 authorization package draft."
            )
        else:
            canary_final_precheck_record_status = "CANARY_FINAL_PRECHECK_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required canary final "
                "precheck observations; continue P113."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_canary_authorization_review_record_status": (
            normalized_p112.get("status") if isinstance(normalized_p112, dict) else None
        ),
        "canary_final_precheck_record_status": canary_final_precheck_record_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": authorization_review_complete_candidates,
        "final_precheck_complete_candidates": complete_candidates,
        "final_precheck_incomplete_candidates": incomplete_candidates,
        "candidate_final_precheck_statuses": candidate_statuses,
        "required_final_precheck_observations": list(
            REQUIRED_FINAL_PRECHECK_OBSERVATION_FIELDS
        ),
        "missing_final_precheck_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p112_research_canary_authorization_review_record",
            "mapping_method": "deterministic_canary_final_precheck_record",
            "required_final_precheck_observation_fields": list(
                REQUIRED_FINAL_PRECHECK_OBSERVATION_FIELDS
            ),
            "final_precheck_completeness_fields": list(
                FINAL_PRECHECK_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "canary_final_precheck_record_is_not_canary_authorization",
                "canary_final_precheck_record_is_not_canary_activation",
                "canary_final_precheck_record_is_not_canary_plan_execution",
                "canary_final_precheck_record_is_not_package_authority",
                "canary_final_precheck_record_is_not_implementation_authority",
                "canary_final_precheck_record_is_not_canon_promotion",
                "canary_final_precheck_record_is_not_production_activation",
                "canary_final_precheck_record_is_not_runtime_mutation",
                "canary_final_precheck_record_is_not_scheduler_authority",
                "canary_final_precheck_record_is_not_forecast_weight_authority",
                "canary_final_precheck_record_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p114_only_when_every_analyzed_candidate_has_complete_"
                "final_precheck_observations_and_no_authority_drift"
            ),
            "p112_status": (
                normalized_p112.get("status") if isinstance(normalized_p112, dict) else None
            ),
            "p112_artifact_type": (
                normalized_p112.get("artifact_type")
                if isinstance(normalized_p112, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_canary_final_precheck_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
