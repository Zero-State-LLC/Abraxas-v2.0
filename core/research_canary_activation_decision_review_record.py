from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P125 is advisory-only and projection-only.
# It does NOT activate canary mode, execute canary plans, or grant runtime authority.
# It does NOT create runtime control behavior or activation envelope behavior.
# It does NOT mutate runtime/scheduler/baseline/forecast or promote canon.
# It does NOT implement P126 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryActivationDecisionReviewRecord.v1"
LANE_ID = "P125_RESEARCH_CANARY_ACTIVATION_DECISION_REVIEW_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P124_RESEARCH_CANARY_ACTIVATION_DECISION_RECORD"
REQUIRED_P124_ARTIFACT_TYPE = "ResearchCanaryActivationDecisionRecord.v1"
REQUIRED_P124_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = (
    "P126_RESEARCH_CANARY_ACTIVATION_DENIAL_HOLD_ROUTING"
)
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P125_RESEARCH_CANARY_ACTIVATION_DECISION_REVIEW_RECORD_CONTINUE"
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
    "canary_runtime_execution",
    "canary_runtime_control",
    "rollback_execution_authority",
    "termination_execution_authority",
    "activation_package_authority",
    "activation_package_execution",
    "activation_decision_authority",
    "activation_execution_authority",
    "activation_envelope_authority",
)

REQUIRED_DECISION_REVIEW_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "activation_decision_record_observed",
    "activation_decision_review_complete",
    "denial_review_recorded",
    "hold_review_recorded",
    "repair_review_recorded",
    "approval_review_recorded",
    "activation_disabled_review_confirmed",
    "execution_disabled_review_confirmed",
    "runtime_control_disabled_review_confirmed",
    "provenance_review_complete",
    "authority_drift_observed",
    "notes",
)

REVIEW_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "activation_decision_review_complete",
    "activation_disabled_review_confirmed",
    "execution_disabled_review_confirmed",
    "runtime_control_disabled_review_confirmed",
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


def _validate_p124_packet(p124_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p124_packet is None:
        return ["p124_packet_missing"], None
    if not isinstance(p124_packet, dict):
        return ["p124_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p124_packet.get("artifact_type") != REQUIRED_P124_ARTIFACT_TYPE:
        reasons.append(
            f"p124_artifact_type_mismatch:{p124_packet.get('artifact_type')!r}"
        )
    if p124_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p124_lane_id_mismatch:{p124_packet.get('lane_id')!r}")
    if p124_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p124_canonical_status_mismatch:{p124_packet.get('canonical_status')!r}"
        )
    if p124_packet.get("advisory_only") is not True:
        reasons.append("p124_advisory_only_not_true")
    if p124_packet.get("projection_only") is not True:
        reasons.append("p124_projection_only_not_true")

    p124_status = p124_packet.get("status")
    p124_lane_status = p124_packet.get("lane_status")
    if p124_status != "CANARY_ACTIVATION_DECISION_RECORD_EMITTED":
        reasons.append(f"p124_status_not_emitted:{p124_status!r}")
    if p124_lane_status not in {
        "CANARY_ACTIVATION_DECISION_DENIED",
        "CANARY_ACTIVATION_DECISION_HELD",
        "CANARY_ACTIVATION_DECISION_REPAIR_REQUESTED",
        "CANARY_ACTIVATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING",
    }:
        reasons.append(f"p124_status_not_pass:{p124_lane_status!r}")

    if p124_packet.get("recommended_next_lane") != REQUIRED_P124_RECOMMENDATION:
        reasons.append(
            "p124_recommendation_chain_mismatch:"
            f"{p124_packet.get('recommended_next_lane')!r}"
        )

    analyzed_candidates = p124_packet.get("analyzed_candidates")
    if not isinstance(analyzed_candidates, list):
        reasons.append("p124_analyzed_candidates_malformed")
    elif not analyzed_candidates:
        reasons.append("p124_no_decisions")
    elif any(not isinstance(candidate, str) for candidate in analyzed_candidates):
        reasons.append("p124_analyzed_candidates_entry_malformed")

    candidate_statuses = p124_packet.get("candidate_statuses")
    if not isinstance(candidate_statuses, list):
        reasons.append("p124_candidate_statuses_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p124_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p124_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p124_{field_name}_entry_malformed")

    return sorted(set(reasons)), p124_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "analyzed_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "analyzed_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift(packet: dict[str, Any] | None, *, source: str) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []
    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append(f"{source}_reports_authority_drift")

    lane_status = packet.get("lane_status")
    if isinstance(lane_status, str) and lane_status.endswith("REJECTED_AUTHORITY_DRIFT"):
        findings.append(f"{source}_lane_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"{source}_authority_lock_drift:{key}")

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
        decision = entry.get("activation_decision")
        if isinstance(candidate_id, str) and isinstance(decision, str):
            mapping[candidate_id] = decision
    return mapping


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_activation_decision_review_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}

    return candidate_observation


def _review_flag_for_decision(decision: str, field_name: str) -> bool:
    if decision == "deny_activation":
        return field_name == "denial_review_recorded"
    if decision == "hold_activation":
        return field_name == "hold_review_recorded"
    if decision == "request_activation_repair":
        return field_name == "repair_review_recorded"
    if decision == "approve_for_activation_envelope_planning":
        return field_name == "approval_review_recorded"
    return False


def _build_candidate_status(
    candidate_id: str,
    decision: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "activation_decision": decision,
            "activation_decision_record_observed": "",
            "activation_decision_review_complete": False,
            "denial_review_recorded": False,
            "hold_review_recorded": False,
            "repair_review_recorded": False,
            "approval_review_recorded": False,
            "activation_disabled_review_confirmed": False,
            "execution_disabled_review_confirmed": False,
            "runtime_control_disabled_review_confirmed": False,
            "provenance_review_complete": False,
            "authority_drift_observed": False,
            "missing_requirements": ["activation_decision_review_observations_missing"],
            "canary_activation_decision_review_status": (
                "CANARY_ACTIVATION_DECISION_REVIEW_INCOMPLETE"
            ),
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    decision_observed_value = observation.get("activation_decision_record_observed")
    decision_observed = (
        decision_observed_value if isinstance(decision_observed_value, str) else ""
    )

    criteria: dict[str, bool] = {}
    for field in REVIEW_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    review_flags: dict[str, bool] = {}
    for field in (
        "denial_review_recorded",
        "hold_review_recorded",
        "repair_review_recorded",
        "approval_review_recorded",
    ):
        review_flags[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    if decision_observed != decision:
        missing_requirements.append("activation_decision_record_observed_mismatch")

    for field in REVIEW_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    for review_field, review_set in review_flags.items():
        expected = _review_flag_for_decision(decision, review_field)
        if review_set is not expected:
            if expected:
                missing_requirements.append(f"{review_field}_not_true")
            else:
                missing_requirements.append(f"{review_field}_unexpected_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(
            f"candidate_activation_decision_review_drift:{candidate_id}"
        )

    if authority_findings:
        review_status = "CANARY_ACTIVATION_DECISION_REVIEW_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        review_status = "CANARY_ACTIVATION_DECISION_REVIEW_COMPLETE"
    else:
        review_status = "CANARY_ACTIVATION_DECISION_REVIEW_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "activation_decision": decision,
        "activation_decision_record_observed": decision_observed,
        "activation_decision_review_complete": criteria[
            "activation_decision_review_complete"
        ],
        "denial_review_recorded": review_flags["denial_review_recorded"],
        "hold_review_recorded": review_flags["hold_review_recorded"],
        "repair_review_recorded": review_flags["repair_review_recorded"],
        "approval_review_recorded": review_flags["approval_review_recorded"],
        "activation_disabled_review_confirmed": criteria[
            "activation_disabled_review_confirmed"
        ],
        "execution_disabled_review_confirmed": criteria[
            "execution_disabled_review_confirmed"
        ],
        "runtime_control_disabled_review_confirmed": criteria[
            "runtime_control_disabled_review_confirmed"
        ],
        "provenance_review_complete": criteria["provenance_review_complete"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_activation_decision_review_status": review_status,
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
) -> tuple[list[dict[str, Any]], dict[str, list[str]], list[str]]:
    candidate_statuses: list[dict[str, Any]] = []
    missing_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in analyzed_candidates:
        decision = decision_map.get(candidate_id, "hold_activation")
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

    return candidate_statuses, missing_requirements, sorted(set(authority_findings))


def build_research_canary_activation_decision_review_record(
    *,
    p124_packet: dict[str, Any] | None = None,
    activation_decision_review_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p124 = _validate_p124_packet(p124_packet)
    candidate_lists = _extract_candidate_lists(normalized_p124)
    authority_drift_findings = _detect_authority_drift(normalized_p124, source="p124")

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    analyzed_candidates = candidate_lists["analyzed_candidates"]

    decision_map = _decision_map(normalized_p124)

    candidate_statuses: list[dict[str, Any]] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_statuses(
            analyzed_candidates=analyzed_candidates,
            decision_map=decision_map,
            observations_packet=activation_decision_review_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_ACTIVATION_DECISION_REVIEW_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P124 or activation decision review observations report authority drift or "
            "authority lock drift; P125 remains advisory-only and cannot proceed while "
            "drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_ACTIVATION_DECISION_REVIEW_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P124 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "activation decisions, or does not recommend P125; P125 cannot compute."
        )
    else:
        status = "CANARY_ACTIVATION_DECISION_REVIEW_RECORD_EMITTED"
        all_complete = (
            len(analyzed_candidates) > 0
            and len(candidate_statuses) == len(analyzed_candidates)
            and not missing_requirements
        )
        if all_complete:
            lane_status = "CANARY_ACTIVATION_DECISION_REVIEW_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete decision review observations and "
                "no authority drift; proceed to advisory P126 denial/hold routing."
            )
        else:
            lane_status = "CANARY_ACTIVATION_DECISION_REVIEW_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required activation decision "
                "review evidence; continue P125."
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
            normalized_p124.get("status") if isinstance(normalized_p124, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p124.get("lane_status")
            if isinstance(normalized_p124, dict)
            else None
        ),
        "lane_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": analyzed_candidates,
        "candidate_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p124_research_canary_activation_decision_record",
            "mapping_method": "deterministic_canary_activation_decision_review_record",
            "required_activation_decision_review_observation_fields": list(
                REQUIRED_DECISION_REVIEW_OBSERVATION_FIELDS
            ),
            "activation_decision_review_completeness_fields": list(
                REVIEW_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "activation_decision_review_record_is_not_activation_authority",
                "activation_decision_review_record_is_not_canary_activation",
                "activation_decision_review_record_is_not_canary_execution",
                "activation_decision_review_record_is_not_runtime_authority",
                "activation_decision_review_record_is_not_runtime_control",
                "activation_decision_review_record_is_not_runtime_mutation",
                "activation_decision_review_record_is_not_scheduler_mutation",
                "activation_decision_review_record_is_not_forecast_mutation",
                "activation_decision_review_record_is_not_canon_promotion",
                "batch_d_does_not_implement_p127",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p126_only_when_every_analyzed_candidate_has_complete_"
                "activation_decision_review_observations_and_no_authority_drift"
            ),
            "p124_status": (
                normalized_p124.get("status")
                if isinstance(normalized_p124, dict)
                else None
            ),
            "p124_artifact_type": (
                normalized_p124.get("artifact_type")
                if isinstance(normalized_p124, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_activation_decision_review_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
