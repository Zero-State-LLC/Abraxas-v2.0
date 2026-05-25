from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryEligibilityDossier.v1"
LANE_ID = "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER"
REQUIRED_P105_ARTIFACT_TYPE = "ResearchPromotionBlockerLedger.v1"
REQUIRED_P105_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P107_RESEARCH_CANARY_REVIEW_PACKET"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER_CONTINUE"

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
)

REQUIRED_ELIGIBILITY_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "blocker_review_complete_observed",
    "operator_review_observed",
    "provenance_complete_observed",
    "replay_stability_observed",
    "boundary_stability_observed",
    "canary_scope_defined",
    "rollback_plan_defined",
    "monitoring_plan_defined",
    "blast_radius_defined",
    "exit_criteria_defined",
    "authority_drift_observed",
    "notes",
)

ELIGIBILITY_CRITERIA_FIELDS: tuple[str, ...] = (
    "blocker_review_complete_observed",
    "operator_review_observed",
    "provenance_complete_observed",
    "replay_stability_observed",
    "boundary_stability_observed",
    "canary_scope_defined",
    "rollback_plan_defined",
    "monitoring_plan_defined",
    "blast_radius_defined",
    "exit_criteria_defined",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, str)]


def _to_bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _validate_p105_packet(p105_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p105_packet is None:
        return ["p105_packet_missing"], None
    if not isinstance(p105_packet, dict):
        return ["p105_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p105_packet.get("artifact_type") != REQUIRED_P105_ARTIFACT_TYPE:
        reasons.append(
            f"p105_artifact_type_mismatch:{p105_packet.get('artifact_type')!r}"
        )
    if p105_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p105_lane_id_mismatch:{p105_packet.get('lane_id')!r}")
    if p105_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p105_canonical_status_mismatch:{p105_packet.get('canonical_status')!r}"
        )
    if p105_packet.get("advisory_only") is not True:
        reasons.append("p105_advisory_only_not_true")
    if p105_packet.get("projection_only") is not True:
        reasons.append("p105_projection_only_not_true")

    p105_status = p105_packet.get("status")
    p105_ledger_status = p105_packet.get("promotion_blocker_ledger_status")
    if not (
        p105_status == "PROMOTION_BLOCKER_LEDGER_EMITTED"
        and p105_ledger_status == "EMITTED"
    ):
        reasons.append(
            f"p105_status_not_emitted:{p105_status!r}"
        )
        reasons.append(
            f"p105_promotion_blocker_ledger_status_not_emitted:{p105_ledger_status!r}"
        )

    if p105_packet.get("recommended_next_lane") != REQUIRED_P105_RECOMMENDATION:
        reasons.append(
            "p105_recommendation_chain_mismatch:"
            f"{p105_packet.get('recommended_next_lane')!r}"
        )

    blocker_review_complete_candidates = p105_packet.get(
        "blocker_review_complete_candidates"
    )
    if not isinstance(blocker_review_complete_candidates, list):
        reasons.append("p105_blocker_review_complete_candidates_malformed")
    else:
        for candidate in blocker_review_complete_candidates:
            if not isinstance(candidate, str):
                reasons.append(
                    "p105_blocker_review_complete_candidates_entry_malformed"
                )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p105_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p105_{field_name}_malformed")
        elif any(not isinstance(c, str) for c in value):
            reasons.append(f"p105_{field_name}_entry_malformed")

    authority_locks = p105_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p105_authority_locks_malformed")
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
        ):
            if key not in authority_locks:
                reasons.append(f"p105_authority_lock_missing:{key}")

    return sorted(set(reasons)), p105_packet


def _extract_candidate_lists(
    packet: dict[str, Any] | None,
) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "blocker_review_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "blocker_review_complete_candidates",
    ):
        value = packet.get(field_name)
        extracted[field_name] = (
            [entry for entry in value if isinstance(entry, str)]
            if isinstance(value, list)
            else []
        )
    return extracted


def _detect_authority_drift_p105(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p105_reports_authority_drift")

    if packet.get("promotion_blocker_ledger_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p105_ledger_status_reports_authority_drift")

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
        ):
            if authority_locks.get(key) is not False:
                findings.append(f"p105_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_eligibility_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_eligibility_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not observation:
        missing_eligibility_requirements = ["eligibility_observations_missing"]
        canary_eligibility_status = "CANARY_ELIGIBILITY_BLOCKED_MISSING_OBSERVATIONS"
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "blocker_review_complete_observed": False,
            "operator_review_observed": False,
            "provenance_complete_observed": False,
            "replay_stability_observed": False,
            "boundary_stability_observed": False,
            "canary_scope_defined": False,
            "rollback_plan_defined": False,
            "monitoring_plan_defined": False,
            "blast_radius_defined": False,
            "exit_criteria_defined": False,
            "authority_drift_observed": False,
            "missing_eligibility_requirements": missing_eligibility_requirements,
            "canary_eligibility_status": canary_eligibility_status,
        }
        return status, []

    candidate_id_observed = observation.get("candidate_id")
    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""

    authority_drift_observed = _to_bool_or_none(
        observation.get("authority_drift_observed")
    ) is True

    criteria: dict[str, bool] = {}
    for field in ELIGIBILITY_CRITERIA_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    missing_eligibility_requirements: list[str] = []
    authority_findings: list[str] = []

    if authority_drift_observed:
        missing_eligibility_requirements.append("authority_drift_observed")
        canary_eligibility_status = "CANARY_ELIGIBILITY_REJECTED_AUTHORITY_DRIFT"
        authority_findings.append(
            f"candidate_authority_drift_observed:{candidate_id}"
        )
    else:
        for field in ELIGIBILITY_CRITERIA_FIELDS:
            if not criteria[field]:
                missing_eligibility_requirements.append(f"{field}_not_true")

        if not missing_eligibility_requirements:
            canary_eligibility_status = "CANARY_DOSSIER_ELIGIBLE"
        else:
            canary_eligibility_status = "CANARY_ELIGIBILITY_INCOMPLETE"

    status = {
        "candidate_id": candidate_id,
        "blocker_review_complete_observed": criteria["blocker_review_complete_observed"],
        "operator_review_observed": criteria["operator_review_observed"],
        "provenance_complete_observed": criteria["provenance_complete_observed"],
        "replay_stability_observed": criteria["replay_stability_observed"],
        "boundary_stability_observed": criteria["boundary_stability_observed"],
        "canary_scope_defined": criteria["canary_scope_defined"],
        "rollback_plan_defined": criteria["rollback_plan_defined"],
        "monitoring_plan_defined": criteria["monitoring_plan_defined"],
        "blast_radius_defined": criteria["blast_radius_defined"],
        "exit_criteria_defined": criteria["exit_criteria_defined"],
        "authority_drift_observed": authority_drift_observed,
        "missing_eligibility_requirements": sorted(set(missing_eligibility_requirements)),
        "canary_eligibility_status": canary_eligibility_status,
    }

    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        notes = f"{notes} [candidate_id_mismatch]".strip()
    if notes:
        status["notes"] = notes

    return status, authority_findings


def _build_candidate_eligibility_statuses(
    *,
    blocker_review_complete_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
    dict[str, list[str]],
    list[str],
]:
    candidate_eligibility_statuses: list[dict[str, Any]] = []
    dossier_eligible_candidates: list[str] = []
    dossier_ineligible_candidates: list[str] = []
    dossier_incomplete_candidates: list[str] = []
    missing_eligibility_requirements: dict[str, list[str]] = {}
    authority_findings: list[str] = []

    for candidate_id in blocker_review_complete_candidates:
        observation = _get_candidate_observation(observations_packet, candidate_id)
        status, candidate_authority_findings = _build_candidate_eligibility_status(
            candidate_id,
            observation,
        )
        candidate_eligibility_statuses.append(status)
        authority_findings.extend(candidate_authority_findings)

        missing = status["missing_eligibility_requirements"]
        if isinstance(missing, list) and missing:
            missing_eligibility_requirements[candidate_id] = list(missing)

        elig_status = status["canary_eligibility_status"]
        if elig_status == "CANARY_DOSSIER_ELIGIBLE":
            dossier_eligible_candidates.append(candidate_id)
        elif elig_status == "CANARY_ELIGIBILITY_INCOMPLETE":
            dossier_incomplete_candidates.append(candidate_id)
        else:
            dossier_ineligible_candidates.append(candidate_id)

    return (
        candidate_eligibility_statuses,
        dossier_eligible_candidates,
        dossier_ineligible_candidates,
        dossier_incomplete_candidates,
        missing_eligibility_requirements,
        sorted(set(authority_findings)),
    )


def build_research_canary_eligibility_dossier(
    *,
    p105_packet: dict[str, Any] | None = None,
    eligibility_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p105 = _validate_p105_packet(p105_packet)
    candidate_lists = _extract_candidate_lists(normalized_p105)
    authority_drift_findings = _detect_authority_drift_p105(normalized_p105)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    blocker_review_complete_candidates = candidate_lists[
        "blocker_review_complete_candidates"
    ]

    if not not_computable_reasons and not blocker_review_complete_candidates:
        not_computable_reasons = ["p105_no_blocker_review_complete_candidates"]

    candidate_eligibility_statuses: list[dict[str, Any]] = []
    dossier_eligible_candidates: list[str] = []
    dossier_ineligible_candidates: list[str] = []
    dossier_incomplete_candidates: list[str] = []
    missing_eligibility_requirements: dict[str, list[str]] = {}

    observation_drift_findings: list[str] = []

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_eligibility_statuses,
            dossier_eligible_candidates,
            dossier_ineligible_candidates,
            dossier_incomplete_candidates,
            missing_eligibility_requirements,
            observation_drift_findings,
        ) = _build_candidate_eligibility_statuses(
            blocker_review_complete_candidates=blocker_review_complete_candidates,
            observations_packet=eligibility_observations_packet,
        )

    all_authority_drift = sorted(
        set(authority_drift_findings + observation_drift_findings)
    )

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_eligibility_dossier_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P105 or eligibility observations report authority drift; P106 remains "
            "anti-authority advisory governance and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        canary_eligibility_dossier_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P105 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, or has no blocker_review_complete_candidates; P106 cannot compute."
        )
    else:
        status = "CANARY_ELIGIBILITY_DOSSIER_EMITTED"
        canary_eligibility_dossier_status = "EMITTED"

        all_candidates_eligible = (
            len(blocker_review_complete_candidates) > 0
            and len(dossier_eligible_candidates)
            == len(blocker_review_complete_candidates)
            and not dossier_ineligible_candidates
            and not dossier_incomplete_candidates
        )

        if all_candidates_eligible:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete dossier eligibility with all "
                "required observations confirmed and no authority drift; proceed to "
                "advisory P107 canary review packet."
            )
        else:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are missing eligibility observations "
                "or have incomplete eligibility criteria; continue P106 dossier review."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_promotion_blocker_ledger_status": (
            normalized_p105.get("status") if isinstance(normalized_p105, dict) else None
        ),
        "canary_eligibility_dossier_status": canary_eligibility_dossier_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": blocker_review_complete_candidates,
        "dossier_eligible_candidates": dossier_eligible_candidates,
        "dossier_ineligible_candidates": dossier_ineligible_candidates,
        "dossier_incomplete_candidates": dossier_incomplete_candidates,
        "candidate_eligibility_statuses": candidate_eligibility_statuses,
        "required_eligibility_observations": list(
            REQUIRED_ELIGIBILITY_OBSERVATION_FIELDS
        ),
        "missing_eligibility_requirements": missing_eligibility_requirements,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p105_research_promotion_blocker_ledger",
            "mapping_method": "deterministic_canary_eligibility_dossier",
            "required_eligibility_observation_fields": list(
                REQUIRED_ELIGIBILITY_OBSERVATION_FIELDS
            ),
            "eligibility_criteria_fields": list(ELIGIBILITY_CRITERIA_FIELDS),
            "boundary_rules": [
                "canary_eligibility_dossier_is_not_canary_activation",
                "canary_eligibility_dossier_is_not_implementation_authority",
                "canary_eligibility_dossier_is_not_canon_promotion",
                "canary_eligibility_dossier_is_not_production_activation",
                "canary_eligibility_dossier_is_not_runtime_mutation",
                "canary_eligibility_dossier_is_not_scheduler_authority",
                "canary_eligibility_dossier_is_not_forecast_weight_authority",
                "canary_eligibility_dossier_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p107_only_when_every_analyzed_candidate_is_dossier_eligible_"
                "with_all_criteria_true_and_no_authority_drift"
            ),
            "p105_status": (
                normalized_p105.get("status")
                if isinstance(normalized_p105, dict)
                else None
            ),
            "p105_artifact_type": (
                normalized_p105.get("artifact_type")
                if isinstance(normalized_p105, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_canary_eligibility_dossier(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
