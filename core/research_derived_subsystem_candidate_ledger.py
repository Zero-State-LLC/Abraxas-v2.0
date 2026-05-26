from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchDerivedSubsystemCandidateLedger.v1"
LANE_ID = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P96_RESEARCH_FOLD_VALIDATION_PLAN"
UPSTREAM_ARTIFACT_TYPE = "ResearchFoldValidationPlan.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P96_RESEARCH_FOLD_VALIDATION_PLAN_REGENERATION"

EXPECTED_VALIDATION_IDS: tuple[str, str] = (
    "DROP006_RESEARCH_FOLD_VALIDATION_PLAN",
    "DROP007_RESEARCH_FOLD_VALIDATION_PLAN",
)

_CANDIDATES_BY_VALIDATION_ID: dict[str, dict[str, str]] = {
    "DROP006_RESEARCH_FOLD_VALIDATION_PLAN": {
        "candidate_id": "DROP006_INTENT_GRAPH_BEHAVIORAL_LOGIC_CANDIDATE",
        "proposed_subsystem_name": "intent_graph_behavioral_logic_layer",
    },
    "DROP007_RESEARCH_FOLD_VALIDATION_PLAN": {
        "candidate_id": "DROP007_SITUATION_RUNTIME_PROACTIVE_COORDINATION_CANDIDATE",
        "proposed_subsystem_name": "situation_runtime_proactive_coordination_layer",
    },
}


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
        "candidate_only": True,
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


def _validate_p96_packet(p96_packet: Any) -> tuple[list[str], list[dict[str, Any]]]:
    if p96_packet is None:
        return ["p96_artifact_missing"], []
    if not isinstance(p96_packet, dict):
        return ["p96_artifact_malformed:not_a_dict"], []

    blockers: list[str] = []
    if p96_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p96_packet.get('lane_id')!r}")
    if p96_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p96_packet.get('artifact_type')!r}")
    if p96_packet.get("validation_plan_status") != "PASS":
        blockers.append(f"validation_plan_status_not_pass:{p96_packet.get('validation_plan_status')!r}")
    if p96_packet.get("validation_plan_ready") is not True:
        blockers.append(f"validation_plan_ready_not_true:{p96_packet.get('validation_plan_ready')!r}")

    validation_records = p96_packet.get("validation_records")
    if not isinstance(validation_records, list):
        blockers.append("validation_records_malformed:not_a_list")
        return blockers, []

    observed_ids: list[str] = []
    for record in validation_records:
        if isinstance(record, dict) and isinstance(record.get("validation_id"), str):
            observed_ids.append(record["validation_id"])
        else:
            observed_ids.append(str(record))
    if sorted(observed_ids) != sorted(EXPECTED_VALIDATION_IDS):
        blockers.append(f"validation_ids_mismatch:{observed_ids!r}")

    return blockers, validation_records


def _build_derived_candidates(validation_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for record in validation_records:
        validation_id = str(record["validation_id"])
        candidate_seed = _CANDIDATES_BY_VALIDATION_ID[validation_id]
        candidates.append(
            {
                "candidate_id": candidate_seed["candidate_id"],
                "source_validation_id": validation_id,
                "source_spec_id": str(record.get("spec_id")),
                "source_surface_id": str(record.get("source_surface_id")),
                "research_fold_family": str(record.get("research_fold_family")),
                "proposed_subsystem_name": candidate_seed["proposed_subsystem_name"],
                "subsystem_scope": "advisory_shadow_research_candidate_only",
                "candidate_status": "CANDIDATE_ONLY",
                "governance_posture": "ADVISORY_ONLY",
                "authority_class": "NON_OPERATIVE",
            }
        )
    return sorted(candidates, key=lambda item: str(item["candidate_id"]))


def build_research_derived_subsystem_candidate_ledger(
    *,
    p96_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers, validation_records = _validate_p96_packet(p96_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        derived_candidates: list[dict[str, Any]] = []
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
    else:
        status = "PASS"
        ready = True
        derived_candidates = _build_derived_candidates(validation_records)
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "candidate_ledger_status": status,
        "candidates_ready": ready,
        "derived_candidates": derived_candidates,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p96_research_fold_validation_plan",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "expected_validation_ids": list(EXPECTED_VALIDATION_IDS),
            "deterministic_ordering": "candidate_id_ascending",
        },
        "recommended_next_lane": next_lane,
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_derived_subsystem_candidate_ledger(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
