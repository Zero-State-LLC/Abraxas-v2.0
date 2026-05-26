from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P124 is advisory-only and projection-only.
# It does NOT activate canary mode, execute canary plans, or grant runtime authority.
# It does NOT create runtime control behavior or activation envelope behavior.
# It does NOT mutate runtime/scheduler/baseline/forecast or promote canon.
# It does NOT implement P125 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryActivationDecisionRecord.v1"
LANE_ID = "P124_RESEARCH_CANARY_ACTIVATION_DECISION_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P123_RESEARCH_CANARY_ACTIVATION_PACKAGE_REVIEW_RECORD"
REQUIRED_P123_ARTIFACT_TYPE = "ResearchCanaryActivationPackageReviewRecord.v1"
REQUIRED_P123_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = (
    "P125_RESEARCH_CANARY_ACTIVATION_DECISION_REVIEW_RECORD"
)
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P124_RESEARCH_CANARY_ACTIVATION_DECISION_RECORD_CONTINUE"
)

ALLOWED_DECISIONS: tuple[str, ...] = (
    "deny_activation",
    "hold_activation",
    "request_activation_repair",
    "approve_for_activation_envelope_planning",
)

FORBIDDEN_DECISIONS: tuple[str, ...] = (
    "activate_canary",
    "execute_canary_plan",
    "grant_canary_authority",
    "grant_runtime_authority",
    "enable_runtime_control",
    "execute_rollback",
    "execute_termination",
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

REQUIRED_ACTIVATION_DECISION_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "activation_package_review_complete_observed",
    "activation_decision_observed",
    "activation_decision",
    "decision_rationale_attached",
    "activation_envelope_planning_only_confirmed",
    "activation_disabled_confirmed",
    "execution_disabled_confirmed",
    "runtime_control_disabled_confirmed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

ACTIVATION_DECISION_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "activation_package_review_complete_observed",
    "activation_decision_observed",
    "decision_rationale_attached",
    "activation_envelope_planning_only_confirmed",
    "activation_disabled_confirmed",
    "execution_disabled_confirmed",
    "runtime_control_disabled_confirmed",
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


def _validate_p123_packet(p123_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p123_packet is None:
        return ["p123_packet_missing"], None
    if not isinstance(p123_packet, dict):
        return ["p123_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p123_packet.get("artifact_type") != REQUIRED_P123_ARTIFACT_TYPE:
        reasons.append(
            f"p123_artifact_type_mismatch:{p123_packet.get('artifact_type')!r}"
        )
    if p123_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p123_lane_id_mismatch:{p123_packet.get('lane_id')!r}")
    if p123_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p123_canonical_status_mismatch:{p123_packet.get('canonical_status')!r}"
        )
    if p123_packet.get("advisory_only") is not True:
        reasons.append("p123_advisory_only_not_true")
    if p123_packet.get("projection_only") is not True:
        reasons.append("p123_projection_only_not_true")

    if p123_packet.get("status") != "CANARY_ACTIVATION_PACKAGE_REVIEW_RECORD_EMITTED":
        reasons.append(f"p123_status_not_emitted:{p123_packet.get('status')!r}")
    if p123_packet.get("lane_status") != "CANARY_ACTIVATION_PACKAGE_REVIEW_COMPLETE":
        reasons.append(f"p123_status_not_pass:{p123_packet.get('lane_status')!r}")

    if p123_packet.get("recommended_next_lane") != REQUIRED_P123_RECOMMENDATION:
        reasons.append(
            "p123_recommendation_chain_mismatch:"
            f"{p123_packet.get('recommended_next_lane')!r}"
        )

    complete_candidates = p123_packet.get("activation_package_review_complete_candidates")
    if not isinstance(complete_candidates, list):
        reasons.append("p123_activation_package_review_complete_candidates_malformed")
    elif not complete_candidates:
        reasons.append("p123_no_activation_package_review_complete_candidates")
    elif any(not isinstance(candidate, str) for candidate in complete_candidates):
        reasons.append(
            "p123_activation_package_review_complete_candidates_entry_malformed"
        )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p123_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p123_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p123_{field_name}_entry_malformed")

    return sorted(set(reasons)), p123_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "activation_package_review_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "activation_package_review_complete_candidates",
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


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_activation_decision_observations")
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
            "activation_decision": "hold_activation",
            "activation_package_review_complete_observed": False,
            "activation_decision_observed": False,
            "decision_rationale_attached": False,
            "activation_envelope_planning_only_confirmed": False,
            "activation_disabled_confirmed": False,
            "execution_disabled_confirmed": False,
            "runtime_control_disabled_confirmed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["activation_decision_observations_missing"],
            "canary_activation_decision_status": "CANARY_ACTIVATION_DECISION_INCOMPLETE",
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")
    decision_raw = observation.get("activation_decision")
    decision = decision_raw if isinstance(decision_raw, str) else "hold_activation"

    criteria: dict[str, bool] = {}
    for field in ACTIVATION_DECISION_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in ACTIVATION_DECISION_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if decision in FORBIDDEN_DECISIONS:
        authority_findings.append(f"forbidden_activation_decision:{candidate_id}:{decision}")
    elif decision not in ALLOWED_DECISIONS:
        missing_requirements.append(f"activation_decision_not_allowed:{decision}")
        decision = "hold_activation"

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_activation_decision_drift:{candidate_id}")

    if authority_findings:
        candidate_status = "CANARY_ACTIVATION_DECISION_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements and decision == "approve_for_activation_envelope_planning":
        candidate_status = "CANARY_ACTIVATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING"
    elif not missing_requirements and decision == "request_activation_repair":
        candidate_status = "CANARY_ACTIVATION_DECISION_REPAIR_REQUESTED"
    elif not missing_requirements and decision == "deny_activation":
        candidate_status = "CANARY_ACTIVATION_DECISION_DENIED"
    elif not missing_requirements:
        candidate_status = "CANARY_ACTIVATION_DECISION_HELD"
    else:
        candidate_status = "CANARY_ACTIVATION_DECISION_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "activation_decision": decision,
        "activation_package_review_complete_observed": criteria[
            "activation_package_review_complete_observed"
        ],
        "activation_decision_observed": criteria["activation_decision_observed"],
        "decision_rationale_attached": criteria["decision_rationale_attached"],
        "activation_envelope_planning_only_confirmed": criteria[
            "activation_envelope_planning_only_confirmed"
        ],
        "activation_disabled_confirmed": criteria["activation_disabled_confirmed"],
        "execution_disabled_confirmed": criteria["execution_disabled_confirmed"],
        "runtime_control_disabled_confirmed": criteria[
            "runtime_control_disabled_confirmed"
        ],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_activation_decision_status": candidate_status,
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
    held_candidates: list[str] = []
    repair_candidates: list[str] = []
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

        decision_status = candidate_status["canary_activation_decision_status"]
        if decision_status == "CANARY_ACTIVATION_DECISION_DENIED":
            denied_candidates.append(candidate_id)
        elif decision_status == "CANARY_ACTIVATION_DECISION_HELD":
            held_candidates.append(candidate_id)
        elif decision_status == "CANARY_ACTIVATION_DECISION_REPAIR_REQUESTED":
            repair_candidates.append(candidate_id)
        elif (
            decision_status
            == "CANARY_ACTIVATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING"
        ):
            approved_candidates.append(candidate_id)

    return (
        candidate_statuses,
        denied_candidates,
        held_candidates,
        repair_candidates,
        approved_candidates,
        missing_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_activation_decision_record(
    *,
    p123_packet: dict[str, Any] | None = None,
    activation_decision_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p123 = _validate_p123_packet(p123_packet)
    candidate_lists = _extract_candidate_lists(normalized_p123)
    authority_drift_findings = _detect_authority_drift(normalized_p123, source="p123")

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    complete_candidates = candidate_lists["activation_package_review_complete_candidates"]

    candidate_statuses: list[dict[str, Any]] = []
    activation_denied_candidates: list[str] = []
    activation_held_candidates: list[str] = []
    activation_repair_requested_candidates: list[str] = []
    approved_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            activation_denied_candidates,
            activation_held_candidates,
            activation_repair_requested_candidates,
            approved_candidates,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_statuses(
            complete_candidates=complete_candidates,
            observations_packet=activation_decision_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_ACTIVATION_DECISION_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P123 or activation decision observations report authority drift, forbidden "
            "decision intent, or authority lock drift; P124 remains advisory-only and "
            "cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_ACTIVATION_DECISION_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P123 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "activation_package_review_complete_candidates, or does not recommend P124; "
            "P124 cannot compute."
        )
    else:
        status = "CANARY_ACTIVATION_DECISION_RECORD_EMITTED"
        all_valid = (
            len(complete_candidates) > 0
            and len(candidate_statuses) == len(complete_candidates)
            and not missing_requirements
        )
        if all_valid:
            if activation_denied_candidates:
                lane_status = "CANARY_ACTIVATION_DECISION_DENIED"
            elif activation_held_candidates:
                lane_status = "CANARY_ACTIVATION_DECISION_HELD"
            elif activation_repair_requested_candidates:
                lane_status = "CANARY_ACTIVATION_DECISION_REPAIR_REQUESTED"
            else:
                lane_status = "CANARY_ACTIVATION_DECISION_APPROVED_FOR_ENVELOPE_PLANNING"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has a valid activation decision observation and "
                "no authority drift; proceed to advisory P125 activation decision review "
                "recording."
            )
        else:
            lane_status = "CANARY_ACTIVATION_DECISION_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required activation decision "
                "evidence; continue P124."
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
            normalized_p123.get("status") if isinstance(normalized_p123, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p123.get("lane_status")
            if isinstance(normalized_p123, dict)
            else None
        ),
        "lane_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": complete_candidates,
        "activation_denied_candidates": activation_denied_candidates,
        "activation_held_candidates": activation_held_candidates,
        "activation_repair_requested_candidates": activation_repair_requested_candidates,
        "approved_for_activation_envelope_planning_candidates": approved_candidates,
        "candidate_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p123_research_canary_activation_package_review_record",
            "mapping_method": "deterministic_canary_activation_decision_record",
            "required_activation_decision_observation_fields": list(
                REQUIRED_ACTIVATION_DECISION_OBSERVATION_FIELDS
            ),
            "activation_decision_completeness_fields": list(
                ACTIVATION_DECISION_COMPLETENESS_FIELDS
            ),
            "allowed_activation_decisions": list(ALLOWED_DECISIONS),
            "forbidden_activation_decisions": list(FORBIDDEN_DECISIONS),
            "boundary_rules": [
                "activation_decision_record_is_not_activation_authority",
                "activation_decision_record_is_not_canary_activation",
                "activation_decision_record_is_not_canary_execution",
                "activation_decision_record_is_not_runtime_authority",
                "activation_decision_record_is_not_runtime_control",
                "activation_decision_record_is_not_runtime_mutation",
                "activation_decision_record_is_not_scheduler_mutation",
                "activation_decision_record_is_not_forecast_mutation",
                "activation_decision_record_is_not_canon_promotion",
                "batch_d_does_not_implement_p127",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p125_only_when_every_analyzed_candidate_has_valid_activation_"
                "decision_observation_and_no_authority_drift"
            ),
            "p123_status": (
                normalized_p123.get("status")
                if isinstance(normalized_p123, dict)
                else None
            ),
            "p123_artifact_type": (
                normalized_p123.get("artifact_type")
                if isinstance(normalized_p123, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_activation_decision_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
