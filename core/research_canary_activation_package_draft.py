from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P122 is advisory-only and projection-only.
# It does NOT activate canary mode, authorize activation, or execute canary plans.
# It does NOT grant runtime authority/control, and does NOT mutate runtime/scheduler.
# It does NOT implement activation decision authority and does NOT implement P123.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryActivationPackageDraft.v1"
LANE_ID = "P122_RESEARCH_CANARY_ACTIVATION_PACKAGE_DRAFT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW"
REQUIRED_P121_ARTIFACT_TYPE = "ResearchCanaryOperatorGoNoGoReview.v1"
REQUIRED_P121_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P123_RESEARCH_CANARY_ACTIVATION_PACKAGE_REVIEW_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P122_RESEARCH_CANARY_ACTIVATION_PACKAGE_DRAFT_CONTINUE"

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

REQUIRED_ACTIVATION_PACKAGE_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "go_for_activation_package_planning_observed",
    "activation_scope_attached",
    "activation_conditions_attached",
    "runtime_boundary_attached",
    "observation_plan_attached",
    "rollback_plan_attached",
    "termination_plan_attached",
    "operator_activation_review_required",
    "activation_disabled_confirmed",
    "runtime_control_disabled_confirmed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

ACTIVATION_PACKAGE_DRAFT_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "go_for_activation_package_planning_observed",
    "activation_scope_attached",
    "activation_conditions_attached",
    "runtime_boundary_attached",
    "observation_plan_attached",
    "rollback_plan_attached",
    "termination_plan_attached",
    "operator_activation_review_required",
    "activation_disabled_confirmed",
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


def _validate_p121_packet(p121_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p121_packet is None:
        return ["p121_packet_missing"], None
    if not isinstance(p121_packet, dict):
        return ["p121_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p121_packet.get("artifact_type") != REQUIRED_P121_ARTIFACT_TYPE:
        reasons.append(
            f"p121_artifact_type_mismatch:{p121_packet.get('artifact_type')!r}"
        )
    if p121_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p121_lane_id_mismatch:{p121_packet.get('lane_id')!r}")
    if p121_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p121_canonical_status_mismatch:{p121_packet.get('canonical_status')!r}"
        )
    if p121_packet.get("advisory_only") is not True:
        reasons.append("p121_advisory_only_not_true")
    if p121_packet.get("projection_only") is not True:
        reasons.append("p121_projection_only_not_true")

    if p121_packet.get("status") != "CANARY_OPERATOR_GO_NO_GO_REVIEW_EMITTED":
        reasons.append(f"p121_status_not_emitted:{p121_packet.get('status')!r}")
    if (
        p121_packet.get("lane_status")
        != "CANARY_OPERATOR_GO_FOR_ACTIVATION_PACKAGE_PLANNING"
    ):
        reasons.append(f"p121_status_not_pass:{p121_packet.get('lane_status')!r}")

    if p121_packet.get("recommended_next_lane") != REQUIRED_P121_RECOMMENDATION:
        reasons.append(
            "p121_recommendation_chain_mismatch:"
            f"{p121_packet.get('recommended_next_lane')!r}"
        )

    complete_candidates = p121_packet.get("go_for_activation_package_planning_candidates")
    if not isinstance(complete_candidates, list):
        reasons.append("p121_go_for_activation_package_planning_candidates_malformed")
    elif not complete_candidates:
        reasons.append("p121_no_go_for_activation_package_planning_candidates")
    elif any(not isinstance(candidate, str) for candidate in complete_candidates):
        reasons.append("p121_go_for_activation_package_planning_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p121_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p121_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p121_{field_name}_entry_malformed")

    return sorted(set(reasons)), p121_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "go_for_activation_package_planning_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "go_for_activation_package_planning_candidates",
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

    entries = observations_packet.get("candidate_activation_package_observations")
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
            "go_for_activation_package_planning_observed": False,
            "activation_scope_attached": False,
            "activation_conditions_attached": False,
            "runtime_boundary_attached": False,
            "observation_plan_attached": False,
            "rollback_plan_attached": False,
            "termination_plan_attached": False,
            "operator_activation_review_required": False,
            "activation_disabled_confirmed": False,
            "runtime_control_disabled_confirmed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["activation_package_observations_missing"],
            "canary_activation_package_draft_status": (
                "CANARY_ACTIVATION_PACKAGE_DRAFT_INCOMPLETE"
            ),
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    criteria: dict[str, bool] = {}
    for field in ACTIVATION_PACKAGE_DRAFT_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in ACTIVATION_PACKAGE_DRAFT_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_activation_package_authority_drift:{candidate_id}")

    if authority_findings:
        candidate_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        candidate_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_COMPLETE"
    else:
        candidate_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "go_for_activation_package_planning_observed": criteria[
            "go_for_activation_package_planning_observed"
        ],
        "activation_scope_attached": criteria["activation_scope_attached"],
        "activation_conditions_attached": criteria["activation_conditions_attached"],
        "runtime_boundary_attached": criteria["runtime_boundary_attached"],
        "observation_plan_attached": criteria["observation_plan_attached"],
        "rollback_plan_attached": criteria["rollback_plan_attached"],
        "termination_plan_attached": criteria["termination_plan_attached"],
        "operator_activation_review_required": criteria[
            "operator_activation_review_required"
        ],
        "activation_disabled_confirmed": criteria["activation_disabled_confirmed"],
        "runtime_control_disabled_confirmed": criteria[
            "runtime_control_disabled_confirmed"
        ],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_activation_package_draft_status": candidate_status,
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
) -> tuple[list[dict[str, Any]], list[str], list[str], dict[str, list[str]], list[str]]:
    candidate_statuses: list[dict[str, Any]] = []
    draft_complete_candidates: list[str] = []
    draft_incomplete_candidates: list[str] = []
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

        if (
            candidate_status["canary_activation_package_draft_status"]
            == "CANARY_ACTIVATION_PACKAGE_DRAFT_COMPLETE"
        ):
            draft_complete_candidates.append(candidate_id)
        else:
            draft_incomplete_candidates.append(candidate_id)

    return (
        candidate_statuses,
        draft_complete_candidates,
        draft_incomplete_candidates,
        missing_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_activation_package_draft(
    *,
    p121_packet: dict[str, Any] | None = None,
    activation_package_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p121 = _validate_p121_packet(p121_packet)
    candidate_lists = _extract_candidate_lists(normalized_p121)
    authority_drift_findings = _detect_authority_drift(normalized_p121, source="p121")

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    complete_candidates = candidate_lists["go_for_activation_package_planning_candidates"]

    candidate_statuses: list[dict[str, Any]] = []
    draft_complete_candidates: list[str] = []
    draft_incomplete_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            draft_complete_candidates,
            draft_incomplete_candidates,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_statuses(
            complete_candidates=complete_candidates,
            observations_packet=activation_package_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P121 or activation package observations report authority drift or authority "
            "lock drift; P122 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P121 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "go_for_activation_package_planning_candidates, or does not recommend P122; "
            "P122 cannot compute."
        )
    else:
        status = "CANARY_ACTIVATION_PACKAGE_DRAFT_EMITTED"
        all_complete = (
            len(complete_candidates) > 0
            and len(draft_complete_candidates) == len(complete_candidates)
            and not draft_incomplete_candidates
        )
        if all_complete:
            lane_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete activation package observations and "
                "no authority drift; proceed to advisory P123 activation package review "
                "recording."
            )
        else:
            lane_status = "CANARY_ACTIVATION_PACKAGE_DRAFT_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required activation package "
                "observations; continue P122."
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
            normalized_p121.get("status") if isinstance(normalized_p121, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p121.get("lane_status") if isinstance(normalized_p121, dict) else None
        ),
        "lane_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": complete_candidates,
        "activation_package_draft_complete_candidates": draft_complete_candidates,
        "activation_package_draft_incomplete_candidates": draft_incomplete_candidates,
        "candidate_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p121_research_canary_operator_go_no_go_review",
            "mapping_method": "deterministic_canary_activation_package_draft",
            "required_activation_package_observation_fields": list(
                REQUIRED_ACTIVATION_PACKAGE_OBSERVATION_FIELDS
            ),
            "activation_package_draft_completeness_fields": list(
                ACTIVATION_PACKAGE_DRAFT_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "activation_package_draft_is_not_canary_activation",
                "activation_package_draft_is_not_canary_authority",
                "activation_package_draft_is_not_canary_plan_execution",
                "activation_package_draft_is_not_runtime_authority",
                "activation_package_draft_is_not_runtime_control",
                "activation_package_draft_is_not_runtime_mutation",
                "activation_package_draft_is_not_scheduler_mutation",
                "activation_package_draft_is_not_forecast_mutation",
                "activation_package_draft_is_not_canon_promotion",
                "activation_package_draft_is_not_activation_package_authority",
                "activation_package_draft_is_not_activation_package_execution",
                "activation_package_draft_is_not_activation_decision_authority",
                "batch_c_does_not_implement_p124",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p123_only_when_every_analyzed_candidate_has_complete_"
                "activation_package_observations_and_no_authority_drift"
            ),
            "p121_status": (
                normalized_p121.get("status") if isinstance(normalized_p121, dict) else None
            ),
            "p121_artifact_type": (
                normalized_p121.get("artifact_type")
                if isinstance(normalized_p121, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_activation_package_draft(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
