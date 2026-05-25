from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryDecisionRecord.v1"
LANE_ID = "P108_RESEARCH_CANARY_DECISION_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P107_RESEARCH_CANARY_REVIEW_PACKET"
REQUIRED_P107_ARTIFACT_TYPE = "ResearchCanaryReviewPacket.v1"
REQUIRED_P107_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_APPROVE = "P109_RESEARCH_CANARY_PLAN_DRAFT"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P108_RESEARCH_CANARY_DECISION_RECORD_CONTINUE"

ALLOWED_DECISIONS: tuple[str, ...] = (
    "hold",
    "request_repair",
    "reject",
    "approve_for_future_canary_plan",
)

FORBIDDEN_DECISIONS: tuple[str, ...] = (
    "activate_canary",
    "grant_canary_authority",
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
)

REQUIRED_DECISION_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "decision",
    "operator_decision_observed",
    "decision_rationale_attached",
    "provenance_bundle_attached",
    "review_packet_complete_observed",
    "authority_drift_observed",
    "notes",
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


def _validate_p107_packet(p107_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p107_packet is None:
        return ["p107_packet_missing"], None
    if not isinstance(p107_packet, dict):
        return ["p107_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p107_packet.get("artifact_type") != REQUIRED_P107_ARTIFACT_TYPE:
        reasons.append(
            f"p107_artifact_type_mismatch:{p107_packet.get('artifact_type')!r}"
        )
    if p107_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p107_lane_id_mismatch:{p107_packet.get('lane_id')!r}")
    if p107_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p107_canonical_status_mismatch:{p107_packet.get('canonical_status')!r}"
        )
    if p107_packet.get("advisory_only") is not True:
        reasons.append("p107_advisory_only_not_true")
    if p107_packet.get("projection_only") is not True:
        reasons.append("p107_projection_only_not_true")

    p107_status = p107_packet.get("status")
    p107_review_status = p107_packet.get("canary_review_packet_status")
    if not (
        p107_status == "CANARY_REVIEW_PACKET_EMITTED"
        and p107_review_status == "EMITTED"
    ):
        reasons.append(f"p107_status_not_emitted:{p107_status!r}")
        reasons.append(
            f"p107_canary_review_packet_status_not_emitted:{p107_review_status!r}"
        )

    if p107_packet.get("recommended_next_lane") != REQUIRED_P107_RECOMMENDATION:
        reasons.append(
            "p107_recommendation_chain_mismatch:"
            f"{p107_packet.get('recommended_next_lane')!r}"
        )

    review_packet_complete_candidates = p107_packet.get("review_packet_complete_candidates")
    if not isinstance(review_packet_complete_candidates, list):
        reasons.append("p107_review_packet_complete_candidates_malformed")
    elif not review_packet_complete_candidates:
        reasons.append("p107_no_review_packet_complete_candidates")
    else:
        for candidate in review_packet_complete_candidates:
            if not isinstance(candidate, str):
                reasons.append(
                    "p107_review_packet_complete_candidates_entry_malformed"
                )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p107_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p107_{field_name}_malformed")
        elif any(not isinstance(c, str) for c in value):
            reasons.append(f"p107_{field_name}_entry_malformed")

    authority_locks = p107_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p107_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p107_authority_lock_missing:{key}")

    return sorted(set(reasons)), p107_packet


def _extract_candidate_lists(
    packet: dict[str, Any] | None,
) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "review_packet_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "review_packet_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p107(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p107_reports_authority_drift")

    if packet.get("canary_review_packet_status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p107_review_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p107_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_decision_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_decision_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> tuple[dict[str, Any], list[str], bool]:
    if not observation:
        status: dict[str, Any] = {
            "candidate_id": candidate_id,
            "decision": "hold",
            "operator_decision_observed": False,
            "decision_rationale_attached": False,
            "provenance_bundle_attached": False,
            "review_packet_complete_observed": False,
            "authority_drift_observed": False,
            "missing_decision_requirements": ["decision_observations_missing"],
            "canary_decision_status": "CANARY_DECISION_HELD_PENDING_REVIEW",
        }
        return status, [], False

    decision_observed = observation.get("decision")
    decision = decision_observed if isinstance(decision_observed, str) else "hold"

    operator_decision_observed = (
        _to_bool_or_none(observation.get("operator_decision_observed")) is True
    )
    decision_rationale_attached = (
        _to_bool_or_none(observation.get("decision_rationale_attached")) is True
    )
    provenance_bundle_attached = (
        _to_bool_or_none(observation.get("provenance_bundle_attached")) is True
    )
    review_packet_complete_observed = (
        _to_bool_or_none(observation.get("review_packet_complete_observed")) is True
    )
    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_decision_requirements: list[str] = []
    authority_findings: list[str] = []

    if not operator_decision_observed:
        missing_decision_requirements.append("operator_decision_observed_not_true")
    if not decision_rationale_attached:
        missing_decision_requirements.append("decision_rationale_attached_not_true")
    if not provenance_bundle_attached:
        missing_decision_requirements.append("provenance_bundle_attached_not_true")
    if not review_packet_complete_observed:
        missing_decision_requirements.append("review_packet_complete_observed_not_true")

    if decision not in ALLOWED_DECISIONS:
        if decision in FORBIDDEN_DECISIONS:
            authority_findings.append(f"forbidden_decision:{candidate_id}:{decision}")
        else:
            missing_decision_requirements.append(f"decision_not_allowed:{decision}")
            decision = "hold"

    if authority_drift_observed:
        authority_findings.append(
            f"candidate_decision_authority_drift_observed:{candidate_id}"
        )

    if authority_findings:
        canary_decision_status = "CANARY_DECISION_REJECTED_AUTHORITY_DRIFT"
    elif decision == "approve_for_future_canary_plan" and not missing_decision_requirements:
        canary_decision_status = "CANARY_DECISION_APPROVED_FOR_FUTURE_PLAN"
    elif decision == "request_repair":
        canary_decision_status = "CANARY_DECISION_REPAIR_REQUESTED"
    elif decision == "reject":
        canary_decision_status = "CANARY_DECISION_REJECTED"
    else:
        canary_decision_status = "CANARY_DECISION_HELD_PENDING_REVIEW"

    status = {
        "candidate_id": candidate_id,
        "decision": decision,
        "operator_decision_observed": operator_decision_observed,
        "decision_rationale_attached": decision_rationale_attached,
        "provenance_bundle_attached": provenance_bundle_attached,
        "review_packet_complete_observed": review_packet_complete_observed,
        "authority_drift_observed": authority_drift_observed,
        "missing_decision_requirements": sorted(set(missing_decision_requirements)),
        "canary_decision_status": canary_decision_status,
    }

    notes_value = observation.get("notes")
    if isinstance(notes_value, str) and notes_value:
        status["notes"] = notes_value

    candidate_id_observed = observation.get("candidate_id")
    if candidate_id_observed is not None and candidate_id_observed != candidate_id:
        existing_notes = status.get("notes", "")
        status["notes"] = f"{existing_notes} [candidate_id_mismatch]".strip()

    approved_with_required_evidence = (
        decision == "approve_for_future_canary_plan"
        and operator_decision_observed
        and decision_rationale_attached
        and provenance_bundle_attached
        and review_packet_complete_observed
        and not authority_drift_observed
    )

    return status, authority_findings, approved_with_required_evidence


def build_research_canary_decision_record(
    *,
    p107_packet: dict[str, Any] | None = None,
    decision_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p107 = _validate_p107_packet(p107_packet)
    candidate_lists = _extract_candidate_lists(normalized_p107)
    upstream_authority_drift_findings = _detect_authority_drift_p107(normalized_p107)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    review_packet_complete_candidates = candidate_lists["review_packet_complete_candidates"]

    candidate_decision_statuses: list[dict[str, Any]] = []
    approved_for_future_canary_plan_candidates: list[str] = []
    held_for_review_candidates: list[str] = []
    repair_requested_candidates: list[str] = []
    rejected_by_decision_candidates: list[str] = []
    missing_decision_requirements: dict[str, list[str]] = {}
    observation_authority_drift_findings: list[str] = []

    if not not_computable_reasons and not upstream_authority_drift_findings:
        for candidate_id in review_packet_complete_candidates:
            observation = _get_candidate_observation(decision_observations_packet, candidate_id)
            status, authority_findings, approved_with_required_evidence = (
                _build_candidate_decision_status(candidate_id, observation)
            )
            candidate_decision_statuses.append(status)
            observation_authority_drift_findings.extend(authority_findings)

            missing = status["missing_decision_requirements"]
            if isinstance(missing, list) and missing:
                missing_decision_requirements[candidate_id] = list(missing)

            decision_status = status["canary_decision_status"]
            if decision_status == "CANARY_DECISION_APPROVED_FOR_FUTURE_PLAN":
                approved_for_future_canary_plan_candidates.append(candidate_id)
            elif decision_status == "CANARY_DECISION_REPAIR_REQUESTED":
                repair_requested_candidates.append(candidate_id)
            elif decision_status == "CANARY_DECISION_REJECTED":
                rejected_by_decision_candidates.append(candidate_id)
            else:
                held_for_review_candidates.append(candidate_id)

            if (
                status.get("decision") == "approve_for_future_canary_plan"
                and not approved_with_required_evidence
                and "approve_missing_required_evidence" not in missing_decision_requirements.get(candidate_id, [])
            ):
                missing_decision_requirements.setdefault(candidate_id, []).append(
                    "approve_missing_required_evidence"
                )
                existing_missing = status.get("missing_decision_requirements")
                if isinstance(existing_missing, list):
                    status["missing_decision_requirements"] = sorted(
                        set(existing_missing + ["approve_missing_required_evidence"])
                    )

    all_authority_drift = sorted(
        set(upstream_authority_drift_findings + observation_authority_drift_findings)
    )

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        canary_decision_record_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P107 or decision observations report authority drift or forbidden authority "
            "intent; P108 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not not_computable_reasons:
        status = "CANARY_DECISION_RECORD_EMITTED"
        canary_decision_record_status = "EMITTED"
        all_candidates_approved_for_future_plan = (
            len(review_packet_complete_candidates) > 0
            and len(approved_for_future_canary_plan_candidates)
            == len(review_packet_complete_candidates)
            and not missing_decision_requirements
        )

        if all_candidates_approved_for_future_plan:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_APPROVE
            recommended_next_lane_reason = (
                "Every analyzed candidate is approved for future canary planning with "
                "required decision evidence and no authority drift; proceed to advisory "
                "P109 plan draft."
            )
        else:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates are held, repair-requested, rejected, "
                "or missing required decision evidence; continue P108 decision record."
            )
    else:
        status = "NOT_COMPUTABLE"
        canary_decision_record_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P107 is missing, malformed, non-pass/non-emitted, structurally invalid, "
            "wrong-chain, or lacks review_packet_complete_candidates; P108 cannot compute."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_canary_review_packet_status": (
            normalized_p107.get("status") if isinstance(normalized_p107, dict) else None
        ),
        "canary_decision_record_status": canary_decision_record_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": review_packet_complete_candidates,
        "approved_for_future_canary_plan_candidates": approved_for_future_canary_plan_candidates,
        "held_for_review_candidates": held_for_review_candidates,
        "repair_requested_candidates": repair_requested_candidates,
        "rejected_by_decision_candidates": rejected_by_decision_candidates,
        "candidate_decision_statuses": candidate_decision_statuses,
        "allowed_decisions": list(ALLOWED_DECISIONS),
        "forbidden_decisions": list(FORBIDDEN_DECISIONS),
        "missing_decision_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_decision_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p107_research_canary_review_packet",
            "mapping_method": "deterministic_canary_decision_record",
            "required_decision_observation_fields": list(
                REQUIRED_DECISION_OBSERVATION_FIELDS
            ),
            "boundary_rules": [
                "canary_decision_record_is_not_canary_activation",
                "canary_decision_record_is_not_implementation_authority",
                "canary_decision_record_is_not_canon_promotion",
                "canary_decision_record_is_not_production_activation",
                "canary_decision_record_is_not_runtime_mutation",
                "canary_decision_record_is_not_scheduler_authority",
                "canary_decision_record_is_not_forecast_weight_authority",
                "canary_decision_record_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p109_only_when_every_analyzed_candidate_is_"
                "approve_for_future_canary_plan_with_required_evidence_and_no_authority_drift"
            ),
            "p107_status": (
                normalized_p107.get("status") if isinstance(normalized_p107, dict) else None
            ),
            "p107_artifact_type": (
                normalized_p107.get("artifact_type")
                if isinstance(normalized_p107, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_decision_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
