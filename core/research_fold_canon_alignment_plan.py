from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

INTAKE_ARTIFACT_PATH = Path("out/canon_drop_research_fold_evidence_intake/latest.json")

ARTIFACT_TYPE = "ResearchFoldCanonAlignmentPlan.v1"
LANE_ID = "P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
RECOMMENDED_NEXT_LANE_ON_PASS = "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"

REQUIRED_UPSTREAM_SURFACES: tuple[str, ...] = (
    "canon_drop_006_research_folds",
    "canon_drop_007_research_folds",
)

DROP_TO_CANDIDATES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "DROP006",
        (
            "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
            "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
            "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
        ),
    ),
    (
        "DROP007",
        (
            "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
            "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
            "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
        ),
    ),
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
)

_BOUNDARY_RULES: tuple[str, ...] = (
    "hidden_intent_is_never_known_intent",
    "proactivity_is_never_autonomous_execution",
    "intent_graph_dependency_is_never_confirmed_intent",
    "endpoint_constraint_is_never_known_goal",
    "calibration_projection_is_never_forecast_weight_mutation",
    "aal_viz_is_projection_only",
)


def _normalize_supplied_surface_ids(supplied_upstream_surfaces: Any) -> set[str]:
    if isinstance(supplied_upstream_surfaces, dict):
        return {
            str(surface_id)
            for surface_id, surface_payload in supplied_upstream_surfaces.items()
            if surface_payload is not None
        }
    if isinstance(supplied_upstream_surfaces, (list, tuple, set)):
        return {str(surface_id) for surface_id in supplied_upstream_surfaces}
    return set()


def _build_research_fold_targets() -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    for drop_id, candidates in DROP_TO_CANDIDATES:
        for candidate_id in sorted(candidates):
            targets.append(
                {
                    "drop_id": drop_id,
                    "candidate_id": candidate_id,
                    "target_mapping": f"research_fold:{candidate_id.lower()}",
                    "implementation_mode": "ADVISORY_TARGET_ONLY",
                }
            )
    return targets


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _load_intake_surface_ids() -> set[str]:
    if not INTAKE_ARTIFACT_PATH.exists():
        return set()
    try:
        payload = json.loads(INTAKE_ARTIFACT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(payload, dict):
        return set()
    if payload.get("evidence_complete") is not True:
        return set()
    observed = payload.get("observed_surfaces")
    if not isinstance(observed, list):
        return set()
    surface_ids: set[str] = set()
    for entry in observed:
        if isinstance(entry, dict) and entry.get("surface_complete") is True:
            surface_id = entry.get("surface_id")
            if isinstance(surface_id, str) and surface_id:
                surface_ids.add(surface_id)
    return surface_ids


def build_research_fold_canon_alignment_plan(
    *,
    supplied_upstream_surfaces: dict[str, Any] | list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict[str, Any]:
    supplied_surface_ids = _normalize_supplied_surface_ids(supplied_upstream_surfaces)
    if not supplied_surface_ids:
        supplied_surface_ids = _load_intake_surface_ids()
    missing_required_surfaces = [
        surface_id for surface_id in REQUIRED_UPSTREAM_SURFACES if surface_id not in supplied_surface_ids
    ]

    status = "PASS"
    canon_alignment_status = "ALIGNED"
    recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
    recommended_next_lane_reason = (
        "P94 alignment is advisory-only and aligned; proceed to governed specification planning in P95."
    )
    not_computable_reasons: list[str] = []

    if missing_required_surfaces:
        status = "NOT_COMPUTABLE"
        canon_alignment_status = "NOT_ALIGNED"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Required upstream canon surfaces are missing; alignment cannot be computed."
        )
        not_computable_reasons = [
            f"missing_required_upstream_surface:{surface_id}"
            for surface_id in missing_required_surfaces
        ]

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "canon_alignment_status": canon_alignment_status,
        "research_fold_targets": _build_research_fold_targets(),
        "required_upstream_surfaces": [
            {
                "surface_id": surface_id,
                "supplied": surface_id in supplied_surface_ids,
            }
            for surface_id in REQUIRED_UPSTREAM_SURFACES
        ],
        "authority_locks": {lock_key: False for lock_key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "notion_canon_drop_006_007",
            "mapping_method": "deterministic_static_alignment",
            "drop_order": [drop_id for drop_id, _ in DROP_TO_CANDIDATES],
            "candidate_ordering": "drop_order_then_lexicographic_candidate_id",
            "supplied_upstream_surface_ids": sorted(supplied_surface_ids),
            "missing_required_upstream_surfaces": missing_required_surfaces,
            "boundary_rules": list(_BOUNDARY_RULES),
            "gated_recommendation_rule": "recommend_p95_only_when_status_pass_and_alignment_aligned",
        },
    }
    return _finalize(packet_base)


def write_research_fold_canon_alignment_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
