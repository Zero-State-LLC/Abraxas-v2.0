from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalCoherenceEvidenceRestorationPlanning.v1"
SLICE_ID = "LOOP-805-SLICE-49"
STATUS = "TEMPORAL_COHERENCE_EVIDENCE_RESTORATION_PLANNING_READY_ADVISORY_ONLY"

DEFAULT_OUT_PATH = "out/audit/temporal_coherence_evidence_restoration_planning_001.latest.json"

SOURCE_ARTIFACT_PATHS = (
    "out/temporal_continuity_binder_readiness_audit/latest.json",
    "out/temporal_continuity_evidence_index/latest.json",
    "out/temporal_continuity_missing_evidence_restoration_plan/latest.json",
    "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
    "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
)

TARGET_EVIDENCE_PATHS = (
    "out/audit/temporal_coherence_chain_001.latest.json",
    "out/projections/coherence_field_operator_surface_001.latest.json",
    "out/projections/temporal_resonance_coherence_001.latest.json",
)

_STATUS_FIELDS = (
    "readiness_status",
    "evidence_index_status",
    "restoration_plan_status",
    "execution_plan_status",
    "authorization_gate_status",
    "authorization_record_plan_status",
    "recommended_next_lane",
)

_DENIED_AUTHORITY = (
    "sandbox_probe_execution",
    "fixture_binding_execution",
    "external_calls",
    "notion_writeback",
    "github_writeback",
    "mcp_exposure",
    "canon_mutation",
    "runtime_activation",
    "runtime_mutation",
    "repair_execution",
    "evidence_generation",
    "production_activation",
)


def _load_json(path: Path) -> tuple[dict[str, Any] | None, bool]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None, path.exists()
    return (payload if isinstance(payload, dict) else None), False


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_hash(payload: dict[str, Any] | None, path: Path) -> str:
    if payload is None:
        return "NOT_COMPUTABLE"
    for key in ("canonical_hash", "packet_hash"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return _sha256_file(path)


def _status_snapshot(payload: dict[str, Any] | None) -> dict[str, str]:
    if payload is None:
        return {}
    return {
        field: str(payload[field])
        for field in _STATUS_FIELDS
        if field in payload and payload[field] is not None
    }


def _path_state(repo_root: Path, path: str) -> dict[str, Any]:
    target = repo_root / path
    observed = target.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    if observed:
        try:
            raw = target.read_bytes()
            readable = True
            file_hash = hashlib.sha256(raw).hexdigest()
            if path.endswith(".json"):
                json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            malformed_json = True

    return {
        "path": path,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "brier_score": 0.1,
    }


def _source_state(repo_root: Path, path: str) -> dict[str, Any]:
    target = repo_root / path
    payload, malformed_json = _load_json(target)
    observed = target.exists()
    return {
        "path": path,
        "observed": observed,
        "readable": payload is not None,
        "malformed_json": malformed_json,
        "source_hash": _source_hash(payload, target) if observed else "NOT_COMPUTABLE",
        "status_snapshot": _status_snapshot(payload),
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {key: False for key in _DENIED_AUTHORITY}


def build_temporal_coherence_evidence_restoration_planning(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    target_evidence = [_path_state(root, path) for path in TARGET_EVIDENCE_PATHS]
    source_artifacts = [_source_state(root, path) for path in SOURCE_ARTIFACT_PATHS]
    missing_targets = [
        str(item["path"]) for item in target_evidence if not bool(item["observed"])
    ]
    malformed_targets = [
        str(item["path"])
        for item in target_evidence
        if bool(item["observed"]) and bool(item["malformed_json"])
    ]
    unavailable_sources = [
        str(item["path"]) for item in source_artifacts if not bool(item["readable"])
    ]

    plan_status = (
        "READY_WITH_MISSING_TEMPORAL_COHERENCE_EVIDENCE"
        if missing_targets
        else "READY_WITH_ALL_TARGET_EVIDENCE_OBSERVED"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "brier_score": 0.1,
        "target_evidence": target_evidence,
        "source_artifacts": source_artifacts,
        "missing_target_evidence_paths": sorted(missing_targets),
        "malformed_target_evidence_paths": sorted(malformed_targets),
        "unavailable_source_artifact_paths": sorted(unavailable_sources),
        "restoration_planning_status": plan_status,
        "recommended_next_advisory_action": (
            "Operator review of Slice49 receipt, then choose whether to create a "
            "separate temporal coherence regeneration authorization gate. This "
            "receipt does not authorize evidence generation or repair execution."
        ),
        "sandbox_gate_status": {
            "issue": "#892",
            "required_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "phrase_issued_by_this_slice": False,
            "sandbox_probe_authorized": False,
            "brier_score": 0.1,
        },
        "authority_locks": _authority_locks(),
        "denied_authority": sorted(_DENIED_AUTHORITY),
        "provenance": {
            "source": "Notion Sprint 001 Hub + Loop 805 Slice49",
            "source_of_truth": "Technical Debt Board + repo temporal continuity receipts",
            "parent_main_sha": "25ff37bea53eedf4f8ef15d51ae1112dc686d888",
            "slice48_status": "MERGED",
            "brier_score": 0.1,
        },
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_temporal_coherence_evidence_restoration_planning(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
