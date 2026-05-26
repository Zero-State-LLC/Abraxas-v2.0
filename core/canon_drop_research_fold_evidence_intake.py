from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "CanonDropResearchFoldEvidenceIntake.v1"
LANE_ID = "P093_CANON_DROP_RESEARCH_FOLD_EVIDENCE_INTAKE"
CANONICAL_STATUS = "ADVISORY_ONLY"

REQUIRED_SURFACES: tuple[str, ...] = (
    "canon_drop_006_research_folds",
    "canon_drop_007_research_folds",
)

ACCEPTED_SOURCE_LABELS: tuple[str, ...] = (
    "notion_canon_drop_006_007",
    "notion_canon_drop_006",
    "notion_canon_drop_007",
)
ACCEPTED_SOURCE_TYPES: tuple[str, ...] = ("notion", "external_canon", "repo_manifest")
ACCEPTED_VALIDATION_STATUSES: tuple[str, ...] = (
    "PRESENT",
    "ABSENT",
    "INVALID",
    "NOT_COMPUTABLE",
)

NEXT_ON_INCOMPLETE = "PROVIDE_CANON_DROP_RESEARCH_FOLD_EVIDENCE_MANIFEST"
NEXT_ON_COMPLETE = "P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN_REGENERATION"


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _normalize_manifest(manifest: Any) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(manifest, dict):
        return [], ["manifest_malformed:not_a_dict"]
    surfaces = manifest.get("surfaces")
    if not isinstance(surfaces, list):
        return [], ["manifest_malformed:surfaces_not_a_list"]
    normalized = [entry for entry in surfaces if isinstance(entry, dict)]
    malformed_count = len(surfaces) - len(normalized)
    reasons = [] if malformed_count == 0 else [f"manifest_malformed:non_object_surface_entries:{malformed_count}"]
    return normalized, reasons


def _surface_entry_status(entry: dict[str, Any]) -> tuple[dict[str, Any], list[str], bool]:
    surface_id = str(entry.get("surface_id", ""))
    source_label = str(entry.get("source_label", ""))
    source_type = str(entry.get("source_type", ""))
    evidence_reference = str(entry.get("evidence_reference", ""))
    content_hash = str(entry.get("content_hash", ""))
    checksum = str(entry.get("checksum", ""))
    observed_at = str(entry.get("observed_at", ""))
    timestamp = str(entry.get("timestamp", ""))
    validation_status = str(entry.get("validation_status", "NOT_COMPUTABLE"))

    issues: list[str] = []
    if source_label not in ACCEPTED_SOURCE_LABELS:
        issues.append("invalid_source_label")
    if source_type not in ACCEPTED_SOURCE_TYPES:
        issues.append("invalid_source_type")
    if validation_status not in ACCEPTED_VALIDATION_STATUSES:
        issues.append("invalid_validation_status")

    hash_value = content_hash if content_hash else checksum
    hash_present = bool(hash_value.strip())
    evidence_present = bool(evidence_reference.strip())

    complete = (
        validation_status == "PRESENT" and evidence_present and hash_present and not issues
    )

    normalized = {
        "surface_id": surface_id,
        "source_label": source_label,
        "source_type": source_type,
        "evidence_reference": evidence_reference,
        "content_hash": content_hash,
        "checksum": checksum,
        "observed_at": observed_at,
        "timestamp": timestamp,
        "validation_status": validation_status,
        "evidence_reference_present": evidence_present,
        "hash_present": hash_present,
        "surface_complete": complete,
        "issues": sorted(issues),
    }
    return normalized, issues, complete


def build_canon_drop_research_fold_evidence_intake(
    *, manifest: dict[str, Any] | None
) -> dict[str, Any]:
    authority_locks = {
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
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

    if manifest is None:
        return _finalize(
            {
                "artifact_type": ARTIFACT_TYPE,
                "canonical_status": CANONICAL_STATUS,
                "lane_id": LANE_ID,
                "intake_status": "NOT_COMPUTABLE",
                "required_surfaces": list(REQUIRED_SURFACES),
                "observed_surfaces": [],
                "missing_surfaces": list(REQUIRED_SURFACES),
                "invalid_surfaces": [],
                "evidence_complete": False,
                "required_surfaces_present": False,
                "provenance": {
                    "source": "input/canon_drop_research_fold_evidence_manifest.json",
                    "manifest_present": False,
                    "validation_reasons": ["manifest_missing"],
                },
                "recommended_next_lane": NEXT_ON_INCOMPLETE,
                "authority_locks": authority_locks,
            }
        )

    entries, manifest_reasons = _normalize_manifest(manifest)
    by_surface: dict[str, dict[str, Any]] = {}
    for entry in entries:
        sid = str(entry.get("surface_id", ""))
        if sid and sid not in by_surface:
            by_surface[sid] = entry

    observed_surfaces: list[dict[str, Any]] = []
    invalid_surfaces: list[str] = []
    missing_surfaces: list[str] = []

    for surface_id in REQUIRED_SURFACES:
        source_entry = by_surface.get(surface_id)
        if source_entry is None:
            missing_surfaces.append(surface_id)
            continue
        normalized, issues, complete = _surface_entry_status(source_entry)
        observed_surfaces.append(normalized)
        if (not complete) or issues:
            invalid_surfaces.append(surface_id)

    required_surfaces_present = not missing_surfaces and not invalid_surfaces
    evidence_complete = required_surfaces_present

    if manifest_reasons:
        intake_status = "NOT_COMPUTABLE"
        recommended_next_lane = NEXT_ON_INCOMPLETE
    elif evidence_complete:
        intake_status = "CANON_DROP_RESEARCH_FOLD_EVIDENCE_PRESENT"
        recommended_next_lane = NEXT_ON_COMPLETE
    else:
        intake_status = "CANON_DROP_RESEARCH_FOLD_EVIDENCE_INCOMPLETE"
        recommended_next_lane = NEXT_ON_INCOMPLETE

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "lane_id": LANE_ID,
        "intake_status": intake_status,
        "required_surfaces": list(REQUIRED_SURFACES),
        "observed_surfaces": observed_surfaces,
        "missing_surfaces": sorted(missing_surfaces),
        "invalid_surfaces": sorted(set(invalid_surfaces)),
        "evidence_complete": evidence_complete,
        "required_surfaces_present": required_surfaces_present,
        "provenance": {
            "source": "input/canon_drop_research_fold_evidence_manifest.json",
            "manifest_present": True,
            "manifest_id": manifest.get("manifest_id") if isinstance(manifest, dict) else None,
            "validation_reasons": sorted(manifest_reasons),
            "accepted_source_labels": list(ACCEPTED_SOURCE_LABELS),
            "accepted_source_types": list(ACCEPTED_SOURCE_TYPES),
            "accepted_validation_statuses": list(ACCEPTED_VALIDATION_STATUSES),
        },
        "recommended_next_lane": recommended_next_lane,
        "authority_locks": authority_locks,
    }
    return _finalize(packet_base)


def write_canon_drop_research_fold_evidence_intake(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
