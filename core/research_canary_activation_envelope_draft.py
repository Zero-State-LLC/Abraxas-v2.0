from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P127 is advisory-only and projection-only.
# It does NOT authorize/activate/execute canary behavior or grant authority.
# It does NOT mutate runtime/scheduler/baseline/forecast state or promote canon.
# It drafts activation envelope boundaries only and may recommend P128 when complete.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryActivationEnvelopeDraft.v1"
LANE_ID = "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P126_RESEARCH_CANARY_ACTIVATION_DENIAL_HOLD_ROUTING"
REQUIRED_P126_ARTIFACT_TYPE = "ResearchCanaryActivationDenialHoldRouting.v1"
REQUIRED_P126_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = (
    "P128_RESEARCH_CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD"
)
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT_CONTINUE"
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
    "final_activation_authority",
)

REQUIRED_ACTIVATION_ENVELOPE_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "approval_route_observed",
    "activation_envelope_scope_defined",
    "activation_boundary_defined",
    "runtime_constraint_defined",
    "observation_window_defined",
    "rollback_binding_defined",
    "termination_binding_defined",
    "operator_supervision_required",
    "activation_disabled_confirmed",
    "execution_disabled_confirmed",
    "runtime_control_disabled_confirmed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

ACTIVATION_ENVELOPE_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "approval_route_observed",
    "activation_envelope_scope_defined",
    "activation_boundary_defined",
    "runtime_constraint_defined",
    "observation_window_defined",
    "rollback_binding_defined",
    "termination_binding_defined",
    "operator_supervision_required",
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


def _validate_p126_packet(p126_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p126_packet is None:
        return ["p126_packet_missing"], None
    if not isinstance(p126_packet, dict):
        return ["p126_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p126_packet.get("artifact_type") != REQUIRED_P126_ARTIFACT_TYPE:
        reasons.append(
            f"p126_artifact_type_mismatch:{p126_packet.get('artifact_type')!r}"
        )
    if p126_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p126_lane_id_mismatch:{p126_packet.get('lane_id')!r}")
    if p126_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p126_canonical_status_mismatch:{p126_packet.get('canonical_status')!r}"
        )
    if p126_packet.get("advisory_only") is not True:
        reasons.append("p126_advisory_only_not_true")
    if p126_packet.get("projection_only") is not True:
        reasons.append("p126_projection_only_not_true")

    p126_status = p126_packet.get("status")
    p126_lane_status = p126_packet.get("lane_status")
    if p126_status != "CANARY_ACTIVATION_DENIAL_HOLD_ROUTING_EMITTED":
        reasons.append(f"p126_status_not_emitted:{p126_status!r}")
    if p126_lane_status != "CANARY_ACTIVATION_ROUTE_APPROVED_FOR_ENVELOPE_DRAFT":
        reasons.append(f"p126_status_not_pass:{p126_lane_status!r}")

    if p126_packet.get("recommended_next_lane") != REQUIRED_P126_RECOMMENDATION:
        reasons.append(
            "p126_recommendation_chain_mismatch:"
            f"{p126_packet.get('recommended_next_lane')!r}"
        )

    analyzed_candidates = p126_packet.get("approved_for_activation_envelope_planning_candidates")
    if not isinstance(analyzed_candidates, list):
        reasons.append("p126_approved_for_activation_envelope_planning_candidates_malformed")
    elif not analyzed_candidates:
        reasons.append("p126_no_approved_for_activation_envelope_planning_candidates")
    elif any(not isinstance(candidate, str) for candidate in analyzed_candidates):
        reasons.append(
            "p126_approved_for_activation_envelope_planning_candidates_entry_malformed"
        )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p126_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p126_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p126_{field_name}_entry_malformed")

    return sorted(set(reasons)), p126_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "analyzed_candidates": [],
        }

    return {
        "stabilized_candidates": _normalize_string_list(packet.get("stabilized_candidates")),
        "held_candidates": _normalize_string_list(packet.get("held_candidates")),
        "repair_candidates": _normalize_string_list(packet.get("repair_candidates")),
        "rejected_candidates": _normalize_string_list(packet.get("rejected_candidates")),
        "analyzed_candidates": _normalize_string_list(
            packet.get("approved_for_activation_envelope_planning_candidates")
        ),
    }


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

    entries = observations_packet.get("candidate_activation_envelope_observations")
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
            "approval_route_observed": False,
            "activation_envelope_scope_defined": False,
            "activation_boundary_defined": False,
            "runtime_constraint_defined": False,
            "observation_window_defined": False,
            "rollback_binding_defined": False,
            "termination_binding_defined": False,
            "operator_supervision_required": False,
            "activation_disabled_confirmed": False,
            "execution_disabled_confirmed": False,
            "runtime_control_disabled_confirmed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["activation_envelope_observations_missing"],
            "canary_activation_envelope_draft_status": (
                "CANARY_ACTIVATION_ENVELOPE_DRAFT_INCOMPLETE"
            ),
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    criteria: dict[str, bool] = {}
    for field in ACTIVATION_ENVELOPE_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in ACTIVATION_ENVELOPE_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(
            f"candidate_activation_envelope_authority_drift:{candidate_id}"
        )

    if authority_findings:
        envelope_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        envelope_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_COMPLETE"
    else:
        envelope_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "approval_route_observed": criteria["approval_route_observed"],
        "activation_envelope_scope_defined": criteria[
            "activation_envelope_scope_defined"
        ],
        "activation_boundary_defined": criteria["activation_boundary_defined"],
        "runtime_constraint_defined": criteria["runtime_constraint_defined"],
        "observation_window_defined": criteria["observation_window_defined"],
        "rollback_binding_defined": criteria["rollback_binding_defined"],
        "termination_binding_defined": criteria["termination_binding_defined"],
        "operator_supervision_required": criteria["operator_supervision_required"],
        "activation_disabled_confirmed": criteria["activation_disabled_confirmed"],
        "execution_disabled_confirmed": criteria["execution_disabled_confirmed"],
        "runtime_control_disabled_confirmed": criteria[
            "runtime_control_disabled_confirmed"
        ],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_activation_envelope_draft_status": envelope_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status_dict["notes"] = notes

    return status_dict, authority_findings


def _build_candidate_statuses(
    *,
    analyzed_candidates: list[str],
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

    for candidate_id in analyzed_candidates:
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

        envelope_status = candidate_status["canary_activation_envelope_draft_status"]
        if envelope_status == "CANARY_ACTIVATION_ENVELOPE_DRAFT_COMPLETE":
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


def build_research_canary_activation_envelope_draft(
    *,
    p126_packet: dict[str, Any] | None = None,
    activation_envelope_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p126 = _validate_p126_packet(p126_packet)
    candidate_lists = _extract_candidate_lists(normalized_p126)
    authority_drift_findings = _detect_authority_drift(normalized_p126, source="p126")

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    analyzed_candidates = candidate_lists["analyzed_candidates"]

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
        ) = _build_candidate_statuses(
            analyzed_candidates=analyzed_candidates,
            observations_packet=activation_envelope_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P126 or activation envelope observations report authority drift or authority "
            "lock drift; P127 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P126 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "approved_for_activation_envelope_planning candidates, or does not "
            "recommend P127; P127 cannot compute."
        )
    else:
        status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_EMITTED"
        all_complete = (
            len(analyzed_candidates) > 0
            and len(complete_candidates) == len(analyzed_candidates)
            and not incomplete_candidates
            and not missing_requirements
        )
        if all_complete:
            lane_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete activation envelope draft "
                "observations and no authority drift; advisory flow may recommend P128 "
                "review recording."
            )
        else:
            lane_status = "CANARY_ACTIVATION_ENVELOPE_DRAFT_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates have incomplete activation envelope "
                "draft observations; continue P127 drafting."
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
            normalized_p126.get("status") if isinstance(normalized_p126, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p126.get("lane_status") if isinstance(normalized_p126, dict) else None
        ),
        "lane_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": analyzed_candidates,
        "activation_envelope_draft_complete_candidates": complete_candidates,
        "activation_envelope_draft_incomplete_candidates": incomplete_candidates,
        "candidate_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p126_research_canary_activation_denial_hold_routing",
            "mapping_method": "deterministic_canary_activation_envelope_draft",
            "required_activation_envelope_observation_fields": list(
                REQUIRED_ACTIVATION_ENVELOPE_OBSERVATION_FIELDS
            ),
            "activation_envelope_completeness_fields": list(
                ACTIVATION_ENVELOPE_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "p127_activation_envelope_draft_is_not_activation_envelope_authority",
                "p127_activation_envelope_draft_is_not_activation_authority",
                "batch_e_does_not_implement_p130",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p128_only_when_every_analyzed_candidate_has_complete_"
                "activation_envelope_draft_observations_and_no_authority_drift"
            ),
            "p126_status": (
                normalized_p126.get("status") if isinstance(normalized_p126, dict) else None
            ),
            "p126_artifact_type": (
                normalized_p126.get("artifact_type")
                if isinstance(normalized_p126, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_activation_envelope_draft(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
