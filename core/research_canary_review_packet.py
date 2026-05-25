from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryReviewPacket.v1"
LANE_ID = "P107_RESEARCH_CANARY_REVIEW_PACKET"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER"
REQUIRED_P106_ARTIFACT_TYPE = "ResearchCanaryEligibilityDossier.v1"
REQUIRED_P106_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P108_RESEARCH_CANARY_DECISION_RECORD"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P107_RESEARCH_CANARY_REVIEW_PACKET_CONTINUE"

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
)

REQUIRED_REVIEW_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "eligibility_dossier_attached",
    "canary_scope_attached",
    "rollback_plan_attached",
    "monitoring_plan_attached",
    "blast_radius_attached",
    "exit_criteria_attached",
    "operator_review_packet_attached",
    "provenance_bundle_attached",
    "risk_notes_attached",
    "authority_drift_observed",
    "notes",
)

REVIEW_PACKET_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "eligibility_dossier_attached",
    "canary_scope_attached",
    "rollback_plan_attached",
    "monitoring_plan_attached",
    "blast_radius_attached",
    "exit_criteria_attached",
    "operator_review_packet_attached",
    "provenance_bundle_attached",
    "risk_notes_attached",
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


def _validate_p106_packet(p106_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p106_packet is None:
        return ["p106_packet_missing"], None
    if not isinstance(p106_packet, dict):
        return ["p106_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p106_packet.get("artifact_type") != REQUIRED_P106_ARTIFACT_TYPE:
        reasons.append(
            f"p106_artifact_type_mismatch:{p106_packet.get('artifact_type')!r}"
        )
    if p106_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p106_lane_id_mismatch:{p106_packet.get('lane_id')!r}")
    if p106_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p106_canonical_status_mismatch:{p106_packet.get('canonical_status')!r}"
        )
    if p106_packet.get("advisory_only") is not True:
        reasons.append("p106_advisory_only_not_true")
    if p106_packet.get("projection_only") is not True:
        reasons.append("p106_projection_only_not_true")

    p106_status = p106_packet.get("status")
    p106_dossier_status = p106_packet.get("canary_eligibility_dossier_status")
    if not (
        p106_status == "CANARY_ELIGIBILITY_DOSSIER_EMITTED"
        and p106_dossier_status == "EMITTED"
    ):
        reasons.append(f"p106_status_not_emitted:{p106_status!r}")
        reasons.append(
            f"p106_canary_eligibility_dossier_status_not_emitted:{p106_dossier_status!r}"
        )

    if p106_packet.get("recommended_next_lane") != REQUIRED_P106_RECOMMENDATION:
        reasons.append(
            "p106_recommendation_chain_mismatch:"
            f"{p106_packet.get('recommended_next_lane')!r}"
        )

    dossier_eligible_candidates = p106_packet.get("dossier_eligible_candidates")
    if not isinstance(dossier_eligible_candidates, list):
        reasons.append("p106_dossier_eligible_candidates_malformed")
    elif not dossier_eligible_candidates:
        reasons.append("p106_no_dossier_eligible_candidates")
    else:
        for candidate in dossier_eligible_candidates:
            if not isinstance(candidate, str):
                reasons.append("p106_dossier_eligible_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p106_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p106_{field_name}_malformed")
        elif any(not isinstance(c, str) for c in value):
            reasons.append(f"p106_{field_name}_entry_malformed")

    authority_locks = p106_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p106_authority_locks_malformed")
    else:
        for key in (
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
        ):
            if key not in authority_locks:
                reasons.append(f"p106_authority_lock_missing:{key}")

    return sorted(set(reasons)), p106_packet


def _extract_candidate_lists(
    packet: dict[str, Any] | None,
) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "dossier_eligible_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "dossier_eligible_candidates",
    ):
        value = packet.get(field_name)
        extracted[field_name] = (
            [entry for entry in value if isinstance(entry, str)]
            if isinstance(value, list)
            else []
        )
    return extracted


def _detect_authority_drift_p106(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p106_reports_authority_drift")

    if packet.get("canary_eligibility_dossier_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p106_dossier_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in (
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
        ):
            if authority_locks.get(key) is not False:
                findings.append(f"p106_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_review_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_review_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        missing_review_requirements = ["review_observations_missing"]
        canary_review_status = "CANARY_REVIEW_PACKET_INCOMPLETE"
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "eligibility_dossier_attached": False,
            "canary_scope_attached": False,
            "rollback_plan_attached": False,
            "monitoring_plan_attached": False,
            "blast_radius_attached": False,
            "exit_criteria_attached": False,
            "operator_review_packet_attached": False,
            "provenance_bundle_attached": False,
            "risk_notes_attached": False,
            "authority_drift_observed": False,
            "missing_review_requirements": missing_review_requirements,
            "canary_review_status": canary_review_status,
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    criteria: dict[str, bool] = {}
    for field in REVIEW_PACKET_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_review_requirements: list[str] = []
    authority_findings: list[str] = []

    if authority_drift_observed:
        missing_review_requirements.append("authority_drift_observed")
        canary_review_status = "CANARY_REVIEW_REJECTED_AUTHORITY_DRIFT"
        authority_findings.append(
            f"candidate_review_authority_drift_observed:{candidate_id}"
        )
    else:
        for field in REVIEW_PACKET_COMPLETENESS_FIELDS:
            if not criteria[field]:
                missing_review_requirements.append(f"{field}_not_true")

        if not missing_review_requirements:
            canary_review_status = "CANARY_REVIEW_PACKET_COMPLETE"
        else:
            canary_review_status = "CANARY_REVIEW_PACKET_INCOMPLETE"

    status = {
        "candidate_id": candidate_id,
        "eligibility_dossier_attached": criteria["eligibility_dossier_attached"],
        "canary_scope_attached": criteria["canary_scope_attached"],
        "rollback_plan_attached": criteria["rollback_plan_attached"],
        "monitoring_plan_attached": criteria["monitoring_plan_attached"],
        "blast_radius_attached": criteria["blast_radius_attached"],
        "exit_criteria_attached": criteria["exit_criteria_attached"],
        "operator_review_packet_attached": criteria["operator_review_packet_attached"],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "risk_notes_attached": criteria["risk_notes_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_review_requirements": sorted(set(missing_review_requirements)),
        "canary_review_status": canary_review_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status["notes"] = notes

    return status, authority_findings


def _build_candidate_review_statuses(
    *,
    dossier_eligible_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_review_statuses: list[dict[str, Any]] = []
    review_packet_complete_candidates: list[str] = []
    review_packet_incomplete_candidates: list[str] = []
    missing_review_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in dossier_eligible_candidates:
        observation = _get_candidate_observation(observations_packet, candidate_id)
        status, candidate_authority_findings = _build_candidate_review_status(
            candidate_id,
            observation,
        )
        candidate_review_statuses.append(status)
        authority_findings.extend(candidate_authority_findings)

        missing = status["missing_review_requirements"]
        if isinstance(missing, list) and missing:
            missing_review_requirements[candidate_id] = list(missing)

        review_status = status["canary_review_status"]
        if review_status == "CANARY_REVIEW_PACKET_COMPLETE":
            review_packet_complete_candidates.append(candidate_id)
        else:
            review_packet_incomplete_candidates.append(candidate_id)

    return (
        candidate_review_statuses,
        review_packet_complete_candidates,
        review_packet_incomplete_candidates,
        missing_review_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_review_packet(
    *,
    p106_packet: dict[str, Any] | None = None,
    review_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p106 = _validate_p106_packet(p106_packet)
    candidate_lists = _extract_candidate_lists(normalized_p106)
    authority_drift_findings = _detect_authority_drift_p106(normalized_p106)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    dossier_eligible_candidates = candidate_lists["dossier_eligible_candidates"]

    candidate_review_statuses: list[dict[str, Any]] = []
    review_packet_complete_candidates: list[str] = []
    review_packet_incomplete_candidates: list[str] = []
    missing_review_requirements: dict[str, list[str]] = {}

    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_review_statuses,
            review_packet_complete_candidates,
            review_packet_incomplete_candidates,
            missing_review_requirements,
            observation_drift_findings,
        ) = _build_candidate_review_statuses(
            dossier_eligible_candidates=dossier_eligible_candidates,
            observations_packet=review_observations_packet,
        )

    all_authority_drift = sorted(
        set(authority_drift_findings + observation_drift_findings)
    )

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_review_packet_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P106 or review observations report authority drift; P107 remains "
            "anti-authority advisory governance and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        canary_review_packet_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P106 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, or has no dossier_eligible_candidates; P107 cannot compute."
        )
    else:
        status = "CANARY_REVIEW_PACKET_EMITTED"
        canary_review_packet_status = "EMITTED"

        all_candidates_complete = (
            len(dossier_eligible_candidates) > 0
            and len(review_packet_complete_candidates)
            == len(dossier_eligible_candidates)
            and not review_packet_incomplete_candidates
        )

        if all_candidates_complete:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has a complete review packet with all "
                "required observations confirmed and no authority drift; proceed to "
                "advisory P108 canary decision record."
            )
        else:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing review observations "
                "or have incomplete review packet requirements; continue P107 review."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_canary_eligibility_dossier_status": (
            normalized_p106.get("status") if isinstance(normalized_p106, dict) else None
        ),
        "canary_review_packet_status": canary_review_packet_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": dossier_eligible_candidates,
        "review_packet_complete_candidates": review_packet_complete_candidates,
        "review_packet_incomplete_candidates": review_packet_incomplete_candidates,
        "candidate_review_statuses": candidate_review_statuses,
        "required_review_observations": list(REQUIRED_REVIEW_OBSERVATION_FIELDS),
        "missing_review_requirements": missing_review_requirements,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p106_research_canary_eligibility_dossier",
            "mapping_method": "deterministic_canary_review_packet",
            "required_review_observation_fields": list(
                REQUIRED_REVIEW_OBSERVATION_FIELDS
            ),
            "review_packet_completeness_fields": list(
                REVIEW_PACKET_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "canary_review_packet_is_not_canary_activation",
                "canary_review_packet_is_not_implementation_authority",
                "canary_review_packet_is_not_canon_promotion",
                "canary_review_packet_is_not_production_activation",
                "canary_review_packet_is_not_runtime_mutation",
                "canary_review_packet_is_not_scheduler_authority",
                "canary_review_packet_is_not_forecast_weight_authority",
                "canary_review_packet_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p108_only_when_every_analyzed_candidate_has_complete_"
                "review_packet_observations_and_no_authority_drift"
            ),
            "p106_status": (
                normalized_p106.get("status")
                if isinstance(normalized_p106, dict)
                else None
            ),
            "p106_artifact_type": (
                normalized_p106.get("artifact_type")
                if isinstance(normalized_p106, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_canary_review_packet(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
