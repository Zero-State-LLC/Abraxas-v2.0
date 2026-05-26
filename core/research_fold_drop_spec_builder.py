from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchFoldDropSpecBuilder.v1"
LANE_ID = "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"
CANONICAL_STATUS = "ADVISORY_ONLY"
RECOMMENDED_NEXT_LANE_ON_PASS = "P96_RESEARCH_FOLD_VALIDATION_PLAN"
RECOMMENDED_NEXT_LANE_ON_BLOCK = "P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN_REGENERATION"

REQUIRED_P94_ARTIFACT_TYPE = "ResearchFoldCanonAlignmentPlan.v1"
REQUIRED_P94_LANE_ID = "P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN"

REQUIRED_SURFACE_IDS: tuple[str, ...] = (
    "canon_drop_006_research_folds",
    "canon_drop_007_research_folds",
)

SURFACE_SPEC_MAP: dict[str, dict[str, str]] = {
    "canon_drop_006_research_folds": {
        "spec_id": "DROP006_RESEARCH_FOLD_SPEC",
        "source_label": "notion_canon_drop_006",
        "research_fold_family": "intent_graph_active_inference_survival_calibration",
    },
    "canon_drop_007_research_folds": {
        "spec_id": "DROP007_RESEARCH_FOLD_SPEC",
        "source_label": "notion_canon_drop_007",
        "research_fold_family": "situation_runtime_proactive_coordination",
    },
}


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _validate_p94_packet(p94_packet: Any) -> list[str]:
    if p94_packet is None:
        return ["p94_packet_missing"]
    if not isinstance(p94_packet, dict):
        return ["p94_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    if p94_packet.get("artifact_type") != REQUIRED_P94_ARTIFACT_TYPE:
        reasons.append(f"p94_artifact_type_mismatch:{p94_packet.get('artifact_type')!r}")
    if p94_packet.get("lane_id") != REQUIRED_P94_LANE_ID:
        reasons.append(f"p94_lane_id_mismatch:{p94_packet.get('lane_id')!r}")

    status = p94_packet.get("status")
    alignment_status = p94_packet.get("canon_alignment_status")
    if status != "PASS":
        reasons.append(f"p94_status_not_pass:{status!r}")
    if alignment_status != "ALIGNED":
        reasons.append(f"p94_alignment_not_aligned:{alignment_status!r}")

    required = p94_packet.get("required_upstream_surfaces")
    if not isinstance(required, list):
        reasons.append("p94_required_upstream_surfaces_malformed")
        return sorted(set(reasons))

    supplied: set[str] = set()
    for entry in required:
        if isinstance(entry, dict):
            sid = entry.get("surface_id")
            if isinstance(sid, str) and entry.get("supplied") is True:
                supplied.add(sid)

    for sid in REQUIRED_SURFACE_IDS:
        if sid not in supplied:
            reasons.append(f"p94_missing_required_surface:{sid}")

    return sorted(set(reasons))


def _extract_intake_observations(p94_packet: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if not isinstance(p94_packet, dict):
        return {}
    p093_path = Path("input/canon_drop_research_fold_evidence_manifest.json")
    if not p093_path.exists():
        return {}
    try:
        payload = json.loads(p093_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    surfaces = payload.get("surfaces")
    if not isinstance(surfaces, list):
        return {}
    out: dict[str, dict[str, str]] = {}
    for row in surfaces:
        if not isinstance(row, dict):
            continue
        sid = row.get("surface_id")
        if not isinstance(sid, str) or sid not in REQUIRED_SURFACE_IDS:
            continue
        out[sid] = {
            "source_type": str(row.get("source_type", "")),
            "source_label": str(row.get("source_label", "")),
            "evidence_reference": str(row.get("evidence_reference", "")),
            "content_hash": str(row.get("content_hash", "")) or str(row.get("checksum", "")),
            "checksum_scope": "identity_reference_only",
        }
    return out


def _build_specs(observations: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for sid in REQUIRED_SURFACE_IDS:
        m = SURFACE_SPEC_MAP[sid]
        obs = observations.get(sid, {})
        specs.append(
            {
                "spec_id": m["spec_id"],
                "source_surface_id": sid,
                "source_label": obs.get("source_label") or m["source_label"],
                "source_type": obs.get("source_type") or "notion",
                "evidence_reference": obs.get("evidence_reference", ""),
                "content_hash": obs.get("content_hash", ""),
                "checksum_scope": obs.get("checksum_scope", ""),
                "research_fold_family": m["research_fold_family"],
                "advisory_scope": "research_fold_specification_only",
                "governance_posture": "ADVISORY_ONLY",
                "status": "SPEC_READY",
            }
        )
    return sorted(specs, key=lambda x: str(x["spec_id"]))


def build_research_fold_drop_spec_builder(*, p94_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    blockers = _validate_p94_packet(p94_packet)

    authority_locks = {
        "advisory_only": True,
        "projection_only": True,
        "planning_only": True,
        "evidence_only": True,
        "spec_only": True,
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
    }

    if blockers:
        packet_base = {
            "lane_id": LANE_ID,
            "artifact_type": ARTIFACT_TYPE,
            "canonical_status": CANONICAL_STATUS,
            "spec_builder_status": "NOT_COMPUTABLE",
            "specs_ready": False,
            "built_specs": [],
            "missing_or_invalid_inputs": blockers,
            "provenance": {
                "source": "p94_research_fold_canon_alignment_plan",
                "p94_status": p94_packet.get("status") if isinstance(p94_packet, dict) else None,
                "p94_alignment_status": p94_packet.get("canon_alignment_status") if isinstance(p94_packet, dict) else None,
                "required_surface_ids": list(REQUIRED_SURFACE_IDS),
                "spec_ordering": "lexicographic_spec_id",
            },
            "recommended_next_lane": RECOMMENDED_NEXT_LANE_ON_BLOCK,
            "authority_locks": authority_locks,
        }
        return _finalize(packet_base)

    observations = _extract_intake_observations(p94_packet)
    specs = _build_specs(observations)
    packet_base = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "spec_builder_status": "PASS",
        "specs_ready": True,
        "built_specs": specs,
        "missing_or_invalid_inputs": [],
        "provenance": {
            "source": "p94_research_fold_canon_alignment_plan",
            "p94_status": p94_packet.get("status") if isinstance(p94_packet, dict) else None,
            "p94_alignment_status": p94_packet.get("canon_alignment_status") if isinstance(p94_packet, dict) else None,
            "required_surface_ids": list(REQUIRED_SURFACE_IDS),
            "spec_ordering": "lexicographic_spec_id",
        },
        "recommended_next_lane": RECOMMENDED_NEXT_LANE_ON_PASS,
        "authority_locks": authority_locks,
    }
    return _finalize(packet_base)


def write_research_fold_drop_spec_builder(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
