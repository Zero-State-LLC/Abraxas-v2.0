from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchFoldValidationPlan.v1"
LANE_ID = "P96_RESEARCH_FOLD_VALIDATION_PLAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"
UPSTREAM_ARTIFACT_TYPE = "ResearchFoldDropSpecBuilder.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER_REGENERATION"

EXPECTED_BUILT_SPECS: tuple[str, str] = (
    "DROP006_RESEARCH_FOLD_SPEC",
    "DROP007_RESEARCH_FOLD_SPEC",
)

SOURCE_SURFACES_BY_SPEC: dict[str, str] = {
    "DROP006_RESEARCH_FOLD_SPEC": "canon_drop_006_research_folds",
    "DROP007_RESEARCH_FOLD_SPEC": "canon_drop_007_research_folds",
}

FAMILY_BY_SPEC: dict[str, str] = {
    "DROP006_RESEARCH_FOLD_SPEC": "DROP006",
    "DROP007_RESEARCH_FOLD_SPEC": "DROP007",
}

REQUIRED_CHECKS: tuple[str, ...] = (
    "source_reference_present",
    "content_hash_present",
    "governance_posture_advisory_only",
    "no_operational_authority",
    "deterministic_spec_shape",
)

EXPECTED_EVIDENCE: tuple[str, ...] = (
    "source_surface_id",
    "spec_id",
    "spec_content_hash",
    "authority_locks",
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
        "validation_only": True,
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


def _validate_p95_packet(p95_packet: Any) -> list[str]:
    if p95_packet is None:
        return ["p95_artifact_missing"]
    if not isinstance(p95_packet, dict):
        return ["p95_artifact_malformed:not_a_dict"]

    blockers: list[str] = []
    if p95_packet.get("lane_id") != UPSTREAM_LANE_ID:
        blockers.append(f"lane_id_mismatch:{p95_packet.get('lane_id')!r}")
    if p95_packet.get("artifact_type") != UPSTREAM_ARTIFACT_TYPE:
        blockers.append(f"artifact_type_mismatch:{p95_packet.get('artifact_type')!r}")
    if p95_packet.get("spec_builder_status") != "PASS":
        blockers.append(f"spec_builder_status_not_pass:{p95_packet.get('spec_builder_status')!r}")
    if p95_packet.get("specs_ready") is not True:
        blockers.append(f"specs_ready_not_true:{p95_packet.get('specs_ready')!r}")

    built_specs = p95_packet.get("built_specs")
    if not isinstance(built_specs, list):
        blockers.append("built_specs_malformed:not_a_list")
    else:
        built_spec_ids: list[str] = []
        for spec in built_specs:
            if isinstance(spec, str):
                built_spec_ids.append(spec)
            elif isinstance(spec, dict) and isinstance(spec.get("spec_id"), str):
                built_spec_ids.append(spec["spec_id"])
            else:
                built_spec_ids.append(str(spec))
        if sorted(built_spec_ids) != sorted(EXPECTED_BUILT_SPECS):
            blockers.append(f"built_specs_mismatch:{built_spec_ids!r}")

    return blockers


def _build_validation_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for spec_id in EXPECTED_BUILT_SPECS:
        records.append(
            {
                "validation_id": spec_id.replace("_SPEC", "_VALIDATION_PLAN"),
                "spec_id": spec_id,
                "source_surface_id": SOURCE_SURFACES_BY_SPEC[spec_id],
                "research_fold_family": FAMILY_BY_SPEC[spec_id],
                "validation_scope": "advisory_research_fold_validation_only",
                "required_checks": list(REQUIRED_CHECKS),
                "expected_evidence": list(EXPECTED_EVIDENCE),
                "status": "PLANNED",
            }
        )
    return sorted(records, key=lambda record: str(record["validation_id"]))


def build_research_fold_validation_plan(
    *,
    p95_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = _validate_p95_packet(p95_packet)

    if blockers:
        status = "NOT_COMPUTABLE"
        ready = False
        records: list[dict[str, Any]] = []
        next_lane = RECOMMENDED_NEXT_LANE_ON_BLOCK
    else:
        status = "PASS"
        ready = True
        records = _build_validation_records()
        next_lane = RECOMMENDED_NEXT_LANE_ON_PASS

    packet_base: dict[str, Any] = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "validation_plan_status": status,
        "validation_plan_ready": ready,
        "validation_records": records,
        "missing_or_invalid_inputs": blockers,
        "provenance": {
            "source": "p95_research_fold_drop_spec_builder",
            "upstream_lane_id": UPSTREAM_LANE_ID,
            "expected_built_specs": list(EXPECTED_BUILT_SPECS),
            "deterministic_ordering": "validation_id_ascending",
        },
        "recommended_next_lane": next_lane,
        "authority_locks": _build_authority_locks(),
    }
    return _finalize(packet_base)


def write_research_fold_validation_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
