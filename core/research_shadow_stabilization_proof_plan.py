from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchShadowStabilizationProofPlan.v1"
LANE_ID = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"
UPSTREAM_ARTIFACT_TYPE = "ResearchDerivedSubsystemCandidateLedger.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER_REGENERATION"

EXPECTED_CANDIDATE_IDS: tuple[str, str] = (
    "DROP006_INTENT_GRAPH_BEHAVIORAL_LOGIC_CANDIDATE",
    "DROP007_SITUATION_RUNTIME_PROACTIVE_COORDINATION_CANDIDATE",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "projection_only": True,
        "planning_only": True,
        "evidence_only": True,
        "proof_only": True,
        "shadow_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "forecast_influence": False,
        "execution_authority": False,
        "repair_execution_authority": False,
        "regeneration_execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "canonical_status": CANONICAL_STATUS,
    }


def _validate_p97_packet(p97_packet: Any) -> tuple[list[str], list[dict[str, Any]]]:
    if p97_packet is None:
        return ["p97_artifact_missing"], []
    if not isinstance(p97_packet, dict):
        return ["p97_artifact_malformed:not_a_dict"], []

    blockers: list[str] = []
    if p97_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p97_packet.get('lane_id')!r}")
    if p97_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p97_packet.get('artifact_type')!r}")
    if p97_packet.get("candidate_ledger_status") != "PASS":
        blockers.append(f"candidate_ledger_status_not_pass:{p97_packet.get('candidate_ledger_status')!r}")
    if p97_packet.get("candidates_ready") is not True:
        blockers.append(f"candidates_ready_not_true:{p97_packet.get('candidates_ready')!r}")

    candidates = p97_packet.get("derived_candidates")
    if not isinstance(candidates, list):
        blockers.append("derived_candidates_malformed:not_a_list")
        return blockers, []

    observed_ids: list[str] = []
    for candidate in candidates:
        if isinstance(candidate, dict) and isinstance(candidate.get("candidate_id"), str):
            observed_ids.append(candidate["candidate_id"])
        else:
            observed_ids.append(str(candidate))
    if sorted(observed_ids) != sorted(EXPECTED_CANDIDATE_IDS):
        blockers.append(f"candidate_ids_mismatch:{observed_ids!r}")

    return blockers, candidates


def _build_proof_records(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        records.append(
            {
                "proof_id": candidate_id.replace("_CANDIDATE", "_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"),
                "candidate_id": candidate_id,
                "source_surface_id": str(candidate.get("source_surface_id")),
                "research_fold_family": str(candidate.get("research_fold_family")),
                "stabilization_scope": "advisory_shadow_stabilization_proof_only",
                "required_proofs": [
                    "shadow_only_boundary_confirmed",
                    "no_forecast_influence",
                    "no_runtime_authority",
                    "no_scheduler_mutation",
                    "candidate_shape_deterministic",
                    "candidate_governance_non_operative",
                ],
                "expected_evidence": [
                    "candidate_id",
                    "authority_locks",
                    "governance_posture",
                    "deterministic_candidate_ordering",
                ],
                "status": "PLANNED",
            }
        )
    return sorted(records, key=lambda item: str(item["proof_id"]))


def build_research_shadow_stabilization_proof_plan(
    *, p97_packet: dict[str, Any] | None = None
) -> dict[str, Any]:
    blockers, candidates = _validate_p97_packet(p97_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        records: list[dict[str, Any]] = []
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
    else:
        status = "PASS"
        ready = True
        records = _build_proof_records(candidates)
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "stabilization_proof_plan_status": status,
        "stabilization_proof_plan_ready": ready,
        "stabilization_proof_records": records,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p97_research_derived_subsystem_candidate_ledger",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "expected_candidate_ids": list(EXPECTED_CANDIDATE_IDS),
            "deterministic_ordering": "proof_id_ascending",
        },
        "recommended_next_lane": next_lane,
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_shadow_stabilization_proof_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
