from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P115 is advisory-only and projection-only.
# It does NOT authorize canary mode.
# It does NOT activate canary mode.
# It does NOT grant canary authority.
# It does NOT execute any canary plan.
# It does NOT authorize canary execution.
# It does NOT create controlled canary runtime envelope behavior.
# It does NOT grant canary runtime envelope authority.
# It does NOT promote canon or mutate runtime/scheduler/forecast.
# It does NOT implement P116 behavior.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryAuthorizationPackageReviewRecord.v1"
LANE_ID = "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT"
REQUIRED_P114_ARTIFACT_TYPE = "ResearchCanaryAuthorizationPackageDraft.v1"
REQUIRED_P114_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_CONTINUE"
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

REQUIRED_PACKAGE_REVIEW_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "package_draft_complete_observed",
    "package_scope_review_complete",
    "package_conditions_review_complete",
    "rollback_binding_review_complete",
    "monitoring_binding_review_complete",
    "blast_radius_binding_review_complete",
    "exit_criteria_binding_review_complete",
    "provenance_review_complete",
    "safety_review_complete",
    "execution_disabled_review_complete",
    "operator_review_observed",
    "authority_drift_observed",
    "notes",
)

PACKAGE_REVIEW_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "package_draft_complete_observed",
    "package_scope_review_complete",
    "package_conditions_review_complete",
    "rollback_binding_review_complete",
    "monitoring_binding_review_complete",
    "blast_radius_binding_review_complete",
    "exit_criteria_binding_review_complete",
    "provenance_review_complete",
    "safety_review_complete",
    "execution_disabled_review_complete",
    "operator_review_observed",
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


def _validate_p114_packet(p114_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p114_packet is None:
        return ["p114_packet_missing"], None
    if not isinstance(p114_packet, dict):
        return ["p114_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p114_packet.get("artifact_type") != REQUIRED_P114_ARTIFACT_TYPE:
        reasons.append(
            f"p114_artifact_type_mismatch:{p114_packet.get('artifact_type')!r}"
        )
    if p114_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p114_lane_id_mismatch:{p114_packet.get('lane_id')!r}")
    if p114_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p114_canonical_status_mismatch:{p114_packet.get('canonical_status')!r}"
        )
    if p114_packet.get("advisory_only") is not True:
        reasons.append("p114_advisory_only_not_true")
    if p114_packet.get("projection_only") is not True:
        reasons.append("p114_projection_only_not_true")

    p114_status = p114_packet.get("status")
    p114_lane_status = p114_packet.get("canary_authorization_package_draft_status")
    if p114_status != "CANARY_AUTHORIZATION_PACKAGE_DRAFT_EMITTED":
        reasons.append(f"p114_status_not_emitted:{p114_status!r}")
    if p114_lane_status != "CANARY_AUTHORIZATION_PACKAGE_DRAFT_COMPLETE":
        reasons.append(f"p114_status_not_pass:{p114_lane_status!r}")

    if p114_packet.get("recommended_next_lane") != REQUIRED_P114_RECOMMENDATION:
        reasons.append(
            "p114_recommendation_chain_mismatch:"
            f"{p114_packet.get('recommended_next_lane')!r}"
        )

    complete_candidates = p114_packet.get("authorization_package_draft_complete_candidates")
    if not isinstance(complete_candidates, list):
        reasons.append("p114_authorization_package_draft_complete_candidates_malformed")
    elif not complete_candidates:
        reasons.append("p114_no_authorization_package_draft_complete_candidates")
    elif any(not isinstance(candidate, str) for candidate in complete_candidates):
        reasons.append(
            "p114_authorization_package_draft_complete_candidates_entry_malformed"
        )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p114_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p114_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p114_{field_name}_entry_malformed")

    return sorted(set(reasons)), p114_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "authorization_package_draft_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "authorization_package_draft_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p114(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p114_reports_authority_drift")

    if (
        packet.get("canary_authorization_package_draft_status")
        == "CANARY_AUTHORIZATION_PACKAGE_DRAFT_REJECTED_AUTHORITY_DRIFT"
    ):
        findings.append("p114_lane_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"p114_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_package_review_observations")
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
            "package_draft_complete_observed": False,
            "package_scope_review_complete": False,
            "package_conditions_review_complete": False,
            "rollback_binding_review_complete": False,
            "monitoring_binding_review_complete": False,
            "blast_radius_binding_review_complete": False,
            "exit_criteria_binding_review_complete": False,
            "provenance_review_complete": False,
            "safety_review_complete": False,
            "execution_disabled_review_complete": False,
            "operator_review_observed": False,
            "authority_drift_observed": False,
            "missing_requirements": ["package_review_observations_missing"],
            "canary_authorization_package_review_status": (
                "CANARY_AUTHORIZATION_PACKAGE_REVIEW_INCOMPLETE"
            ),
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    criteria: dict[str, bool] = {}
    for field in PACKAGE_REVIEW_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in PACKAGE_REVIEW_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_package_review_authority_drift:{candidate_id}")
        candidate_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        candidate_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE"
    else:
        candidate_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "package_draft_complete_observed": criteria["package_draft_complete_observed"],
        "package_scope_review_complete": criteria["package_scope_review_complete"],
        "package_conditions_review_complete": criteria[
            "package_conditions_review_complete"
        ],
        "rollback_binding_review_complete": criteria["rollback_binding_review_complete"],
        "monitoring_binding_review_complete": criteria[
            "monitoring_binding_review_complete"
        ],
        "blast_radius_binding_review_complete": criteria[
            "blast_radius_binding_review_complete"
        ],
        "exit_criteria_binding_review_complete": criteria[
            "exit_criteria_binding_review_complete"
        ],
        "provenance_review_complete": criteria["provenance_review_complete"],
        "safety_review_complete": criteria["safety_review_complete"],
        "execution_disabled_review_complete": criteria[
            "execution_disabled_review_complete"
        ],
        "operator_review_observed": criteria["operator_review_observed"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_authorization_package_review_status": candidate_status,
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
    reviewed_complete_candidates: list[str] = []
    reviewed_incomplete_candidates: list[str] = []
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
            candidate_status["canary_authorization_package_review_status"]
            == "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE"
        ):
            reviewed_complete_candidates.append(candidate_id)
        else:
            reviewed_incomplete_candidates.append(candidate_id)

    return (
        candidate_statuses,
        reviewed_complete_candidates,
        reviewed_incomplete_candidates,
        missing_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_authorization_package_review_record(
    *,
    p114_packet: dict[str, Any] | None = None,
    package_review_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p114 = _validate_p114_packet(p114_packet)
    candidate_lists = _extract_candidate_lists(normalized_p114)
    authority_drift_findings = _detect_authority_drift_p114(normalized_p114)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    package_draft_complete_candidates = candidate_lists[
        "authorization_package_draft_complete_candidates"
    ]

    candidate_statuses: list[dict[str, Any]] = []
    package_review_complete_candidates: list[str] = []
    package_review_incomplete_candidates: list[str] = []
    missing_requirements: dict[str, list[str]] = {}
    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_statuses,
            package_review_complete_candidates,
            package_review_incomplete_candidates,
            missing_requirements,
            observation_drift_findings,
        ) = _build_candidate_statuses(
            complete_candidates=package_draft_complete_candidates,
            observations_packet=package_review_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P114 or package review observations report authority drift or authority lock "
            "drift; P115 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P114 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "authorization_package_draft_complete_candidates, or does not recommend "
            "P115; P115 cannot compute."
        )
    else:
        status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD_EMITTED"
        all_complete = (
            len(package_draft_complete_candidates) > 0
            and len(package_review_complete_candidates)
            == len(package_draft_complete_candidates)
            and not package_review_incomplete_candidates
        )
        if all_complete:
            lane_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete package review observations and no "
                "authority drift exists; proceed to advisory P116 authorization decision "
                "record."
            )
        else:
            lane_status = "CANARY_AUTHORIZATION_PACKAGE_REVIEW_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing required package review "
                "observations; continue P115."
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
            normalized_p114.get("status") if isinstance(normalized_p114, dict) else None
        ),
        "upstream_canary_authorization_package_draft_status": (
            normalized_p114.get("canary_authorization_package_draft_status")
            if isinstance(normalized_p114, dict)
            else None
        ),
        "lane_status": lane_status,
        "canary_authorization_package_review_record_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": package_draft_complete_candidates,
        "package_review_complete_candidates": package_review_complete_candidates,
        "package_review_incomplete_candidates": package_review_incomplete_candidates,
        "candidate_statuses": candidate_statuses,
        "candidate_package_review_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "missing_package_review_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "required_package_review_observations": list(
            REQUIRED_PACKAGE_REVIEW_OBSERVATION_FIELDS
        ),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p114_research_canary_authorization_package_draft",
            "mapping_method": "deterministic_canary_authorization_package_review_record",
            "required_package_review_observation_fields": list(
                REQUIRED_PACKAGE_REVIEW_OBSERVATION_FIELDS
            ),
            "package_review_completeness_fields": list(
                PACKAGE_REVIEW_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "package_review_is_not_canary_authorization",
                "package_review_is_not_canary_activation",
                "package_review_is_not_canary_plan_execution",
                "package_review_is_not_canary_package_execution",
                "package_review_is_not_canary_runtime_envelope_authority",
                "package_review_is_not_runtime_mutation",
                "package_review_is_not_scheduler_mutation",
                "package_review_is_not_forecast_mutation",
                "package_review_is_not_canon_promotion",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p116_only_when_every_analyzed_candidate_has_complete_"
                "package_review_observations_and_no_authority_drift"
            ),
            "p114_status": (
                normalized_p114.get("status") if isinstance(normalized_p114, dict) else None
            ),
            "p114_artifact_type": (
                normalized_p114.get("artifact_type")
                if isinstance(normalized_p114, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_authorization_package_review_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
