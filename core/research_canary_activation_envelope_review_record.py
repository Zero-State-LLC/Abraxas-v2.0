from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P128 is advisory-only and projection-only.
# It reviews P127 envelope drafts but does NOT activate/execute/authorize canary runtime.
# It does NOT mutate runtime/scheduler/baseline/forecast state or promote canon.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryActivationEnvelopeReviewRecord.v1"
LANE_ID = "P128_RESEARCH_CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT"
REQUIRED_P127_ARTIFACT_TYPE = "ResearchCanaryActivationEnvelopeDraft.v1"
REQUIRED_P127_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = (
    "P129_RESEARCH_CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD"
)
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P128_RESEARCH_CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD_CONTINUE"
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

REQUIRED_ACTIVATION_ENVELOPE_REVIEW_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "activation_envelope_draft_complete_observed",
    "activation_envelope_scope_review_complete",
    "activation_boundary_review_complete",
    "runtime_constraint_review_complete",
    "observation_window_review_complete",
    "rollback_binding_review_complete",
    "termination_binding_review_complete",
    "operator_supervision_review_complete",
    "activation_disabled_review_confirmed",
    "execution_disabled_review_confirmed",
    "runtime_control_disabled_review_confirmed",
    "provenance_review_complete",
    "authority_drift_observed",
    "notes",
)

ACTIVATION_ENVELOPE_REVIEW_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "activation_envelope_draft_complete_observed",
    "activation_envelope_scope_review_complete",
    "activation_boundary_review_complete",
    "runtime_constraint_review_complete",
    "observation_window_review_complete",
    "rollback_binding_review_complete",
    "termination_binding_review_complete",
    "operator_supervision_review_complete",
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


def _validate_p127_packet(p127_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p127_packet is None:
        return ["p127_packet_missing"], None
    if not isinstance(p127_packet, dict):
        return ["p127_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p127_packet.get("artifact_type") != REQUIRED_P127_ARTIFACT_TYPE:
        reasons.append(
            f"p127_artifact_type_mismatch:{p127_packet.get('artifact_type')!r}"
        )
    if p127_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p127_lane_id_mismatch:{p127_packet.get('lane_id')!r}")
    if p127_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p127_canonical_status_mismatch:{p127_packet.get('canonical_status')!r}"
        )
    if p127_packet.get("advisory_only") is not True:
        reasons.append("p127_advisory_only_not_true")
    if p127_packet.get("projection_only") is not True:
        reasons.append("p127_projection_only_not_true")

    p127_status = p127_packet.get("status")
    p127_lane_status = p127_packet.get("lane_status")
    if p127_status != "CANARY_ACTIVATION_ENVELOPE_DRAFT_EMITTED":
        reasons.append(f"p127_status_not_emitted:{p127_status!r}")
    if p127_lane_status != "CANARY_ACTIVATION_ENVELOPE_DRAFT_COMPLETE":
        reasons.append(f"p127_status_not_pass:{p127_lane_status!r}")

    if p127_packet.get("recommended_next_lane") != REQUIRED_P127_RECOMMENDATION:
        reasons.append(
            "p127_recommendation_chain_mismatch:"
            f"{p127_packet.get('recommended_next_lane')!r}"
        )

    analyzed_candidates = p127_packet.get("activation_envelope_draft_complete_candidates")
    if not isinstance(analyzed_candidates, list):
        reasons.append("p127_activation_envelope_draft_complete_candidates_malformed")
    elif not analyzed_candidates:
        reasons.append("p127_no_activation_envelope_draft_complete_candidates")
    elif any(not isinstance(candidate, str) for candidate in analyzed_candidates):
        reasons.append("p127_activation_envelope_draft_complete_candidates_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p127_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p127_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p127_{field_name}_entry_malformed")

    return sorted(set(reasons)), p127_packet


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
            packet.get("activation_envelope_draft_complete_candidates")
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

    entries = observations_packet.get("candidate_activation_envelope_review_observations")
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
            "activation_envelope_draft_complete_observed": False,
            "activation_envelope_scope_review_complete": False,
            "activation_boundary_review_complete": False,
            "runtime_constraint_review_complete": False,
            "observation_window_review_complete": False,
            "rollback_binding_review_complete": False,
            "termination_binding_review_complete": False,
            "operator_supervision_review_complete": False,
            "activation_disabled_review_confirmed": False,
            "execution_disabled_review_confirmed": False,
            "runtime_control_disabled_review_confirmed": False,
            "provenance_review_complete": False,
            "authority_drift_observed": False,
            "missing_requirements": ["activation_envelope_review_observations_missing"],
            "canary_activation_envelope_review_status": (
                "CANARY_ACTIVATION_ENVELOPE_REVIEW_INCOMPLETE"
            ),
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    criteria: dict[str, bool] = {}
    for field in ACTIVATION_ENVELOPE_REVIEW_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in ACTIVATION_ENVELOPE_REVIEW_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(
            f"candidate_activation_envelope_review_authority_drift:{candidate_id}"
        )

    if authority_findings:
        review_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        review_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_COMPLETE"
    else:
        review_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "activation_envelope_draft_complete_observed": criteria[
            "activation_envelope_draft_complete_observed"
        ],
        "activation_envelope_scope_review_complete": criteria[
            "activation_envelope_scope_review_complete"
        ],
        "activation_boundary_review_complete": criteria[
            "activation_boundary_review_complete"
        ],
        "runtime_constraint_review_complete": criteria[
            "runtime_constraint_review_complete"
        ],
        "observation_window_review_complete": criteria[
            "observation_window_review_complete"
        ],
        "rollback_binding_review_complete": criteria[
            "rollback_binding_review_complete"
        ],
        "termination_binding_review_complete": criteria[
            "termination_binding_review_complete"
        ],
        "operator_supervision_review_complete": criteria[
            "operator_supervision_review_complete"
        ],
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
        "canary_activation_envelope_review_status": review_status,
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

        review_status = candidate_status["canary_activation_envelope_review_status"]
        if review_status == "CANARY_ACTIVATION_ENVELOPE_REVIEW_COMPLETE":
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


def build_research_canary_activation_envelope_review_record(
    *,
    p127_packet: dict[str, Any] | None = None,
    activation_envelope_review_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p127 = _validate_p127_packet(p127_packet)
    candidate_lists = _extract_candidate_lists(normalized_p127)
    authority_drift_findings = _detect_authority_drift(normalized_p127, source="p127")

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
            observations_packet=activation_envelope_review_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P127 or activation envelope review observations report authority drift or "
            "authority lock drift; P128 remains advisory-only and cannot proceed while "
            "drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P127 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks "
            "activation_envelope_draft_complete candidates, or does not recommend P128; "
            "P128 cannot compute."
        )
    else:
        status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD_EMITTED"
        all_complete = (
            len(analyzed_candidates) > 0
            and len(complete_candidates) == len(analyzed_candidates)
            and not incomplete_candidates
            and not missing_requirements
        )
        if all_complete:
            lane_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete activation envelope review "
                "observations and no authority drift; advisory flow may recommend P129 "
                "readiness evidence recording."
            )
        else:
            lane_status = "CANARY_ACTIVATION_ENVELOPE_REVIEW_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates have incomplete activation envelope "
                "review observations; continue P128 review recording."
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
            normalized_p127.get("status") if isinstance(normalized_p127, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p127.get("lane_status") if isinstance(normalized_p127, dict) else None
        ),
        "lane_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": analyzed_candidates,
        "activation_envelope_review_complete_candidates": complete_candidates,
        "activation_envelope_review_incomplete_candidates": incomplete_candidates,
        "candidate_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p127_research_canary_activation_envelope_draft",
            "mapping_method": "deterministic_canary_activation_envelope_review_record",
            "required_activation_envelope_review_observation_fields": list(
                REQUIRED_ACTIVATION_ENVELOPE_REVIEW_OBSERVATION_FIELDS
            ),
            "activation_envelope_review_completeness_fields": list(
                ACTIVATION_ENVELOPE_REVIEW_COMPLETENESS_FIELDS
            ),
            "boundary_rules": [
                "p128_activation_envelope_review_is_not_activation_authority",
                "p128_activation_envelope_review_is_not_canary_activation",
                "batch_e_does_not_implement_p130",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p129_only_when_every_analyzed_candidate_has_complete_"
                "activation_envelope_review_observations_and_no_authority_drift"
            ),
            "p127_status": (
                normalized_p127.get("status") if isinstance(normalized_p127, dict) else None
            ),
            "p127_artifact_type": (
                normalized_p127.get("artifact_type")
                if isinstance(normalized_p127, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_activation_envelope_review_record(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
