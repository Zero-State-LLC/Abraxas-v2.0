from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchShadowReplayAudit.v1"
LANE_ID = "P103_RESEARCH_SHADOW_REPLAY_AUDIT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR"
REQUIRED_P102_ARTIFACT_TYPE = "ResearchStabilizationWindowMonitor.v1"
REQUIRED_P102_RECOMMENDATION = LANE_ID
RECOMMENDED_NEXT_LANE_ON_COMPLETE = "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS"
RECOMMENDED_NEXT_LANE_ON_CONTINUE = "P103_RESEARCH_SHADOW_REPLAY_AUDIT_CONTINUE"
REQUIRED_REPLAY_RUN_COUNT = 12

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

REQUIRED_REPLAY_PROOF_FLAGS: tuple[str, ...] = (
    "authority_lock_invariance_observed",
    "not_computable_replay_observed",
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
        reasons.append(f"p102_{field_name}_malformed")
        return []
    normalized: list[str] = []
    for candidate in value:
        if not isinstance(candidate, str):
            reasons.append(f"p102_{field_name}_entry_malformed")
            continue
        normalized.append(candidate)
    return normalized


def _validate_p102_packet(p102_packet: Any) -> tuple[list[str], dict[str, Any] | None]:
    if p102_packet is None:
        return ["p102_packet_missing"], None
    if not isinstance(p102_packet, dict):
        return ["p102_packet_malformed:not_a_dict"], None

    reasons: list[str] = []

    if p102_packet.get("artifact_type") != REQUIRED_P102_ARTIFACT_TYPE:
        reasons.append(
            f"p102_artifact_type_mismatch:{p102_packet.get('artifact_type')!r}"
        )
    if p102_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p102_lane_id_mismatch:{p102_packet.get('lane_id')!r}")
    if p102_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p102_canonical_status_mismatch:{p102_packet.get('canonical_status')!r}"
        )
    if p102_packet.get("advisory_only") is not True:
        reasons.append("p102_advisory_only_not_true")
    if p102_packet.get("projection_only") is not True:
        reasons.append("p102_projection_only_not_true")

    p102_status = p102_packet.get("status")
    p102_monitor_status = p102_packet.get("stabilization_window_monitor_status")
    valid_emitted_status = (
        p102_status == "STABILIZATION_WINDOW_MONITOR_EMITTED"
        and p102_monitor_status == "EMITTED"
    )
    valid_rejected_drift_status = (
        p102_status == "REJECTED_AUTHORITY_DRIFT"
        and p102_monitor_status == "REJECTED_AUTHORITY_DRIFT"
    )

    if not (valid_emitted_status or valid_rejected_drift_status):
        reasons.append(f"p102_status_not_emitted_or_rejected_drift:{p102_status!r}")
        reasons.append(
            "p102_stabilization_window_monitor_status_not_emitted_or_rejected_drift:"
            f"{p102_monitor_status!r}"
        )

    if valid_emitted_status:
        if p102_packet.get("recommended_next_lane") != REQUIRED_P102_RECOMMENDATION:
            reasons.append(
                "p102_recommendation_chain_mismatch:"
                f"{p102_packet.get('recommended_next_lane')!r}"
            )

    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
    ):
        _validate_candidate_list(p102_packet, field_name, reasons)

    window_complete = p102_packet.get("window_complete_candidates")
    if not isinstance(window_complete, list):
        reasons.append("p102_window_complete_candidates_malformed")

    authority_locks = p102_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p102_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p102_authority_lock_missing:{key}")

    return sorted(set(reasons)), p102_packet


def _extract_candidate_lists(packet: dict[str, Any] | None) -> dict[str, list[str]]:
    if packet is None:
        return {
            "stabilized_candidates": [],
            "held_candidates": [],
            "repair_candidates": [],
            "rejected_candidates": [],
            "window_complete_candidates": [],
        }

    out: dict[str, list[str]] = {}
    for field_name in (
        "stabilized_candidates",
        "held_candidates",
        "repair_candidates",
        "rejected_candidates",
        "window_complete_candidates",
    ):
        value = packet.get(field_name)
        out[field_name] = (
            [v for v in value if isinstance(v, str)] if isinstance(value, list) else []
        )
    return out


def _detect_authority_drift_p102(packet: dict[str, Any] | None) -> list[str]:
    if packet is None:
        return []

    findings: list[str] = []

    if packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p102_reports_authority_drift")

    authority_locks = packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p102_authority_lock_drift:{key}")

    return sorted(set(findings))


def _detect_authority_drift_replay(
    observations_packet: dict[str, Any] | None,
) -> list[str]:
    if not isinstance(observations_packet, dict):
        return []

    findings: list[str] = []
    candidate_observations = observations_packet.get("candidate_replay_observations")
    if not isinstance(candidate_observations, dict):
        return []

    for candidate_id, obs in candidate_observations.items():
        if not isinstance(obs, dict):
            continue
        proof_flags = obs.get("proof_flags")
        if isinstance(proof_flags, dict):
            if proof_flags.get("authority_lock_invariance_observed") is False:
                findings.append(
                    f"replay_authority_lock_drift_candidate:{candidate_id}"
                )
        elif obs.get("authority_lock_invariance_observed") is False:
            findings.append(
                f"replay_authority_lock_drift_candidate:{candidate_id}"
            )

    return sorted(set(findings))


def _get_candidate_replay_observation(
    observations_packet: dict[str, Any] | None, candidate_id: str
) -> dict[str, Any]:
    if not isinstance(observations_packet, dict):
        return {}

    entries = observations_packet.get("candidate_replay_observations")
    if not isinstance(entries, dict):
        return {}

    candidate_observation = entries.get(candidate_id)
    if not isinstance(candidate_observation, dict):
        return {}
    return candidate_observation


def _build_candidate_replay_status(
    candidate_id: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    replay_run_hashes_raw = observation.get("replay_run_hashes")
    if isinstance(replay_run_hashes_raw, list):
        replay_run_hashes = [h for h in replay_run_hashes_raw if isinstance(h, str)]
    else:
        replay_run_hashes = []

    replay_run_count = len(replay_run_hashes)
    count_satisfied = replay_run_count >= REQUIRED_REPLAY_RUN_COUNT

    if replay_run_hashes:
        identical_replay_hashes = len(set(replay_run_hashes)) == 1
    else:
        identical_replay_hashes = False

    raw_proof = observation.get("proof_flags")
    has_explicit_proof_flags = isinstance(raw_proof, dict)

    proof_flags: dict[str, bool] = {
        flag: (raw_proof.get(flag) is True if has_explicit_proof_flags else False)
        for flag in REQUIRED_REPLAY_PROOF_FLAGS
    }

    missing_replay_requirements: list[str] = []

    if replay_run_count == 0:
        shadow_replay_status = "REPLAY_NOT_STARTED"
        replay_requirement_satisfied = False
    elif not count_satisfied:
        shadow_replay_status = "REPLAY_IN_PROGRESS"
        replay_requirement_satisfied = False
        missing_replay_requirements.append("insufficient_replay_run_count")
    elif not identical_replay_hashes:
        shadow_replay_status = "REPLAY_FAIL_HASH_DIVERGENCE"
        replay_requirement_satisfied = False
        missing_replay_requirements.append("replay_hash_divergence")
    else:
        missing_flags = sorted(
            [flag for flag in REQUIRED_REPLAY_PROOF_FLAGS if not proof_flags.get(flag)]
        )
        if missing_flags:
            shadow_replay_status = "REPLAY_BLOCKED_MISSING_PROOFS"
            replay_requirement_satisfied = False
            missing_replay_requirements.extend(missing_flags)
        else:
            shadow_replay_status = "REPLAY_PASS"
            replay_requirement_satisfied = True

    return {
        "candidate_id": candidate_id,
        "replay_run_count": replay_run_count,
        "required_replay_run_count": REQUIRED_REPLAY_RUN_COUNT,
        "replay_run_hashes": replay_run_hashes,
        "identical_replay_hashes": identical_replay_hashes,
        "replay_requirement_satisfied": replay_requirement_satisfied,
        "proof_flags": proof_flags,
        "missing_replay_requirements": missing_replay_requirements,
        "shadow_replay_status": shadow_replay_status,
    }


def _build_candidate_replay_statuses(
    *,
    window_complete_candidates: list[str],
    observations_packet: dict[str, Any] | None,
) -> tuple[
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
    dict[str, list[str]],
    bool,
]:
    statuses: list[dict[str, Any]] = []
    replay_pass: list[str] = []
    replay_fail: list[str] = []
    replay_incomplete: list[str] = []
    missing_replay_requirements: dict[str, list[str]] = {}
    all_pass = True

    for candidate_id in window_complete_candidates:
        observation = _get_candidate_replay_observation(observations_packet, candidate_id)
        status = _build_candidate_replay_status(candidate_id, observation)
        statuses.append(status)

        if status["missing_replay_requirements"]:
            missing_replay_requirements[candidate_id] = status["missing_replay_requirements"]

        sr_status = status["shadow_replay_status"]
        if sr_status == "REPLAY_PASS":
            replay_pass.append(candidate_id)
        elif sr_status in ("REPLAY_FAIL_HASH_DIVERGENCE", "REPLAY_BLOCKED_MISSING_PROOFS"):
            replay_fail.append(candidate_id)
            all_pass = False
        else:
            replay_incomplete.append(candidate_id)
            all_pass = False

    return statuses, replay_pass, replay_fail, replay_incomplete, missing_replay_requirements, all_pass


def build_research_shadow_replay_audit(
    *,
    p102_packet: dict[str, Any] | None = None,
    replay_observations_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons, normalized_p102 = _validate_p102_packet(p102_packet)
    candidate_lists = _extract_candidate_lists(normalized_p102)
    authority_drift_findings = _detect_authority_drift_p102(normalized_p102)

    stabilized_candidates = candidate_lists["stabilized_candidates"]
    held_candidates = candidate_lists["held_candidates"]
    repair_candidates = candidate_lists["repair_candidates"]
    rejected_candidates = candidate_lists["rejected_candidates"]
    window_complete_candidates = candidate_lists["window_complete_candidates"]

    if not not_computable_reasons and not window_complete_candidates:
        not_computable_reasons = ["p102_no_window_complete_candidates"]

    replay_drift_findings: list[str] = []
    if not not_computable_reasons and not authority_drift_findings:
        replay_drift_findings = _detect_authority_drift_replay(replay_observations_packet)

    candidate_replay_statuses: list[dict[str, Any]] = []
    replay_pass_candidates: list[str] = []
    replay_fail_candidates: list[str] = []
    replay_incomplete_candidates: list[str] = []
    missing_replay_requirements: dict[str, list[str]] = {}
    all_pass = False

    if not not_computable_reasons and not authority_drift_findings and not replay_drift_findings:
        (
            candidate_replay_statuses,
            replay_pass_candidates,
            replay_fail_candidates,
            replay_incomplete_candidates,
            missing_replay_requirements,
            all_pass,
        ) = _build_candidate_replay_statuses(
            window_complete_candidates=window_complete_candidates,
            observations_packet=replay_observations_packet,
        )

    all_authority_drift = authority_drift_findings + replay_drift_findings

    if all_authority_drift:
        status = "REJECTED_AUTHORITY_DRIFT"
        shadow_replay_audit_status = "REJECTED_AUTHORITY_DRIFT"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P102 reports authority drift or replay observations indicate authority lock "
            "drift; P103 remains advisory-only and cannot advance while any authority "
            "drift exists."
        )
        not_computable_reasons = []
    elif not_computable_reasons:
        status = "NOT_COMPUTABLE"
        shadow_replay_audit_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P102 is missing, malformed, non-emitted, wrong-chain, structurally invalid, "
            "or has no window_complete_candidates; P103 cannot compute replay audit status."
        )
    elif all_pass and window_complete_candidates:
        status = "SHADOW_REPLAY_AUDIT_EMITTED"
        shadow_replay_audit_status = "EMITTED"
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_COMPLETE
        recommended_next_lane_reason = (
            "All audited candidates satisfy minimum replay run count, identical hashes, "
            "and required proof flags; proceed to P104 research boundary decay analysis."
        )
    else:
        status = "SHADOW_REPLAY_AUDIT_EMITTED"
        shadow_replay_audit_status = "EMITTED"
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_CONTINUE
        recommended_next_lane_reason = (
            "One or more audited candidates have incomplete replay runs, hash divergence, "
            "or missing proof flags; continue deterministic P103 shadow replay audit."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_stabilization_window_monitor_status": (
            normalized_p102.get("status") if isinstance(normalized_p102, dict) else None
        ),
        "shadow_replay_audit_status": shadow_replay_audit_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "audited_candidates": window_complete_candidates,
        "replay_pass_candidates": replay_pass_candidates,
        "replay_fail_candidates": replay_fail_candidates,
        "replay_incomplete_candidates": replay_incomplete_candidates,
        "candidate_replay_statuses": candidate_replay_statuses,
        "missing_replay_requirements": missing_replay_requirements,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p102_research_stabilization_window_monitor",
            "mapping_method": "deterministic_shadow_replay_audit",
            "required_replay_proof_flags": list(REQUIRED_REPLAY_PROOF_FLAGS),
            "required_replay_run_count": REQUIRED_REPLAY_RUN_COUNT,
            "boundary_rules": [
                "shadow_replay_audit_is_observation_only",
                "shadow_replay_audit_is_not_implementation_authority",
                "shadow_replay_audit_is_not_canon_promotion",
                "shadow_replay_audit_is_not_production_activation",
                "shadow_replay_audit_is_not_runtime_mutation",
                "shadow_replay_audit_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p104_only_when_every_audited_candidate_has_at_least_12_identical_replay_hashes_and_all_proof_flags_true"
            ),
            "p102_status": (
                normalized_p102.get("status") if isinstance(normalized_p102, dict) else None
            ),
            "p102_artifact_type": (
                normalized_p102.get("artifact_type")
                if isinstance(normalized_p102, dict)
                else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_shadow_replay_audit(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
