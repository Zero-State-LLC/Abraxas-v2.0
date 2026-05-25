from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchStabilizationWindowMonitor.v1"
LANE_ID = "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT"
REQUIRED_P101_ARTIFACT_TYPE = "ResearchShadowStabilizationReceipt.v1"
REQUIRED_P101_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P103_RESEARCH_SHADOW_REPLAY_AUDIT"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR_CONTINUE"

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
)

REQUIRED_PROOF_FLAGS: tuple[str, ...] = (
    "authority_lock_invariance_observed",
    "deterministic_replay_observed",
    "not_computable_failure_proof_observed",
    "aal_viz_projection_only_observed",
    "operator_review_observed",
    "no_runtime_mutation_observed",
    "no_canon_promotion_observed",
    "no_forecast_weight_mutation_observed",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _validate_candidate_list(
    packet: dict[str, Any], field_name: str, reasons: list[str]
) -> list[str]:
    value = packet.get(field_name)
    if not isinstance(value, list):
        reasons.append(f"p101_{field_name}_malformed")
        return []
    normalized: list[str] = []
    for candidate in value:
        if not isinstance(candidate, str):
            reasons.append(f"p101_{field_name}_entry_malformed")
            continue
        normalized.append(candidate)
    return normalized


def _validate_p101_packet(p101_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p101_packet is None:
        return ["p101_packet_missing"], None
    if not isinstance(p101_packet, dict):
        return ["p101_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p101_packet.get("artifact_type") != REQUIRED_P101_ARTIFACT_TYPE:
        reasons.append(
            f"p101_artifact_type_mismatch:{p101_packet.get('artifact_type')!r}"
        )
    if p101_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p101_lane_id_mismatch:{p101_packet.get('lane_id')!r}")
    if p101_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p101_canonical_status_mismatch:{p101_packet.get('canonical_status')!r}"
        )
    if p101_packet.get("advisory_only") is not True:
        reasons.append("p101_advisory_only_not_true")
    if p101_packet.get("projection_only") is not True:
        reasons.append("p101_projection_only_not_true")

    p101_status = p101_packet.get("status")
    p101_receipt_status = p101_packet.get("stabilization_receipt_status")
    valid_emitted_status = (
        p101_status == "SHADOW_STABILIZATION_RECEIPT_EMITTED"
        and p101_receipt_status == "EMITTED"
    )
    valid_rejected_drift_status = (
        p101_status == "REJECTED_AUTHORITY_DRIFT"
        and p101_receipt_status == "REJECTED_AUTHORITY_DRIFT"
    )

    if not (valid_emitted_status or valid_rejected_drift_status):
        reasons.append(f"p101_status_not_emitted_or_rejected_drift:{p101_status!r}")
        reasons.append(
            "p101_stabilization_receipt_status_not_emitted_or_rejected_drift:"
            f"{p101_receipt_status!r}"
        )

    if valid_emitted_status:
        if p101_packet.get("recommended_next_lane") != REQUIRED_P101_RECOMMENDATION:
            reasons.append(
                "p101_recommendation_chain_mismatch:"
                f"{p101_packet.get('recommended_next_lane')!r}"
            )

    stabilization_window_requirements = p101_packet.get(
        "stabilization_window_requirements"
    )
    if not isinstance(stabilization_window_requirements, dict):
        reasons.append("p101_stabilization_window_requirements_malformed")
    else:
        minimum_cycles = stabilization_window_requirements.get(
            "minimum_shadow_cycles_required"
        )
        if not isinstance(minimum_cycles, int):
            reasons.append("p101_minimum_shadow_cycles_required_malformed")

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        _validate_candidate_list(p101_packet, field_name, reasons)

    authority_locks = p101_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p101_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p101_authority_lock_missing:{key}")

    return sorted(set(reasons)), p101_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
        }

    out: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        value = packet.get(field_name)
        out[field_name] = [v for v in value if isinstance(v, str)] if isinstance(value, list) else []
    return out


def _detect_authority_drift(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p101_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p101_authority_lock_drift:{key}")

    return sorted(set(findings))


def _get_candidate_observation(
    observations_packet: dict[str, Any] | None, candidate_id: str
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_window_statuses(
    *,
    stabilized_candidates: list[str],
    minimum_shadow_cycles_required: int,
    observations_packet: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[str], list[str], dict[str, list[str]], bool]:
    statuses: list[dict[str, Any]] = []
    complete: list[str] = []
    incomplete: list[str] = []
    missing_proof_flags: dict[str, list[str]] = {}

    all_complete_with_proofs = True

    for candidate_id in stabilized_candidates:
        observation = _get_candidate_observation(observations_packet, candidate_id)

        cycles_raw = observation.get("current_shadow_cycles_observed")
        if isinstance(cycles_raw, int) and cycles_raw >= 0:
            current_shadow_cycles_observed = cycles_raw
        else:
            current_shadow_cycles_observed = 0

        raw_proof_flags = observation.get("proof_flags")
        proof_flags = {
            flag: bool(raw_proof_flags.get(flag) is True)
            if isinstance(raw_proof_flags, dict)
            else False
            for flag in REQUIRED_PROOF_FLAGS
        }

        missing_flags = sorted(
            [flag for flag in REQUIRED_PROOF_FLAGS if proof_flags[flag] is not True]
        )
        cycle_requirement_satisfied = (
            current_shadow_cycles_observed >= minimum_shadow_cycles_required
        )

        if missing_flags:
            stabilization_window_status = "WINDOW_BLOCKED_MISSING_PROOFS"
        elif cycle_requirement_satisfied:
            stabilization_window_status = "WINDOW_COMPLETE"
        elif current_shadow_cycles_observed == 0:
            stabilization_window_status = "WINDOW_NOT_STARTED"
        else:
            stabilization_window_status = "WINDOW_IN_PROGRESS"

        candidate_status = {
            "candidate_id": candidate_id,
            "current_shadow_cycles_observed": current_shadow_cycles_observed,
            "minimum_shadow_cycles_required": minimum_shadow_cycles_required,
            "cycle_requirement_satisfied": cycle_requirement_satisfied,
            "proof_flags": proof_flags,
            "missing_proof_flags": missing_flags,
            "stabilization_window_status": stabilization_window_status,
        }
        statuses.append(candidate_status)

        if missing_flags:
            missing_proof_flags[candidate_id] = missing_flags

        if cycle_requirement_satisfied and not missing_flags:
            complete.append(candidate_id)
        else:
            incomplete.append(candidate_id)
            all_complete_with_proofs = False

    return statuses, complete, incomplete, missing_proof_flags, all_complete_with_proofs


def build_research_stabilization_window_monitor(
    *,
    p101_packet: dict[str, Any] | None = None,
    observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p101 = _validate_p101_packet(p101_packet)
    candidate_lists = _extract_candidate_lists(normalized_p101)
    authority_drift_findings = _detect_authority_drift(normalized_p101)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]

    minimum_shadow_cycles_required = 0
    if isinstance(normalized_p101, dict):
        requirements = normalized_p101.get("stabilization_window_requirements")
        if isinstance(requirements, dict):
            raw_minimum = requirements.get("minimum_shadow_cycles_required")
            if isinstance(raw_minimum, int):
                minimum_shadow_cycles_required = raw_minimum

    if not not_computable_reasons and not stabilized_candidates:
        not_computable_reasons = ["p101_no_stabilized_candidates"]

    candidate_window_statuses: list[dict[str, Any]] = []
    window_complete_candidates: list[str] = []
    window_incomplete_candidates: list[str] = []
    missing_proof_flags: dict[str, list[str]] = {}

    if not not_computable_reasons and not authority_drift_findings:
        (
            candidate_window_statuses,
            window_complete_candidates,
            window_incomplete_candidates,
            missing_proof_flags,
            all_complete_with_proofs,
        ) = _build_candidate_window_statuses(
            stabilized_candidates=stabilized_candidates,
            minimum_shadow_cycles_required=minimum_shadow_cycles_required,
            observations_packet=observations_packet,
        )
    else:
        all_complete_with_proofs = False

    if authority_drift_findings:
        status = "REJECTED_AUTHORITY_DRIFT"
        stabilization_window_monitor_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P101 reports authority drift or lock drift; P102 remains advisory-only and "
            "cannot advance while any authority drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        stabilization_window_monitor_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P101 is missing, malformed, non-emitted, wrong-chain, structurally invalid, "
            "or has no stabilized candidates; P102 cannot compute stabilization-window status."
        )
    elif all_complete_with_proofs:
        status = "STABILIZATION_WINDOW_MONITOR_EMITTED"
        stabilization_window_monitor_status = "EMITTED"
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
        recommended_next_lane_reason = (
            "All stabilized candidates satisfy minimum shadow cycles and required proof "
            "flags; proceed to P103 research shadow replay audit."
        )
    else:
        status = "STABILIZATION_WINDOW_MONITOR_EMITTED"
        stabilization_window_monitor_status = "EMITTED"
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
        recommended_next_lane_reason = (
            "One or more stabilized candidates have incomplete cycles or missing proof "
            "flags; continue deterministic P102 stabilization-window monitoring."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_stabilization_receipt_status": (
            normalized_p101.get("status") if isinstance(normalized_p101, dict) else None
        ),
        "stabilization_window_monitor_status": stabilization_window_monitor_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "minimum_shadow_cycles_required": minimum_shadow_cycles_required,
        "candidate_window_statuses": candidate_window_statuses,
        "window_complete_candidates": window_complete_candidates,
        "window_incomplete_candidates": window_incomplete_candidates,
        "missing_proof_flags": missing_proof_flags,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p101_research_shadow_stabilization_receipt",
            "mapping_method": "deterministic_stabilization_window_monitor",
            "required_proof_flags": list(REQUIRED_PROOF_FLAGS),
            "boundary_rules": [
                "stabilization_window_monitor_is_observation_only",
                "stabilization_window_monitor_is_not_implementation_authority",
                "stabilization_window_monitor_is_not_canon_promotion",
                "stabilization_window_monitor_is_not_production_activation",
                "stabilization_window_monitor_is_not_runtime_mutation",
                "stabilization_window_monitor_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p103_only_when_every_stabilized_candidate_meets_cycle_requirement_and_all_required_proof_flags"
            ),
            "p101_status": (
                normalized_p101.get("status") if isinstance(normalized_p101, dict) else None
            ),
            "p101_artifact_type": (
                normalized_p101.get("artifact_type")
                if isinstance(normalized_p101, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_stabilization_window_monitor(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
