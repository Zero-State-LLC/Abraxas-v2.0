from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P112 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT authorize canary execution.
# It does NOT promote any candidate to canon.
# It does NOT grant runtime authority.
# It does NOT execute runtime behavior.
# It does NOT create proactive or autonomous behavior.
# It does NOT mutate runtime, scheduler, baseline, canon, or forecast weights.
# It does NOT grant AAL-Viz inference authority.
# It does NOT implement P113 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationReviewRecord.v1"
LANE_ID = "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT"
REQUIRED_P111_ARTIFACT_TYPE = "ResearchCanaryAuthorizationDraft.v1"
REQUIRED_P111_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P113_RESEARCH_CANARY_FINAL_PRECHECK_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD_CONTINUE"
)

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
)

P111_AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
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

REQUIRED_AUTHORIZATION_REVIEW_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "authorization_draft_complete_observed",
    "authorization_scope_review_complete",
    "authorization_conditions_review_complete",
    "rollback_binding_review_complete",
    "monitoring_binding_review_complete",
    "blast_radius_binding_review_complete",
    "exit_criteria_binding_review_complete",
    "operator_authorization_requirement_review_complete",
    "execution_disabled_review_complete",
    "provenance_review_complete",
    "authority_drift_observed",
    "notes",
)

AUTHORIZATION_REVIEW_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "authorization_draft_complete_observed",
    "authorization_scope_review_complete",
    "authorization_conditions_review_complete",
    "rollback_binding_review_complete",
    "monitoring_binding_review_complete",
    "blast_radius_binding_review_complete",
    "exit_criteria_binding_review_complete",
    "operator_authorization_requirement_review_complete",
    "execution_disabled_review_complete",
    "provenance_review_complete",
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


def _validate_p111_packet(p111_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p111_packet is None:
        return ["p111_packet_missing"], None
    if not isinstance(p111_packet, dict):
        return ["p111_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p111_packet.get("artifact_type") != REQUIRED_P111_ARTIFACT_TYPE:
        reasons.append(
            f"p111_artifact_type_mismatch:{p111_packet.get('artifact_type')!r}"
        )
    if p111_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p111_lane_id_mismatch:{p111_packet.get('lane_id')!r}")
    if p111_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p111_canonical_status_mismatch:{p111_packet.get('canonical_status')!r}"
        )
    if p111_packet.get("advisory_only") is not True:
        reasons.append("p111_advisory_only_not_true")
    if p111_packet.get("projection_only") is not True:
        reasons.append("p111_projection_only_not_true")

    p111_status = p111_packet.get("status")
    p111_draft_status = p111_packet.get("canary_authorization_draft_status")
    if p111_status != "CANARY_AUTHORIZATION_DRAFT_EMITTED":
        reasons.append(f"p111_status_not_emitted:{p111_status!r}")
    if p111_draft_status not in (
        "CANARY_AUTHORIZATION_DRAFT_COMPLETE",
        "CANARY_AUTHORIZATION_DRAFT_INCOMPLETE",
    ):
        reasons.append(
            "p111_canary_authorization_draft_status_not_pass_or_incomplete:"
            f"{p111_draft_status!r}"
        )

    if p111_packet.get("recommended_next_lane") != REQUIRED_P111_RECOMMENDATION:
        reasons.append(
            "p111_recommendation_chain_mismatch:"
            f"{p111_packet.get('recommended_next_lane')!r}"
        )

    authorization_draft_complete_candidates = p111_packet.get(
        "authorization_draft_complete_candidates"
    )
    if not isinstance(authorization_draft_complete_candidates, list):
        reasons.append("p111_authorization_draft_complete_candidates_malformed")
    elif not authorization_draft_complete_candidates:
        reasons.append("p111_no_authorization_draft_complete_candidates")
    elif any(
        not isinstance(candidate, str)
        for candidate in authorization_draft_complete_candidates
    ):
        reasons.append("p111_authorization_draft_complete_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p111_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p111_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p111_{field_name}_entry_malformed")

    authority_locks = p111_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p111_authority_locks_malformed")
    else:
        for key in P111_AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p111_authority_lock_missing:{key}")

    return sorted(set(reasons)), p111_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "authorization_draft_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "authorization_draft_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p111(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p111_reports_authority_drift")

    if (
        packet.get("canary_authorization_draft_status")
        == "CANARY_AUTHORIZATION_DRAFT_REJECTED_AUTHORITY_DRIFT"
    ):
        findings.append("p111_draft_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in P111_AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p111_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_authorization_review_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_authorization_review_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_authorization_review_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "authorization_draft_complete_observed": False,
            "authorization_scope_review_complete": False,
            "authorization_conditions_review_complete": False,
            "rollback_binding_review_complete": False,
            "monitoring_binding_review_complete": False,
            "blast_radius_binding_review_complete": False,
            "exit_criteria_binding_review_complete": False,
            "operator_authorization_requirement_review_complete": False,
            "execution_disabled_review_complete": False,
            "provenance_review_complete": False,
            "authority_drift_observed": False,
            "missing_authorization_review_requirements": [
                "authorization_review_observations_missing"
            ],
            "canary_authorization_review_status": "CANARY_AUTHORIZATION_REVIEW_INCOMPLETE",
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    criteria: dict[str, bool] = {}
    for field in AUTHORIZATION_REVIEW_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_authorization_review_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in AUTHORIZATION_REVIEW_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_authorization_review_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_authorization_review_requirements.append("authority_drift_observed")
        authority_findings.append(
            f"candidate_authorization_review_authority_drift_observed:{candidate_id}"
        )
        canary_authorization_review_status = (
            "CANARY_AUTHORIZATION_REVIEW_REJECTED_AUTHORITY_DRIFT"
        )
    elif not missing_authorization_review_requirements:
        canary_authorization_review_status = "CANARY_AUTHORIZATION_REVIEW_COMPLETE"
    else:
        canary_authorization_review_status = "CANARY_AUTHORIZATION_REVIEW_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "authorization_draft_complete_observed": criteria[
            "authorization_draft_complete_observed"
        ],
        "authorization_scope_review_complete": criteria[
            "authorization_scope_review_complete"
        ],
        "authorization_conditions_review_complete": criteria[
            "authorization_conditions_review_complete"
        ],
        "rollback_binding_review_complete": criteria[
            "rollback_binding_review_complete"
        ],
        "monitoring_binding_review_complete": criteria[
            "monitoring_binding_review_complete"
        ],
        "blast_radius_binding_review_complete": criteria[
            "blast_radius_binding_review_complete"
        ],
        "exit_criteria_binding_review_complete": criteria[
            "exit_criteria_binding_review_complete"
        ],
        "operator_authorization_requirement_review_complete": criteria[
            "operator_authorization_requirement_review_complete"
        ],
        "execution_disabled_review_complete": criteria[
            "execution_disabled_review_complete"
        ],
        "provenance_review_complete": criteria["provenance_review_complete"],
        "authority_drift_observed": authority_drift_observed,
        "missing_authorization_review_requirements": sorted(
            set(missing_authorization_review_requirements)
        ),
        "canary_authorization_review_status": canary_authorization_review_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status_dict["notes"] = notes

    return status_dict, authority_findings


def _build_candidate_authorization_review_statuses(
    *,
    authorization_draft_complete_candidates: list[str],
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

    for candidate_id in authorization_draft_complete_candidates:
        observation = _get_candidate_authorization_review_observation(
            observations_packet, candidate_id
        )
        candidate_status, candidate_authority_findings = (
            _build_candidate_authorization_review_status(candidate_id, observation)
        )
        candidate_statuses.append(candidate_status)
        authority_findings.extend(candidate_authority_findings)

        missing = candidate_status["missing_authorization_review_requirements"]
        if isinstance(missing, list) and missing:
            missing_requirements[candidate_id] = list(missing)

        if (
            candidate_status["canary_authorization_review_status"]
            == "CANARY_AUTHORIZATION_REVIEW_COMPLETE"
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


def build_research_canary_authorization_review_record(
    *,
    p111_packet: dict[str, Any] | None = None,
    authorization_review_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p111 = _validate_p111_packet(p111_packet)
    candidate_lists = _extract_candidate_lists(normalized_p111)
    authority_drift_findings = _detect_authority_drift_p111(normalized_p111)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    authorization_draft_complete_candidates = candidate_lists[
        "authorization_draft_complete_candidates"
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
        ) = _build_candidate_authorization_review_statuses(
            authorization_draft_complete_candidates=authorization_draft_complete_candidates,
            observations_packet=authorization_review_observations_packet,
        )

    all_authority_drift = sorted(
        set(authority_drift_findings + observation_drift_findings)
    )

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_authorization_review_record_status = (
            "CANARY_AUTHORIZATION_REVIEW_REJECTED_AUTHORITY_DRIFT"
        )
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P111 or authorization review observations report authority drift or "
            "authority lock drift; P112 remains advisory-only and cannot proceed "
            "while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        canary_authorization_review_record_status = "CANARY_AUTHORIZATION_REVIEW_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P111 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, does not recommend P112, or has no "
            "authorization_draft_complete_candidates; P112 cannot compute."
        )
    else:
        status = "CANARY_AUTHORIZATION_REVIEW_RECORD_EMITTED"
        all_candidates_complete = (
            len(authorization_draft_complete_candidates) > 0
            and len(complete_candidates) == len(authorization_draft_complete_candidates)
            and not incomplete_candidates
        )
        if all_candidates_complete:
            canary_authorization_review_record_status = "CANARY_AUTHORIZATION_REVIEW_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete canary authorization review "
                "observations and no authority drift exists; proceed to advisory "
                "P113 final precheck record."
            )
        else:
            canary_authorization_review_record_status = (
                "CANARY_AUTHORIZATION_REVIEW_INCOMPLETE"
            )
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required canary "
                "authorization review observations; continue P112."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_canary_authorization_draft_status": (
            normalized_p111.get("status") if isinstance(normalized_p111, dict) else None
        ),
        "canary_authorization_review_record_status": (
            canary_authorization_review_record_status
        ),
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": authorization_draft_complete_candidates,
        "authorization_review_complete_candidates": complete_candidates,
        "authorization_review_incomplete_candidates": incomplete_candidates,
        "candidate_authorization_review_statuses": candidate_statuses,
        "required_authorization_review_observations": list(
            REQUIRED_AUTHORIZATION_REVIEW_OBSERVATION_FIELDS
        ),
        "missing_authorization_review_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p111_research_canary_authorization_draft",
            "mapping_method": "deterministic_canary_authorization_review_record",
            "required_authorization_review_observation_fields": list(
                REQUIRED_AUTHORIZATION_REVIEW_OBSERVATION_FIELDS
            ),
            "authorization_review_completeness_fields": list(
                AUTHORIZATION_REVIEW_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "canary_authorization_review_record_is_not_canary_authorization",
                "canary_authorization_review_record_is_not_canary_activation",
                "canary_authorization_review_record_is_not_canary_plan_execution",
                "canary_authorization_review_record_is_not_implementation_authority",
                "canary_authorization_review_record_is_not_canon_promotion",
                "canary_authorization_review_record_is_not_production_activation",
                "canary_authorization_review_record_is_not_runtime_mutation",
                "canary_authorization_review_record_is_not_scheduler_authority",
                "canary_authorization_review_record_is_not_forecast_weight_authority",
                "canary_authorization_review_record_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p113_only_when_every_analyzed_candidate_has_complete_"
                "authorization_review_observations_and_no_authority_drift"
            ),
            "p111_status": (
                normalized_p111.get("status") if isinstance(normalized_p111, dict) else None
            ),
            "p111_artifact_type": (
                normalized_p111.get("artifact_type")
                if isinstance(normalized_p111, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_canary_authorization_review_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
