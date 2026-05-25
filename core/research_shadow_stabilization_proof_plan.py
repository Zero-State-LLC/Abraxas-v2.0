from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchShadowStabilizationProofPlan.v1"
LANE_ID = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"
RECOMMENDED_NEXT_LANE_ON_PASS = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"

REQUIRED_P97_ARTIFACT_TYPE = "ResearchDerivedSubsystemCandidateLedger.v1"
REQUIRED_P97_RECOMMENDATION = LANE_ID

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

REQUIRED_DROP_IDS: tuple[str, ...] = ("DROP006", "DROP007")

REQUIRED_PROOFS: tuple[str, ...] = (
    "12-run invariance proof required",
    "authority-lock invariance proof required",
    "NOT_COMPUTABLE failure proof required",
    "AAL-Viz projection-only proof required",
    "cross-drop conflict scan required",
    "operator review hold required",
)


def _validate_p97_packet(p97_packet: Any) -> list[str]:
    if p97_packet is None:
        return ["p97_packet_missing"]
    if not isinstance(p97_packet, dict):
        return ["p97_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    if p97_packet.get("artifact_type") != REQUIRED_P97_ARTIFACT_TYPE:
        reasons.append(f"p97_artifact_type_mismatch:{p97_packet.get('artifact_type')!r}")
    if p97_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p97_lane_id_mismatch:{p97_packet.get('lane_id')!r}")
    if p97_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p97_canonical_status_mismatch:{p97_packet.get('canonical_status')!r}"
        )
    if p97_packet.get("advisory_only") is not True:
        reasons.append("p97_advisory_only_not_true")
    if p97_packet.get("projection_only") is not True:
        reasons.append("p97_projection_only_not_true")

    p97_status = p97_packet.get("status")
    if p97_status != "PASS":
        reasons.append(f"p97_status_not_pass:{p97_status!r}")
    elif p97_packet.get("recommended_next_lane") != REQUIRED_P97_RECOMMENDATION:
        reasons.append(
            "p97_recommended_next_lane_invalid:"
            f"{p97_packet.get('recommended_next_lane')!r}"
        )

    if not isinstance(p97_packet.get("subsystem_candidates"), list):
        reasons.append("p97_subsystem_candidates_malformed")

    structured_fields: tuple[tuple[str, type[Any]], ...] = (
        ("target_subsystems", list),
        ("stabilization_requirements", list),
        ("provenance", dict),
    )
    for field_name, expected_type in structured_fields:
        if not isinstance(p97_packet.get(field_name), expected_type):
            reasons.append(f"p97_{field_name}_malformed")

    authority_locks = p97_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p97_authority_locks_malformed")
    else:
        drifted = [
            key
            for key in AUTHORITY_LOCK_KEYS
            if authority_locks.get(key) is not False
        ]
        if drifted:
            reasons.append(f"p97_authority_drift_detected:{sorted(drifted)!r}")

    drop_ids: set[str] = set()
    candidate_ids: set[str] = set()
    for candidate in p97_packet.get("subsystem_candidates", []):
        if not isinstance(candidate, dict):
            reasons.append("p97_subsystem_candidate_entry_malformed")
            continue
        drop_id = candidate.get("drop_id")
        candidate_id = candidate.get("candidate_id")
        if not isinstance(drop_id, str) or not isinstance(candidate_id, str):
            reasons.append("p97_subsystem_candidate_identity_malformed")
            continue
        drop_ids.add(drop_id)
        candidate_ids.add(candidate_id)

    missing_drops = sorted(set(REQUIRED_DROP_IDS) - drop_ids)
    if missing_drops:
        reasons.append(f"p97_required_drop_candidates_missing:{missing_drops!r}")

    if len(candidate_ids) != len(
        [
            candidate
            for candidate in p97_packet.get("subsystem_candidates", [])
            if isinstance(candidate, dict)
        ]
    ):
        reasons.append("p97_duplicate_or_malformed_candidate_entries")

    return reasons


def _build_stabilization_proof_requirements(
    p97_packet: dict[str, Any],
) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for candidate in p97_packet["subsystem_candidates"]:
        if not isinstance(candidate, dict):
            continue
        drop_id = candidate.get("drop_id")
        candidate_id = candidate.get("candidate_id")
        if drop_id not in REQUIRED_DROP_IDS:
            continue
        if not isinstance(candidate_id, str):
            continue
        requirements.append(
            {
                "drop_id": drop_id,
                "candidate_id": candidate_id,
                "proof_requirements": list(REQUIRED_PROOFS),
                "stabilization_execution": "PROHIBITED_IN_P98",
            }
        )

    return sorted(requirements, key=lambda item: (item["drop_id"], item["candidate_id"]))


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def build_research_shadow_stabilization_proof_plan(
    *,
    p97_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons = _validate_p97_packet(p97_packet)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        stabilization_proof_plan_status = "NOT_COMPUTABLE"
        stabilization_proof_requirements: list[dict[str, Any]] = []
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P97 upstream candidate ledger is missing, malformed, non-pass, structurally "
            "invalid, or contains authority drift; stabilization proof planning cannot proceed."
        )
    else:
        status = "PASS"
        stabilization_proof_plan_status = "READY"
        stabilization_proof_requirements = _build_stabilization_proof_requirements(p97_packet)
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
        recommended_next_lane_reason = (
            "P98 stabilization proof planning is deterministic, advisory-only, and projection-only; "
            "proceed to P99 research cross-drop conflict scan."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_candidate_ledger_status": (
            p97_packet.get("status") if isinstance(p97_packet, dict) else None
        ),
        "stabilization_proof_plan_status": stabilization_proof_plan_status,
        "stabilization_proof_requirements": stabilization_proof_requirements,
        "global_proof_requirements": list(REQUIRED_PROOFS),
        "cross_drop_conflict_scan_required": True,
        "operator_review_hold_required": True,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p97_research_derived_subsystem_candidate_ledger",
            "mapping_method": "deterministic_shadow_stabilization_proof_planning",
            "required_drop_ids": list(REQUIRED_DROP_IDS),
            "candidate_ordering": "drop_order_then_lexicographic_candidate_id",
            "p97_status": p97_packet.get("status") if isinstance(p97_packet, dict) else None,
            "p97_artifact_type": (
                p97_packet.get("artifact_type") if isinstance(p97_packet, dict) else None
            ),
            "advisory_boundary": "proof_planning_only_no_stabilization_or_promotion",
            "gated_recommendation_rule": "recommend_p99_only_when_status_pass",
        },
    }
    return _finalize(packet_base)


def write_research_shadow_stabilization_proof_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
