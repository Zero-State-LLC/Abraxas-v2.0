from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P117 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT create controlled canary runtime envelope behavior.
# It does NOT grant canary runtime envelope authority.
# It does NOT implement P118 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationDenialHoldRouting.v1"
LANE_ID = "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD"
REQUIRED_P116_ARTIFACT_TYPE = "ResearchCanaryAuthorizationDecisionRecord.v1"
REQUIRED_P116_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_CONTINUE"
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
    "canary_package_authority",
    "canary_package_execution",
    "canary_runtime_envelope_authority",
)

REQUIRED_ROUTING_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "authorization_decision_observed",
    "denial_route_recorded",
    "hold_route_recorded",
    "repair_route_recorded",
    "approval_route_recorded",
    "operator_routing_review_observed",
    "provenance_bundle_attached",
    "runtime_envelope_disabled_confirmed",
    "authority_drift_observed",
    "notes",
)

ROUTING_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "operator_routing_review_observed",
    "provenance_bundle_attached",
    "runtime_envelope_disabled_confirmed",
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


def _validate_p116_packet(p116_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p116_packet is None:
        return ["p116_packet_missing"], None
    if not isinstance(p116_packet, dict):
        return ["p116_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p116_packet.get("artifact_type") != REQUIRED_P116_ARTIFACT_TYPE:
        reasons.append(
            f"p116_artifact_type_mismatch:{p116_packet.get('artifact_type')!r}"
        )
    if p116_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p116_lane_id_mismatch:{p116_packet.get('lane_id')!r}")
    if p116_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p116_canonical_status_mismatch:{p116_packet.get('canonical_status')!r}"
        )
    if p116_packet.get("advisory_only") is not True:
        reasons.append("p116_advisory_only_not_true")
    if p116_packet.get("projection_only") is not True:
        reasons.append("p116_projection_only_not_true")

    p116_status = p116_packet.get("status")
    p116_lane_status = p116_packet.get("lane_status")
    if p116_status != "CANARY_AUTHORIZATION_DECISION_RECORD_EMITTED":
        reasons.append(f"p116_status_not_emitted:{p116_status!r}")
    if p116_lane_status not in {
        "CANARY_AUTHORIZATION_DECISION_DENIED",
        "CANARY_AUTHORIZATION_DECISION_HELD",
        "CANARY_AUTHORIZATION_DECISION_REPAIR_REQUESTED",
        "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING",
    }:
        reasons.append(f"p116_status_not_pass:{p116_lane_status!r}")

    if p116_packet.get("recommended_next_lane") != REQUIRED_P116_RECOMMENDATION:
        reasons.append(
            "p116_recommendation_chain_mismatch:"
            f"{p116_packet.get('recommended_next_lane')!r}"
        )

    analyzed_candidates = p116_packet.get("analyzed_candidates")
    if not isinstance(analyzed_candidates, list):
        reasons.append("p116_analyzed_candidates_malformed")
    elif not analyzed_candidates:
        reasons.append("p116_no_decisions")
    elif any(not isinstance(candidate, str) for candidate in analyzed_candidates):
        reasons.append("p116_analyzed_candidates_entry_malformed")

    candidate_statuses = p116_packet.get("candidate_statuses")
    if not isinstance(candidate_statuses, list):
        reasons.append("p116_candidate_statuses_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "denied_candidates",
        "held_for_review_candidates",
        "repair_requested_candidates",
        "approved_for_controlled_envelope_planning_candidates",
    ):
        value = p116_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p116_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p116_{field_name}_entry_malformed")

    return sorted(set(reasons)), p116_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "denied_candidates": [],
            "held_for_review_candidates": [],
            "repair_requested_candidates": [],
            "approved_for_controlled_envelope_planning_candidates": [],
            "analyzed_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "denied_candidates",
        "held_for_review_candidates",
        "repair_requested_candidates",
        "approved_for_controlled_envelope_planning_candidates",
        "analyzed_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p116(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p116_reports_authority_drift")

    if packet.get("lane_status") == "CANARY_AUTHORIZATION_DECISION_REJECTED_AUTHORITY_DRIFT":
        findings.append("p116_lane_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"p116_authority_lock_drift:{key}")

    return sorted(set(findings))


def _decision_map(packet: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(packet, dict):
        return {}

    statuses = packet.get("candidate_statuses")
    if not isinstance(statuses, list):
        return {}

    mapping: dict[str, str] = {}
    for entry in statuses:
        if not isinstance(entry, dict):
            continue
        candidate_id = entry.get("candidate_id")
        decision = entry.get("decision")
        if isinstance(candidate_id, str) and isinstance(decision, str):
            mapping[candidate_id] = decision
    return mapping


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_routing_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}

    return candidate_observation


def _route_flag_for_decision(decision: str, field_name: str) -> bool:
    if decision == "deny":
        return field_name == "denial_route_recorded"
    if decision == "hold":
        return field_name == "hold_route_recorded"
    if decision == "request_repair":
        return field_name == "repair_route_recorded"
    if decision == "approve_for_controlled_envelope_planning":
        return field_name == "approval_route_recorded"
    return False


def _build_candidate_status(
    candidate_id: str,
    decision: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "authorization_decision_observed": "",
            "denial_route_recorded": False,
            "hold_route_recorded": False,
            "repair_route_recorded": False,
            "approval_route_recorded": False,
            "operator_routing_review_observed": False,
            "provenance_bundle_attached": False,
            "runtime_envelope_disabled_confirmed": False,
            "authority_drift_observed": False,
            "missing_requirements": ["routing_observations_missing"],
            "canary_authorization_route_status": "CANARY_AUTHORIZATION_ROUTE_INCOMPLETE",
            "decision": decision,
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    decision_observed_value = observation.get("authorization_decision_observed")
    decision_observed = (
        decision_observed_value if isinstance(decision_observed_value, str) else ""
    )

    criteria: dict[str, bool] = {}
    for field in ROUTING_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    route_flags: dict[str, bool] = {}
    for field in (
        "denial_route_recorded",
        "hold_route_recorded",
        "repair_route_recorded",
        "approval_route_recorded",
    ):
        route_flags[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    if decision_observed != decision:
        missing_requirements.append("authorization_decision_observed_mismatch")

    for field in ROUTING_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    for route_field, route_set in route_flags.items():
        expected = _route_flag_for_decision(decision, route_field)
        if route_set is not expected:
            if expected:
                missing_requirements.append(f"{route_field}_not_true")
            else:
                missing_requirements.append(f"{route_field}_unexpected_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_routing_authority_drift:{candidate_id}")

    if authority_findings:
        route_status = "CANARY_AUTHORIZATION_ROUTE_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements and decision == "deny":
        route_status = "CANARY_AUTHORIZATION_ROUTE_DENIED"
    elif not missing_requirements and decision == "hold":
        route_status = "CANARY_AUTHORIZATION_ROUTE_HELD"
    elif not missing_requirements and decision == "request_repair":
        route_status = "CANARY_AUTHORIZATION_ROUTE_REPAIR_REQUESTED"
    elif (
        not missing_requirements
        and decision == "approve_for_controlled_envelope_planning"
    ):
        route_status = "CANARY_AUTHORIZATION_ROUTE_APPROVED_FOR_ENVELOPE_DRAFT"
    else:
        route_status = "CANARY_AUTHORIZATION_ROUTE_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "decision": decision,
        "authorization_decision_observed": decision_observed,
        "denial_route_recorded": route_flags["denial_route_recorded"],
        "hold_route_recorded": route_flags["hold_route_recorded"],
        "repair_route_recorded": route_flags["repair_route_recorded"],
        "approval_route_recorded": route_flags["approval_route_recorded"],
        "operator_routing_review_observed": criteria[
            "operator_routing_review_observed"
        ],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "runtime_envelope_disabled_confirmed": criteria[
            "runtime_envelope_disabled_confirmed"
        ],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_authorization_route_status": route_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status_dict["notes"] = notes

    return status_dict, authority_findings


def _build_candidate_statuses(
    *,
    analyzed_candidates: list[str],
    decision_map: dict[str, str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_statuses: list[dict[str, Any]] = []
    denied_candidates: list[str] = []
    held_for_review_candidates: list[str] = []
    repair_requested_candidates: list[str] = []
    approved_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in analyzed_candidates:
        decision = decision_map.get(candidate_id, "hold")
        observation = _get_candidate_observation(observations_packet, candidate_id)
        candidate_status, candidate_authority_findings = _build_candidate_status(
            candidate_id,
            decision,
            observation,
        )
        candidate_statuses.append(candidate_status)
        authority_findings.extend(candidate_authority_findings)

        missing = candidate_status.get("missing_requirements")
        if isinstance(missing, list) and missing:
            missing_requirements[candidate_id] = list(missing)

        route_status = candidate_status["canary_authorization_route_status"]
        if route_status == "CANARY_AUTHORIZATION_ROUTE_DENIED":
            denied_candidates.append(candidate_id)
        elif route_status == "CANARY_AUTHORIZATION_ROUTE_HELD":
            held_for_review_candidates.append(candidate_id)
        elif route_status == "CANARY_AUTHORIZATION_ROUTE_REPAIR_REQUESTED":
            repair_requested_candidates.append(candidate_id)
        elif route_status == "CANARY_AUTHORIZATION_ROUTE_APPROVED_FOR_ENVELOPE_DRAFT":
            approved_candidates.append(candidate_id)
        else:
            held_for_review_candidates.append(candidate_id)

    return (
        candidate_statuses,
        denied_candidates,
        held_for_review_candidates,
        repair_requested_candidates,
        approved_candidates,
        missing_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_authorization_denial_hold_routing(
    *,
    p116_packet: dict[str, Any] | None = None,
    routing_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p116 = _validate_p116_packet(p116_packet)
    candidate_lists = _extract_candidate_lists(normalized_p116)
    authority_drift_findings = _detect_authority_drift_p116(normalized_p116)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    analyzed_candidates = candidate_lists["analyzed_candidates"]

    decision_map = _decision_map(normalized_p116)

    candidate_statuses: list[dict[str, Any]] = []
    denied_candidates: list[str] = []
    held_for_review_candidates: list[str] = []
    repair_requested_candidates: list[str] = []
    approved_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            denied_candidates,
            held_for_review_candidates,
            repair_requested_candidates,
            approved_candidates,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_statuses(
            analyzed_candidates=analyzed_candidates,
            decision_map=decision_map,
            observations_packet=routing_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_AUTHORIZATION_ROUTE_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P116 or routing observations report authority drift or authority lock drift; "
            "P117 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_AUTHORIZATION_ROUTE_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P116 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks decision "
            "candidates, or does not recommend P117; P117 cannot compute."
        )
    else:
        status = "CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_EMITTED"
        all_approved = (
            len(analyzed_candidates) > 0
            and len(approved_candidates) == len(analyzed_candidates)
            and not denied_candidates
            and not repair_requested_candidates
            and not missing_requirements
        )

        if all_approved:
            lane_status = "CANARY_AUTHORIZATION_ROUTE_APPROVED_FOR_ENVELOPE_DRAFT"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate is approved_for_controlled_envelope_planning with "
                "complete routing evidence and no authority drift; advisory routing may "
                "recommend P118 envelope draft planning."
            )
        else:
            if denied_candidates:
                lane_status = "CANARY_AUTHORIZATION_ROUTE_DENIED"
            elif repair_requested_candidates:
                lane_status = "CANARY_AUTHORIZATION_ROUTE_REPAIR_REQUESTED"
            elif held_for_review_candidates:
                lane_status = "CANARY_AUTHORIZATION_ROUTE_HELD"
            else:
                lane_status = "CANARY_AUTHORIZATION_ROUTE_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates route to deny/hold/repair or have incomplete "
                "routing evidence; continue P117 routing."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_status": (
            normalized_p116.get("status") if isinstance(normalized_p116, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p116.get("lane_status") if isinstance(normalized_p116, dict) else None
        ),
        "lane_status": lane_status,
        "canary_authorization_denial_hold_routing_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": analyzed_candidates,
        "denied_candidates": denied_candidates,
        "held_for_review_candidates": held_for_review_candidates,
        "repair_requested_candidates": repair_requested_candidates,
        "approved_for_controlled_envelope_planning_candidates": approved_candidates,
        "candidate_statuses": candidate_statuses,
        "candidate_routing_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "missing_routing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "required_routing_observations": list(REQUIRED_ROUTING_OBSERVATION_FIELDS),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p116_research_canary_authorization_decision_record",
            "mapping_method": "deterministic_canary_authorization_denial_hold_routing",
            "required_routing_observation_fields": list(
                REQUIRED_ROUTING_OBSERVATION_FIELDS
            ),
            "routing_completeness_fields": list(ROUTING_COMPLETENESS_FIELDS),
            "boundary_rules": [
                "routing_is_not_canary_authorization",
                "routing_is_not_canary_activation",
                "routing_is_not_canary_plan_execution",
                "routing_is_not_canary_package_execution",
                "routing_is_not_canary_runtime_envelope_authority",
                "routing_is_not_runtime_mutation",
                "routing_is_not_scheduler_mutation",
                "routing_is_not_forecast_mutation",
                "routing_is_not_canon_promotion",
                "batch_a_does_not_implement_p118_runtime_behavior",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p118_only_when_every_analyzed_candidate_is_"
                "approved_for_controlled_envelope_planning_with_complete_routing_"
                "evidence_and_no_authority_drift"
            ),
            "p116_status": (
                normalized_p116.get("status") if isinstance(normalized_p116, dict) else None
            ),
            "p116_artifact_type": (
                normalized_p116.get("artifact_type")
                if isinstance(normalized_p116, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_authorization_denial_hold_routing(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
