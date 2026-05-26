from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P118 is advisory-only and projection-only.
# It does NOT activate or execute canary mode.
# It does NOT grant canary/runtime/rollback/termination authority.
# It does NOT mutate runtime, scheduler, baseline, forecast, or canon.
# It does NOT implement P119 runtime observation behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchControlledCanaryEnvelopeDraft.v1"
LANE_ID = "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING"
REQUIRED_P117_ARTIFACT_TYPE = "ResearchCanaryAuthorizationDenialHoldRouting.v1"
REQUIRED_P117_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT_CONTINUE"
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
)

REQUIRED_ENVELOPE_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "approval_route_observed",
    "envelope_scope_defined",
    "runtime_boundary_defined",
    "observation_surface_defined",
    "rollback_hook_defined",
    "termination_condition_defined",
    "blast_radius_limit_defined",
    "operator_supervision_required",
    "execution_disabled_confirmed",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

ENVELOPE_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "approval_route_observed",
    "envelope_scope_defined",
    "runtime_boundary_defined",
    "observation_surface_defined",
    "rollback_hook_defined",
    "termination_condition_defined",
    "blast_radius_limit_defined",
    "operator_supervision_required",
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


def _validate_p117_packet(p117_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p117_packet is None:
        return ["p117_packet_missing"], None
    if not isinstance(p117_packet, dict):
        return ["p117_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p117_packet.get("artifact_type") != REQUIRED_P117_ARTIFACT_TYPE:
        reasons.append(
            f"p117_artifact_type_mismatch:{p117_packet.get('artifact_type')!r}"
        )
    if p117_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p117_lane_id_mismatch:{p117_packet.get('lane_id')!r}")
    if p117_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p117_canonical_status_mismatch:{p117_packet.get('canonical_status')!r}"
        )
    if p117_packet.get("advisory_only") is not True:
        reasons.append("p117_advisory_only_not_true")
    if p117_packet.get("projection_only") is not True:
        reasons.append("p117_projection_only_not_true")

    if p117_packet.get("status") != "CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING_EMITTED":
        reasons.append(f"p117_status_not_emitted:{p117_packet.get('status')!r}")
    if p117_packet.get("lane_status") != "CANARY_AUTHORIZATION_ROUTE_APPROVED_FOR_ENVELOPE_DRAFT":
        reasons.append(f"p117_status_not_pass:{p117_packet.get('lane_status')!r}")

    if p117_packet.get("recommended_next_lane") != REQUIRED_P117_RECOMMENDATION:
        reasons.append(
            "p117_recommendation_chain_mismatch:"
            f"{p117_packet.get('recommended_next_lane')!r}"
        )

    analyzed_candidates = p117_packet.get("approved_for_controlled_envelope_planning_candidates")
    if not isinstance(analyzed_candidates, list):
        reasons.append("p117_approved_for_controlled_envelope_planning_candidates_malformed")
    elif not analyzed_candidates:
        reasons.append("p117_no_candidates_for_p118")
    elif any(not isinstance(candidate, str) for candidate in analyzed_candidates):
        reasons.append("p117_candidate_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p117_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p117_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p117_{field_name}_entry_malformed")

    return sorted(set(reasons)), p117_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "approved_for_controlled_envelope_planning_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "approved_for_controlled_envelope_planning_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p117(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p117_reports_authority_drift")

    if packet.get("lane_status") == "CANARY_AUTHORIZATION_ROUTE_REJECTED_AUTHORITY_DRIFT":
        findings.append("p117_lane_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"p117_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_envelope_observations")
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
            "envelope_scope_defined": False,
            "runtime_boundary_defined": False,
            "observation_surface_defined": False,
            "rollback_hook_defined": False,
            "termination_condition_defined": False,
            "blast_radius_limit_defined": False,
            "operator_supervision_required": False,
            "execution_disabled_confirmed": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["envelope_observations_missing"],
            "controlled_canary_envelope_draft_status": (
                "CONTROLLED_CANARY_ENVELOPE_DRAFT_INCOMPLETE"
            ),
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    criteria: dict[str, bool] = {}
    for field in ENVELOPE_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in ENVELOPE_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_envelope_authority_drift:{candidate_id}")

    if authority_findings:
        envelope_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        envelope_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_COMPLETE"
    else:
        envelope_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "approval_route_observed": criteria["approval_route_observed"],
        "envelope_scope_defined": criteria["envelope_scope_defined"],
        "runtime_boundary_defined": criteria["runtime_boundary_defined"],
        "observation_surface_defined": criteria["observation_surface_defined"],
        "rollback_hook_defined": criteria["rollback_hook_defined"],
        "termination_condition_defined": criteria["termination_condition_defined"],
        "blast_radius_limit_defined": criteria["blast_radius_limit_defined"],
        "operator_supervision_required": criteria["operator_supervision_required"],
        "execution_disabled_confirmed": criteria["execution_disabled_confirmed"],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "controlled_canary_envelope_draft_status": envelope_status,
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

        envelope_status = candidate_status["controlled_canary_envelope_draft_status"]
        if envelope_status == "CONTROLLED_CANARY_ENVELOPE_DRAFT_COMPLETE":
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


def build_research_controlled_canary_envelope_draft(
    *,
    p117_packet: dict[str, Any] | None = None,
    envelope_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p117 = _validate_p117_packet(p117_packet)
    candidate_lists = _extract_candidate_lists(normalized_p117)
    authority_drift_findings = _detect_authority_drift_p117(normalized_p117)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    analyzed_candidates = candidate_lists[
        "approved_for_controlled_envelope_planning_candidates"
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
        ) = _build_candidate_statuses(
            analyzed_candidates=analyzed_candidates,
            observations_packet=envelope_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P117 or envelope observations report authority drift or authority lock drift; "
            "P118 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P117 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks approved "
            "candidates, or does not recommend P118; P118 cannot compute."
        )
    else:
        status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_EMITTED"
        all_complete = (
            len(analyzed_candidates) > 0
            and len(complete_candidates) == len(analyzed_candidates)
            and not missing_requirements
        )

        if all_complete:
            lane_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete controlled-canary envelope draft "
                "observations and no authority drift; advisory planning may recommend P119."
            )
        else:
            lane_status = "CONTROLLED_CANARY_ENVELOPE_DRAFT_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates have incomplete envelope draft observations; "
                "continue P118 advisory envelope drafting."
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
            normalized_p117.get("status") if isinstance(normalized_p117, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p117.get("lane_status") if isinstance(normalized_p117, dict) else None
        ),
        "lane_status": lane_status,
        "research_controlled_canary_envelope_draft_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": analyzed_candidates,
        "envelope_draft_complete_candidates": complete_candidates,
        "envelope_draft_incomplete_candidates": incomplete_candidates,
        "candidate_statuses": candidate_statuses,
        "candidate_envelope_draft_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "missing_envelope_draft_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "required_envelope_draft_observations": list(REQUIRED_ENVELOPE_OBSERVATION_FIELDS),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p117_research_canary_authorization_denial_hold_routing",
            "mapping_method": "deterministic_controlled_canary_envelope_draft",
            "required_envelope_observation_fields": list(
                REQUIRED_ENVELOPE_OBSERVATION_FIELDS
            ),
            "envelope_completeness_fields": list(ENVELOPE_COMPLETENESS_FIELDS),
            "boundary_rules": [
                "envelope_draft_is_not_canary_activation",
                "envelope_draft_is_not_canary_execution",
                "envelope_draft_is_not_canary_authority",
                "envelope_draft_is_not_runtime_control",
                "envelope_draft_is_not_runtime_mutation",
                "envelope_draft_is_not_scheduler_mutation",
                "envelope_draft_is_not_forecast_mutation",
                "envelope_draft_is_not_canon_promotion",
                "batch_b_does_not_implement_p121",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p119_only_when_every_analyzed_candidate_has_complete_"
                "envelope_draft_observations_and_no_authority_drift"
            ),
            "p117_status": (
                normalized_p117.get("status") if isinstance(normalized_p117, dict) else None
            ),
            "p117_artifact_type": (
                normalized_p117.get("artifact_type")
                if isinstance(normalized_p117, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_controlled_canary_envelope_draft(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
