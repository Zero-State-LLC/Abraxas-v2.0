from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P121 is advisory-only and projection-only.
# It does NOT activate canary mode, execute canary plans, or grant authority.
# It does NOT create runtime control or mutate runtime/scheduler/forecast/canon.
# It does NOT execute rollback/termination and does NOT implement P122 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryOperatorGoNoGoReview.v1"
LANE_ID = "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE"
REQUIRED_P120_ARTIFACT_TYPE = "ResearchCanaryRollbackTerminationGovernance.v1"
REQUIRED_P120_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P122_RESEARCH_CANARY_ACTIVATION_PACKAGE_DRAFT"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW_CONTINUE"

ALLOWED_DECISIONS: tuple[str, ...] = (
    "no_go",
    "hold",
    "repair_required",
    "go_for_activation_package_planning",
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
)

REQUIRED_GO_NO_GO_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "rollback_termination_governance_complete_observed",
    "operator_review_observed",
    "operator_decision",
    "decision_rationale_attached",
    "activation_package_planning_only_confirmed",
    "execution_disabled_confirmed",
    "runtime_control_disabled_confirmed",
    "rollback_authority_withheld_confirmed",
    "termination_authority_withheld_confirmed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

GO_NO_GO_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "rollback_termination_governance_complete_observed",
    "operator_review_observed",
    "decision_rationale_attached",
    "activation_package_planning_only_confirmed",
    "execution_disabled_confirmed",
    "runtime_control_disabled_confirmed",
    "rollback_authority_withheld_confirmed",
    "termination_authority_withheld_confirmed",
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


def _validate_p120_packet(p120_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p120_packet is None:
        return ["p120_packet_missing"], None
    if not isinstance(p120_packet, dict):
        return ["p120_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p120_packet.get("artifact_type") != REQUIRED_P120_ARTIFACT_TYPE:
        reasons.append(
            f"p120_artifact_type_mismatch:{p120_packet.get('artifact_type')!r}"
        )
    if p120_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p120_lane_id_mismatch:{p120_packet.get('lane_id')!r}")
    if p120_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p120_canonical_status_mismatch:{p120_packet.get('canonical_status')!r}"
        )
    if p120_packet.get("advisory_only") is not True:
        reasons.append("p120_advisory_only_not_true")
    if p120_packet.get("projection_only") is not True:
        reasons.append("p120_projection_only_not_true")

    if p120_packet.get("status") != "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_EMITTED":
        reasons.append(f"p120_status_not_emitted:{p120_packet.get('status')!r}")
    if (
        p120_packet.get("lane_status")
        != "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_COMPLETE"
    ):
        reasons.append(f"p120_status_not_pass:{p120_packet.get('lane_status')!r}")

    if p120_packet.get("recommended_next_lane") != REQUIRED_P120_RECOMMENDATION:
        reasons.append(
            "p120_recommendation_chain_mismatch:"
            f"{p120_packet.get('recommended_next_lane')!r}"
        )

    complete_candidates = p120_packet.get("rollback_termination_governance_complete_candidates")
    if not isinstance(complete_candidates, list):
        reasons.append("p120_rollback_termination_governance_complete_candidates_malformed")
    elif not complete_candidates:
        reasons.append("p120_no_rollback_termination_governance_complete_candidates")
    elif any(not isinstance(candidate, str) for candidate in complete_candidates):
        reasons.append(
            "p120_rollback_termination_governance_complete_candidates_entry_malformed"
        )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p120_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p120_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p120_{field_name}_entry_malformed")

    return sorted(set(reasons)), p120_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "rollback_termination_governance_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "rollback_termination_governance_complete_candidates",
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

    entries = observations_packet.get("candidate_go_no_go_observations")
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
            "rollback_termination_governance_complete_observed": False,
            "operator_review_observed": False,
            "operator_decision": "hold",
            "decision_rationale_attached": False,
            "activation_package_planning_only_confirmed": False,
            "execution_disabled_confirmed": False,
            "runtime_control_disabled_confirmed": False,
            "rollback_authority_withheld_confirmed": False,
            "termination_authority_withheld_confirmed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["go_no_go_observations_missing"],
            "canary_operator_go_no_go_status": "CANARY_OPERATOR_HOLD",
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")
    decision_raw = observation.get("operator_decision")
    decision = decision_raw if isinstance(decision_raw, str) else "hold"

    criteria: dict[str, bool] = {}
    for field in GO_NO_GO_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in GO_NO_GO_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if decision in FORBIDDEN_DECISIONS:
        authority_findings.append(f"forbidden_decision:{candidate_id}:{decision}")
    elif decision not in ALLOWED_DECISIONS:
        missing_requirements.append(f"operator_decision_not_allowed:{decision}")
        decision = "hold"

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_go_no_go_authority_drift:{candidate_id}")

    if authority_findings:
        candidate_status = "CANARY_OPERATOR_GO_NO_GO_REJECTED_AUTHORITY_DRIFT"
    elif decision == "go_for_activation_package_planning" and not missing_requirements:
        candidate_status = "CANARY_OPERATOR_GO_FOR_ACTIVATION_PACKAGE_PLANNING"
    elif decision == "repair_required":
        candidate_status = "CANARY_OPERATOR_REPAIR_REQUIRED"
    elif decision == "no_go":
        candidate_status = "CANARY_OPERATOR_NO_GO"
    else:
        candidate_status = "CANARY_OPERATOR_HOLD"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "rollback_termination_governance_complete_observed": criteria[
            "rollback_termination_governance_complete_observed"
        ],
        "operator_review_observed": criteria["operator_review_observed"],
        "operator_decision": decision,
        "decision_rationale_attached": criteria["decision_rationale_attached"],
        "activation_package_planning_only_confirmed": criteria[
            "activation_package_planning_only_confirmed"
        ],
        "execution_disabled_confirmed": criteria["execution_disabled_confirmed"],
        "runtime_control_disabled_confirmed": criteria[
            "runtime_control_disabled_confirmed"
        ],
        "rollback_authority_withheld_confirmed": criteria[
            "rollback_authority_withheld_confirmed"
        ],
        "termination_authority_withheld_confirmed": criteria[
            "termination_authority_withheld_confirmed"
        ],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_operator_go_no_go_status": candidate_status,
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
    no_go_candidates: list[str] = []
    held_for_review_candidates: list[str] = []
    repair_required_candidates: list[str] = []
    go_for_planning_candidates: list[str] = []
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

        decision_status = candidate_status["canary_operator_go_no_go_status"]
        if decision_status == "CANARY_OPERATOR_GO_FOR_ACTIVATION_PACKAGE_PLANNING":
            go_for_planning_candidates.append(candidate_id)
        elif decision_status == "CANARY_OPERATOR_REPAIR_REQUIRED":
            repair_required_candidates.append(candidate_id)
        elif decision_status == "CANARY_OPERATOR_NO_GO":
            no_go_candidates.append(candidate_id)
        else:
            held_for_review_candidates.append(candidate_id)

    return (
        candidate_statuses,
        no_go_candidates,
        held_for_review_candidates,
        repair_required_candidates,
        go_for_planning_candidates,
        missing_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_operator_go_no_go_review(
    *,
    p120_packet: dict[str, Any] | None = None,
    go_no_go_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p120 = _validate_p120_packet(p120_packet)
    candidate_lists = _extract_candidate_lists(normalized_p120)
    authority_drift_findings = _detect_authority_drift(normalized_p120, source="p120")

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    complete_candidates = candidate_lists["rollback_termination_governance_complete_candidates"]

    candidate_statuses: list[dict[str, Any]] = []
    no_go_candidates: list[str] = []
    held_for_review_candidates: list[str] = []
    repair_required_candidates: list[str] = []
    go_for_planning_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            no_go_candidates,
            held_for_review_candidates,
            repair_required_candidates,
            go_for_planning_candidates,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_statuses(
            complete_candidates=complete_candidates,
            observations_packet=go_no_go_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_OPERATOR_GO_NO_GO_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P120 or operator go/no-go observations report authority drift, forbidden "
            "decision intent, or authority lock drift; P121 remains advisory-only and "
            "cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_OPERATOR_GO_NO_GO_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P120 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "rollback_termination_governance_complete_candidates, or does not recommend "
            "P121; P121 cannot compute."
        )
    else:
        status = "CANARY_OPERATOR_GO_NO_GO_REVIEW_EMITTED"
        all_go = (
            len(complete_candidates) > 0
            and len(go_for_planning_candidates) == len(complete_candidates)
            and not missing_requirements
        )
        if all_go:
            lane_status = "CANARY_OPERATOR_GO_FOR_ACTIVATION_PACKAGE_PLANNING"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate is go_for_activation_package_planning with "
                "complete review observations and no authority drift; proceed to advisory "
                "P122 activation package drafting."
            )
        else:
            if no_go_candidates:
                lane_status = "CANARY_OPERATOR_NO_GO"
            elif repair_required_candidates:
                lane_status = "CANARY_OPERATOR_REPAIR_REQUIRED"
            else:
                lane_status = "CANARY_OPERATOR_HOLD"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are no_go, hold, repair_required, or "
                "missing required operator review evidence; continue P121."
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
            normalized_p120.get("status") if isinstance(normalized_p120, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p120.get("lane_status") if isinstance(normalized_p120, dict) else None
        ),
        "lane_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": complete_candidates,
        "no_go_candidates": no_go_candidates,
        "held_for_review_candidates": held_for_review_candidates,
        "repair_required_candidates": repair_required_candidates,
        "go_for_activation_package_planning_candidates": go_for_planning_candidates,
        "candidate_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p120_research_canary_rollback_termination_governance",
            "mapping_method": "deterministic_canary_operator_go_no_go_review",
            "required_go_no_go_observation_fields": list(
                REQUIRED_GO_NO_GO_OBSERVATION_FIELDS
            ),
            "go_no_go_completeness_fields": list(GO_NO_GO_COMPLETENESS_FIELDS),
            "boundary_rules": [
                "operator_go_no_go_review_is_not_canary_activation",
                "operator_go_no_go_review_is_not_canary_plan_execution",
                "operator_go_no_go_review_is_not_canary_authority_grant",
                "operator_go_no_go_review_is_not_runtime_authority_grant",
                "operator_go_no_go_review_is_not_runtime_control",
                "operator_go_no_go_review_is_not_runtime_mutation",
                "operator_go_no_go_review_is_not_scheduler_mutation",
                "operator_go_no_go_review_is_not_forecast_mutation",
                "operator_go_no_go_review_is_not_canon_promotion",
                "operator_go_no_go_review_is_not_rollback_execution",
                "operator_go_no_go_review_is_not_termination_execution",
                "batch_c_does_not_implement_p124",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p122_only_when_every_analyzed_candidate_is_"
                "go_for_activation_package_planning_with_complete_observations_"
                "and_no_authority_drift"
            ),
            "p120_status": (
                normalized_p120.get("status") if isinstance(normalized_p120, dict) else None
            ),
            "p120_artifact_type": (
                normalized_p120.get("artifact_type")
                if isinstance(normalized_p120, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_operator_go_no_go_review(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
