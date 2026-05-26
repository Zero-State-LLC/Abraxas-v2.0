from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P116 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT create controlled canary runtime envelope behavior.
# It does NOT grant runtime envelope authority.
# It does NOT mutate runtime/scheduler/forecast or promote canon.
# It does NOT implement P117 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationDecisionRecord.v1"
LANE_ID = "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD"
REQUIRED_P115_ARTIFACT_TYPE = "ResearchCanaryAuthorizationPackageReviewRecord.v1"
REQUIRED_P115_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD_CONTINUE"

ALLOWED_DECISIONS: tuple[str, ...] = (
    "deny",
    "hold",
    "request_repair",
    "approve_for_controlled_envelope_planning",
)

FORBIDDEN_DECISIONS: tuple[str, ...] = (
    "authorize_canary",
    "activate_canary",
    "grant_canary_authority",
    "execute_canary_plan",
    "production_activate",
    "canon_promote",
    "runtime_mutate",
    "scheduler_mutate",
    "forecast_weight_import",
    "autonomous_execute",
    "operator_bypass",
    "hidden_intent_claim_authority",
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

REQUIRED_DECISION_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "decision",
    "operator_decision_observed",
    "decision_rationale_attached",
    "package_review_complete_observed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

DECISION_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "operator_decision_observed",
    "decision_rationale_attached",
    "package_review_complete_observed",
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


def _validate_p115_packet(p115_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p115_packet is None:
        return ["p115_packet_missing"], None
    if not isinstance(p115_packet, dict):
        return ["p115_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p115_packet.get("artifact_type") != REQUIRED_P115_ARTIFACT_TYPE:
        reasons.append(
            f"p115_artifact_type_mismatch:{p115_packet.get('artifact_type')!r}"
        )
    if p115_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p115_lane_id_mismatch:{p115_packet.get('lane_id')!r}")
    if p115_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p115_canonical_status_mismatch:{p115_packet.get('canonical_status')!r}"
        )
    if p115_packet.get("advisory_only") is not True:
        reasons.append("p115_advisory_only_not_true")
    if p115_packet.get("projection_only") is not True:
        reasons.append("p115_projection_only_not_true")

    p115_status = p115_packet.get("status")
    p115_lane_status = p115_packet.get("lane_status")
    if p115_status != "CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_EMITTED":
        reasons.append(f"p115_status_not_emitted:{p115_status!r}")
    if p115_lane_status != "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE":
        reasons.append(f"p115_status_not_pass:{p115_lane_status!r}")

    if p115_packet.get("recommended_next_lane") != REQUIRED_P115_RECOMMENDATION:
        reasons.append(
            "p115_recommendation_chain_mismatch:"
            f"{p115_packet.get('recommended_next_lane')!r}"
        )

    complete_candidates = p115_packet.get("package_review_complete_candidates")
    if not isinstance(complete_candidates, list):
        reasons.append("p115_package_review_complete_candidates_malformed")
    elif not complete_candidates:
        reasons.append("p115_no_package_review_complete_candidates")
    elif any(not isinstance(candidate, str) for candidate in complete_candidates):
        reasons.append("p115_package_review_complete_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p115_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p115_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p115_{field_name}_entry_malformed")

    return sorted(set(reasons)), p115_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "package_review_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "package_review_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p115(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p115_reports_authority_drift")

    if packet.get("lane_status") == "CANARY_AUTHORIZATION_PACKAGE_REVIEW_REJECTED_AUTHORITY_DRIFT":
        findings.append("p115_lane_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"p115_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_authorization_decision_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}

    return candidate_observation


def _build_candidate_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "decision": "hold",
            "operator_decision_observed": False,
            "decision_rationale_attached": False,
            "package_review_complete_observed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["authorization_decision_observations_missing"],
            "canary_authorization_decision_status": "CANARY_AUTHORIZATION_DECISION_HELD",
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")
    decision_raw = observation.get("decision")
    decision = decision_raw if isinstance(decision_raw, str) else "hold"

    criteria: dict[str, bool] = {}
    for field in DECISION_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in DECISION_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if decision in FORBIDDEN_DECISIONS:
        authority_findings.append(f"forbidden_decision:{candidate_id}:{decision}")
    elif decision not in ALLOWED_DECISIONS:
        missing_requirements.append(f"decision_not_allowed:{decision}")
        decision = "hold"

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_authorization_decision_drift:{candidate_id}")

    if authority_findings:
        candidate_status = "CANARY_AUTHORIZATION_DECISION_REJECTED_AUTHORITY_DRIFT"
    elif decision == "approve_for_controlled_envelope_planning" and not missing_requirements:
        candidate_status = "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING"
    elif decision == "request_repair":
        candidate_status = "CANARY_AUTHORIZATION_DECISION_REPAIR_REQUESTED"
    elif decision == "deny":
        candidate_status = "CANARY_AUTHORIZATION_DECISION_DENIED"
    else:
        candidate_status = "CANARY_AUTHORIZATION_DECISION_HELD"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "decision": decision,
        "operator_decision_observed": criteria["operator_decision_observed"],
        "decision_rationale_attached": criteria["decision_rationale_attached"],
        "package_review_complete_observed": criteria[
            "package_review_complete_observed"
        ],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_authorization_decision_status": candidate_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status_dict["notes"] = notes

    return status_dict, authority_findings


def _build_candidate_statuses(
    *,
    complete_candidates: list[str],
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

    for candidate_id in complete_candidates:
        observation = _get_candidate_observation(observations_packet, candidate_id)
        candidate_status, candidate_authority_findings = _build_candidate_status(
            candidate_id,
            observation,
        )
        candidate_statuses.append(candidate_status)
        authority_findings.extend(candidate_authority_findings)

        missing = candidate_status.get("missing_requirements")
        if isinstance(missing, list) and missing:
            missing_requirements[candidate_id] = list(missing)

        decision_status = candidate_status["canary_authorization_decision_status"]
        if decision_status == "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING":
            approved_candidates.append(candidate_id)
        elif decision_status == "CANARY_AUTHORIZATION_DECISION_REPAIR_REQUESTED":
            repair_requested_candidates.append(candidate_id)
        elif decision_status == "CANARY_AUTHORIZATION_DECISION_DENIED":
            denied_candidates.append(candidate_id)
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


def build_research_canary_authorization_decision_record(
    *,
    p115_packet: dict[str, Any] | None = None,
    authorization_decision_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p115 = _validate_p115_packet(p115_packet)
    candidate_lists = _extract_candidate_lists(normalized_p115)
    authority_drift_findings = _detect_authority_drift_p115(normalized_p115)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    package_review_complete_candidates = candidate_lists["package_review_complete_candidates"]

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
            complete_candidates=package_review_complete_candidates,
            observations_packet=authorization_decision_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_AUTHORIZATION_DECISION_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P115 or authorization decision observations report authority drift, "
            "forbidden decision intent, or authority lock drift; P116 remains advisory-only "
            "and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_AUTHORIZATION_DECISION_HELD"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P115 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "package_review_complete_candidates, or does not recommend P116; P116 cannot "
            "compute."
        )
    else:
        status = "CANARY_AUTHORIZATION_DECISION_RECORD_EMITTED"
        all_approved = (
            len(package_review_complete_candidates) > 0
            and len(approved_candidates) == len(package_review_complete_candidates)
            and not missing_requirements
        )
        if all_approved:
            lane_status = "CANARY_AUTHORIZATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has a valid approved decision and no authority "
                "drift exists; proceed to advisory P117 denial/hold routing."
            )
        else:
            if denied_candidates:
                lane_status = "CANARY_AUTHORIZATION_DECISION_DENIED"
            elif repair_requested_candidates:
                lane_status = "CANARY_AUTHORIZATION_DECISION_REPAIR_REQUESTED"
            else:
                lane_status = "CANARY_AUTHORIZATION_DECISION_HELD"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are denied, held, repair-requested, or "
                "missing required decision evidence; continue P116."
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
            normalized_p115.get("status") if isinstance(normalized_p115, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p115.get("lane_status") if isinstance(normalized_p115, dict) else None
        ),
        "lane_status": lane_status,
        "canary_authorization_decision_record_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": package_review_complete_candidates,
        "denied_candidates": denied_candidates,
        "held_for_review_candidates": held_for_review_candidates,
        "repair_requested_candidates": repair_requested_candidates,
        "approved_for_controlled_envelope_planning_candidates": approved_candidates,
        "candidate_statuses": candidate_statuses,
        "candidate_authorization_decision_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "missing_authorization_decision_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "required_authorization_decision_observations": list(
            REQUIRED_DECISION_OBSERVATION_FIELDS
        ),
        "allowed_decisions": list(ALLOWED_DECISIONS),
        "forbidden_decisions": list(FORBIDDEN_DECISIONS),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p115_research_canary_authorization_package_review_record",
            "mapping_method": "deterministic_canary_authorization_decision_record",
            "required_authorization_decision_observation_fields": list(
                REQUIRED_DECISION_OBSERVATION_FIELDS
            ),
            "decision_completeness_fields": list(DECISION_COMPLETENESS_FIELDS),
            "boundary_rules": [
                "authorization_decision_record_is_not_canary_authorization",
                "authorization_decision_record_is_not_canary_activation",
                "authorization_decision_record_is_not_canary_plan_execution",
                "authorization_decision_record_is_not_canary_package_execution",
                "authorization_decision_record_is_not_canary_runtime_envelope_authority",
                "authorization_decision_record_is_not_runtime_mutation",
                "authorization_decision_record_is_not_scheduler_mutation",
                "authorization_decision_record_is_not_forecast_mutation",
                "authorization_decision_record_is_not_canon_promotion",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p117_only_when_every_analyzed_candidate_has_valid_decision_"
                "record_and_no_authority_drift"
            ),
            "p115_status": (
                normalized_p115.get("status") if isinstance(normalized_p115, dict) else None
            ),
            "p115_artifact_type": (
                normalized_p115.get("artifact_type")
                if isinstance(normalized_p115, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_authorization_decision_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
