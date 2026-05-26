from __future__ import annotations

# ---------------------------------------------------------------------------
# Self-audit notes
# ---------------------------------------------------------------------------
# P120 is advisory-only and projection-only.
# It does NOT execute rollback or termination.
# It does NOT grant rollback/termination/runtime/canary authority.
# It does NOT mutate runtime, scheduler, baseline, forecast, or canon.
# It does NOT implement P121.

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchCanaryRollbackTerminationGovernance.v1"
LANE_ID = "P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD"
REQUIRED_P119_ARTIFACT_TYPE = "ResearchCanaryRuntimeObservationRecord.v1"
REQUIRED_P119_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = (
    "P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE_CONTINUE"
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

REQUIRED_GOVERNANCE_OBSERVATION_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "runtime_observation_complete_observed",
    "rollback_condition_defined",
    "rollback_procedure_documented",
    "termination_condition_defined",
    "termination_procedure_documented",
    "rollback_authority_withheld_confirmed",
    "termination_authority_withheld_confirmed",
    "operator_go_no_go_required",
    "provenance_bundle_attached",
    "authority_drift_observed",
    "notes",
)

GOVERNANCE_COMPLETENESS_FIELDS: tuple[str, ...] = (
    "runtime_observation_complete_observed",
    "rollback_condition_defined",
    "rollback_procedure_documented",
    "termination_condition_defined",
    "termination_procedure_documented",
    "rollback_authority_withheld_confirmed",
    "termination_authority_withheld_confirmed",
    "operator_go_no_go_required",
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


def _validate_p119_packet(p119_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p119_packet is None:
        return ["p119_packet_missing"], None
    if not isinstance(p119_packet, dict):
        return ["p119_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p119_packet.get("artifact_type") != REQUIRED_P119_ARTIFACT_TYPE:
        reasons.append(
            f"p119_artifact_type_mismatch:{p119_packet.get('artifact_type')!r}"
        )
    if p119_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p119_lane_id_mismatch:{p119_packet.get('lane_id')!r}")
    if p119_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p119_canonical_status_mismatch:{p119_packet.get('canonical_status')!r}"
        )
    if p119_packet.get("advisory_only") is not True:
        reasons.append("p119_advisory_only_not_true")
    if p119_packet.get("projection_only") is not True:
        reasons.append("p119_projection_only_not_true")

    if p119_packet.get("status") != "CANARY_RUNTIME_OBSERVATION_RECORD_EMITTED":
        reasons.append(f"p119_status_not_emitted:{p119_packet.get('status')!r}")
    if p119_packet.get("lane_status") != "CANARY_RUNTIME_OBSERVATION_COMPLETE":
        reasons.append(f"p119_status_not_pass:{p119_packet.get('lane_status')!r}")

    if p119_packet.get("recommended_next_lane") != REQUIRED_P119_RECOMMENDATION:
        reasons.append(
            "p119_recommendation_chain_mismatch:"
            f"{p119_packet.get('recommended_next_lane')!r}"
        )

    analyzed_candidates = p119_packet.get("runtime_observation_complete_candidates")
    if not isinstance(analyzed_candidates, list):
        reasons.append("p119_runtime_observation_complete_candidates_malformed")
    elif not analyzed_candidates:
        reasons.append("p119_no_candidates_for_p120")
    elif any(not isinstance(candidate, str) for candidate in analyzed_candidates):
        reasons.append("p119_candidate_entry_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = p119_packet.get(field_name)
        if not isinstance(value, list):
            reasons.append(f"p119_{field_name}_malformed")
        elif any(not isinstance(candidate, str) for candidate in value):
            reasons.append(f"p119_{field_name}_entry_malformed")

    return sorted(set(reasons)), p119_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "runtime_observation_complete_candidates": [],
        }

    extracted: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "runtime_observation_complete_candidates",
    ):
        extracted[field_name] = _normalize_string_list(packet.get(field_name))
    return extracted


def _detect_authority_drift_p119(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p119_reports_authority_drift")

    if packet.get("lane_status") == "CANARY_RUNTIME_OBSERVATION_REJECTED_AUTHORITY_DRIFT":
        findings.append("p119_lane_status_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key, value in sorted(authority_locks.items()):
            if value is not False:
                findings.append(f"p119_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None,
    candidate_id: str,
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_rollback_termination_observations")
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
            "runtime_observation_complete_observed": False,
            "rollback_condition_defined": False,
            "rollback_procedure_documented": False,
            "termination_condition_defined": False,
            "termination_procedure_documented": False,
            "rollback_authority_withheld_confirmed": False,
            "termination_authority_withheld_confirmed": False,
            "operator_go_no_go_required": False,
            "provenance_bundle_attached": False,
            "authority_drift_observed": False,
            "missing_requirements": ["rollback_termination_observations_missing"],
            "canary_rollback_termination_governance_status": (
                "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_INCOMPLETE"
            ),
        }
        return status, []

    notes = observation.get("notes") if isinstance(observation.get("notes"), str) else ""
    candidate_id_observed = observation.get("candidate_id")

    criteria: dict[str, bool] = {}
    for field in GOVERNANCE_COMPLETENESS_FIELDS:
        criteria[field] = _to_bool_or_none(observation.get(field)) is True

    authority_drift_observed = (
        _to_bool_or_none(observation.get("authority_drift_observed")) is True
    )

    missing_requirements: list[str] = []
    authority_findings: list[str] = []

    for field in GOVERNANCE_COMPLETENESS_FIELDS:
        if not criteria[field]:
            missing_requirements.append(f"{field}_not_true")

    if authority_drift_observed:
        missing_requirements.append("authority_drift_observed")
        authority_findings.append(f"candidate_governance_authority_drift:{candidate_id}")

    if authority_findings:
        governance_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_REJECTED_AUTHORITY_DRIFT"
    elif not missing_requirements:
        governance_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_COMPLETE"
    else:
        governance_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_INCOMPLETE"

    status_dict: dict[str, Any] = {
        "candidate_id": candidate_id,
        "runtime_observation_complete_observed": criteria[
            "runtime_observation_complete_observed"
        ],
        "rollback_condition_defined": criteria["rollback_condition_defined"],
        "rollback_procedure_documented": criteria["rollback_procedure_documented"],
        "termination_condition_defined": criteria["termination_condition_defined"],
        "termination_procedure_documented": criteria["termination_procedure_documented"],
        "rollback_authority_withheld_confirmed": criteria[
            "rollback_authority_withheld_confirmed"
        ],
        "termination_authority_withheld_confirmed": criteria[
            "termination_authority_withheld_confirmed"
        ],
        "operator_go_no_go_required": criteria["operator_go_no_go_required"],
        "provenance_bundle_attached": criteria["provenance_bundle_attached"],
        "authority_drift_observed": authority_drift_observed,
        "missing_requirements": sorted(set(missing_requirements)),
        "canary_rollback_termination_governance_status": governance_status,
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

        governance_status = candidate_status[
            "canary_rollback_termination_governance_status"
        ]
        if governance_status == "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_COMPLETE":
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


def build_research_canary_rollback_termination_governance(
    *,
    p119_packet: dict[str, Any] | None = None,
    rollback_termination_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p119 = _validate_p119_packet(p119_packet)
    candidate_lists = _extract_candidate_lists(normalized_p119)
    authority_drift_findings = _detect_authority_drift_p119(normalized_p119)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    analyzed_candidates = candidate_lists["runtime_observation_complete_candidates"]

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
            observations_packet=rollback_termination_observations_packet,
        )

    all_authority_drift = sorted(set(authority_drift_findings + observation_drift_findings))

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        lane_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P119 or governance observations report authority drift or authority lock drift; "
            "P120 remains advisory-only and cannot proceed while drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        lane_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_INCOMPLETE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P119 is missing, malformed, non-pass/non-emitted, wrong-chain, lacks complete "
            "runtime-observation candidates, or does not recommend P120; P120 cannot compute."
        )
    else:
        status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_EMITTED"
        all_complete = (
            len(analyzed_candidates) > 0
            and len(complete_candidates) == len(analyzed_candidates)
            and not missing_requirements
        )

        if all_complete:
            lane_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_COMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
            recommended_next_lane_reason = (
                "Every analyzed candidate has complete rollback/termination governance "
                "observations and no authority drift; advisory planning may recommend P121."
            )
        else:
            lane_status = "CANARY_ROLLBACK_TERMINATION_GOVERNANCE_INCOMPLETE"
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
            recommended_next_lane_reason = (
                "One or more analyzed candidates have incomplete rollback/termination "
                "governance observations; continue P120 governance drafting."
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
            normalized_p119.get("status") if isinstance(normalized_p119, dict) else None
        ),
        "upstream_lane_status": (
            normalized_p119.get("lane_status") if isinstance(normalized_p119, dict) else None
        ),
        "lane_status": lane_status,
        "research_canary_rollback_termination_governance_status": lane_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "analyzed_candidates": analyzed_candidates,
        "rollback_termination_governance_complete_candidates": complete_candidates,
        "rollback_termination_governance_incomplete_candidates": incomplete_candidates,
        "candidate_statuses": candidate_statuses,
        "candidate_rollback_termination_governance_statuses": candidate_statuses,
        "missing_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "missing_rollback_termination_governance_requirements": {
            key: sorted(set(values)) for key, values in sorted(missing_requirements.items())
        },
        "required_rollback_termination_governance_observations": list(
            REQUIRED_GOVERNANCE_OBSERVATION_FIELDS
        ),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p119_research_canary_runtime_observation_record",
            "mapping_method": "deterministic_canary_rollback_termination_governance",
            "required_governance_observation_fields": list(
                REQUIRED_GOVERNANCE_OBSERVATION_FIELDS
            ),
            "governance_completeness_fields": list(GOVERNANCE_COMPLETENESS_FIELDS),
            "boundary_rules": [
                "rollback_termination_governance_is_not_rollback_execution",
                "rollback_termination_governance_is_not_termination_execution",
                "rollback_termination_governance_is_not_runtime_control",
                "rollback_termination_governance_is_not_runtime_mutation",
                "rollback_termination_governance_is_not_scheduler_mutation",
                "rollback_termination_governance_is_not_canary_activation",
                "rollback_termination_governance_is_not_canary_execution",
                "rollback_termination_governance_is_not_forecast_mutation",
                "rollback_termination_governance_is_not_canon_promotion",
                "batch_b_does_not_implement_p121",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p121_only_when_every_analyzed_candidate_has_complete_"
                "rollback_termination_governance_observations_and_no_authority_drift"
            ),
            "p119_status": (
                normalized_p119.get("status") if isinstance(normalized_p119, dict) else None
            ),
            "p119_artifact_type": (
                normalized_p119.get("artifact_type")
                if isinstance(normalized_p119, dict)
                else None
            ),
        },
    }

    return _finalize(packet_base)


def write_research_canary_rollback_termination_governance(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
