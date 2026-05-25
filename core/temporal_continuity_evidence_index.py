from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityEvidenceIndex.v1"
SOURCE_READINESS_AUDIT_PATH = "out/temporal_continuity_binder_readiness_audit/latest.json"
SOURCE_BINDER_CONTRACT_PATH = "out/temporal_continuity_spine_binder_contract/latest.json"
SOURCE_PRECHECK_PATH = "out/temporal_continuity_spine_precheck/latest.json"

_DENIED_AUTHORITY = (
    "approval_granted",
    "authorization_granted",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "evidence_generation_authority",
    "spine_implementation_authority",
)

_PATH_TOKEN_RE = re.compile(r"(?:out|scripts)/[A-Za-z0-9_./-]+")


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _unique_sorted(items: list[str]) -> list[str]:
    return sorted(set(items))


def _extract_paths_from_marker(value: str) -> list[str]:
    if "|" in value and ":" in value:
        _, right = value.split(":", 1)
        return sorted(set(path for path in right.split("|") if path.startswith(("out/", "scripts/"))))
    return _unique_sorted(_PATH_TOKEN_RE.findall(value))


def _source_category(path: str) -> str:
    if path.startswith("out/audit/"):
        return "audit"
    if path.startswith("out/projections/"):
        return "projection"
    if path.startswith("out/archive/"):
        return "archive"
    if path.startswith("out/package/"):
        return "package"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("out/canon_resume_state/"):
        return "canon_resume_state"
    if path.startswith("out/temporal_continuity"):
        return "temporal_continuity"
    return "unknown"


def _read_path_state(root: Path, path: str) -> tuple[bool, bool, bool, str]:
    target = root / path
    observed = target.exists()
    if not observed:
        return False, False, False, "NOT_COMPUTABLE"

    try:
        raw = target.read_bytes()
    except OSError:
        return True, False, False, "NOT_COMPUTABLE"

    malformed_json = False
    if path.endswith(".json"):
        try:
            json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            malformed_json = True

    return True, True, malformed_json, hashlib.sha256(raw).hexdigest()


def _build_group_maps(
    continuity_group_statuses: list[dict[str, Any]],
) -> tuple[dict[str, set[str]], dict[str, str], set[str], set[str]]:
    path_to_groups: dict[str, set[str]] = {}
    group_status_map: dict[str, str] = {}
    observed_group_paths: set[str] = set()
    missing_group_paths: set[str] = set()

    for group in continuity_group_statuses:
        group_id = str(group.get("group_id", "UNKNOWN"))
        group_status_map[group_id] = str(group.get("status", "NOT_COMPUTABLE"))

        observed_paths = _as_str_list(group.get("observed_paths"))
        missing_paths = _as_str_list(group.get("missing_paths"))
        for path in observed_paths:
            observed_group_paths.add(path)
            path_to_groups.setdefault(path, set()).add(group_id)
        for path in missing_paths:
            missing_group_paths.add(path)
            path_to_groups.setdefault(path, set()).add(group_id)

    observed_group_paths -= missing_group_paths
    return path_to_groups, group_status_map, observed_group_paths, missing_group_paths


def _group_id_values(path_to_groups: dict[str, set[str]], path: str) -> list[str]:
    groups = sorted(path_to_groups.get(path, set()))
    return groups or ["UNKNOWN"]


def build_temporal_continuity_evidence_index(
    *,
    repo_root: str | Path = ".",
    source_readiness_audit_path: str = SOURCE_READINESS_AUDIT_PATH,
    source_binder_contract_path: str = SOURCE_BINDER_CONTRACT_PATH,
    source_precheck_path: str = SOURCE_PRECHECK_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_readiness_audit_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)
    source_usable = source_payload is not None
    source_hash = _sha256_file(source_path) if source_usable else "NOT_COMPUTABLE"

    supporting_inputs: list[dict[str, Any]] = []
    for label, rel_path in (
        ("binder_contract", source_binder_contract_path),
        ("spine_precheck", source_precheck_path),
    ):
        absolute = root / rel_path
        payload = _load_json_dict(absolute)
        usable = payload is not None
        supporting_inputs.append(
            {
                "input_label": label,
                "path": rel_path,
                "observed": absolute.exists(),
                "readable": usable,
                "source_hash": _sha256_file(absolute) if usable else "NOT_COMPUTABLE",
            }
        )
    supporting_inputs = sorted(supporting_inputs, key=lambda item: item["input_label"])

    if not source_usable:
        packet_base: dict[str, Any] = {
            "artifact_type": ARTIFACT_TYPE,
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "approval_granted": False,
            "authorization_granted": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "evidence_generation_authority": False,
            "spine_implementation_authority": False,
            "source_readiness_audit_path": source_readiness_audit_path,
            "source_readiness_audit_observed": source_observed,
            "source_readiness_audit_hash": source_hash,
            "source_readiness_status": "NOT_COMPUTABLE",
            "source_recommended_next_lane": "NOT_COMPUTABLE",
            "supporting_inputs": supporting_inputs,
            "evidence_index_status": "NOT_COMPUTABLE",
            "evidence_items": [],
            "observed_evidence_paths": [],
            "missing_evidence_paths": [source_readiness_audit_path],
            "unreadable_evidence_paths": [],
            "degraded_evidence_inputs": [],
            "ready_groups": [],
            "degraded_groups": [],
            "partial_groups": [],
            "not_computable_groups": [],
            "inherited_blockers": [
                f"source_readiness_audit_not_computable:{source_readiness_audit_path}"
            ],
            "inherited_drift_flags": ["SOURCE_READINESS_AUDIT_NOT_COMPUTABLE"],
            "semantic_overlap_flags": [],
            "group_evidence_summary": [],
            "recommended_next_lane": "NOT_COMPUTABLE",
            "recommended_next_lane_reason": (
                "Primary P72 readiness audit is missing, unreadable, or malformed; next lane is not computable from repo evidence."
            ),
            "denied_authority": sorted(_DENIED_AUTHORITY),
        }
        packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
        return json.loads(
            json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        )

    continuity_group_statuses_raw = source_payload.get("continuity_group_statuses")
    continuity_group_statuses = (
        [group for group in continuity_group_statuses_raw if isinstance(group, dict)]
        if isinstance(continuity_group_statuses_raw, list)
        else []
    )
    continuity_group_statuses = sorted(
        (
            json.loads(
                json.dumps(group, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            )
            for group in continuity_group_statuses
        ),
        key=lambda item: str(item.get("group_id", "")),
    )

    missing_or_not_computable_inputs = _as_str_list(
        source_payload.get("missing_or_not_computable_inputs")
    )
    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    path_to_groups, group_status_map, observed_group_paths, missing_group_paths = _build_group_maps(
        continuity_group_statuses
    )

    degraded_paths = {
        path
        for marker in degraded_evidence_inputs
        for path in _extract_paths_from_marker(marker)
    }
    blocker_paths = {
        path for marker in inherited_blockers for path in _extract_paths_from_marker(marker)
    }
    semantic_overlap_paths = {
        path for marker in semantic_overlap_flags for path in _extract_paths_from_marker(marker)
    }
    missing_input_paths = {
        path
        for marker in missing_or_not_computable_inputs
        for path in _extract_paths_from_marker(marker)
    }

    all_paths = sorted(
        observed_group_paths
        | missing_group_paths
        | missing_input_paths
        | degraded_paths
        | blocker_paths
        | semantic_overlap_paths
    )

    observed_evidence_paths: list[str] = []
    missing_evidence_paths: list[str] = []
    unreadable_evidence_paths: list[str] = []

    path_state: dict[str, tuple[bool, bool, bool, str]] = {}
    for path in all_paths:
        state = _read_path_state(root, path)
        path_state[path] = state
        observed, readable, malformed_json, _ = state
        if observed:
            observed_evidence_paths.append(path)
        else:
            missing_evidence_paths.append(path)
        if observed and ((not readable) or malformed_json):
            unreadable_evidence_paths.append(path)

    entries: set[tuple[str, str, str]] = set()
    for path in observed_group_paths:
        for group_id in _group_id_values(path_to_groups, path):
            entries.add((path, group_id, "observed_path"))
    for path in missing_group_paths | missing_input_paths:
        for group_id in _group_id_values(path_to_groups, path):
            entries.add((path, group_id, "missing_path"))
    for path in degraded_paths:
        for group_id in _group_id_values(path_to_groups, path):
            entries.add((path, group_id, "degraded_input"))
    for path in blocker_paths:
        for group_id in _group_id_values(path_to_groups, path):
            entries.add((path, group_id, "blocker_path"))
    for path in semantic_overlap_paths:
        for group_id in _group_id_values(path_to_groups, path):
            entries.add((path, group_id, "semantic_overlap_path"))
    existing_entry_paths = {entry[0] for entry in entries}
    for path in all_paths:
        if path not in existing_entry_paths:
            for group_id in _group_id_values(path_to_groups, path):
                entries.add((path, group_id, "unknown"))

    evidence_items: list[dict[str, Any]] = []
    for path, group_id, role in sorted(
        entries,
        key=lambda item: (item[0], item[1], item[2]),
    ):
        observed, readable, malformed_json, evidence_hash = path_state[path]
        if group_id != "UNKNOWN" and group_id in group_status_map:
            inherited_status = group_status_map[group_id]
        elif role == "missing_path":
            inherited_status = "MISSING"
        elif role == "degraded_input":
            inherited_status = "DEGRADED"
        else:
            inherited_status = "NOT_COMPUTABLE"

        evidence_items.append(
            {
                "path": path,
                "group_id": group_id,
                "evidence_role": role,
                "observed": observed,
                "readable": readable,
                "malformed_json": malformed_json,
                "source_category": _source_category(path),
                "inherited_status": inherited_status,
                "evidence_hash": evidence_hash if readable else "NOT_COMPUTABLE",
            }
        )

    degraded_path_set = set(degraded_paths)
    group_evidence_summary: list[dict[str, Any]] = []
    for group in continuity_group_statuses:
        group_id = str(group.get("group_id", "UNKNOWN"))
        group_paths = _unique_sorted(
            _as_str_list(group.get("observed_paths")) + _as_str_list(group.get("missing_paths"))
        )
        ready_count = 0
        missing_count = 0
        unreadable_count = 0
        degraded_count = 0

        for path in group_paths:
            observed, readable, malformed_json, _ = path_state.get(
                path, _read_path_state(root, path)
            )
            if not observed:
                missing_count += 1
                continue
            if (not readable) or malformed_json:
                unreadable_count += 1
                continue
            if path in degraded_path_set:
                degraded_count += 1
                continue
            ready_count += 1

        group_evidence_summary.append(
            {
                "group_id": group_id,
                "group_status": str(group.get("status", "NOT_COMPUTABLE")),
                "ready_count": ready_count,
                "missing_count": missing_count,
                "unreadable_count": unreadable_count,
                "degraded_count": degraded_count,
                "total_paths": len(group_paths),
            }
        )

    group_evidence_summary = sorted(group_evidence_summary, key=lambda item: item["group_id"])

    missing_evidence_paths = _unique_sorted(missing_evidence_paths)
    unreadable_evidence_paths = _unique_sorted(unreadable_evidence_paths)
    observed_evidence_paths = _unique_sorted(observed_evidence_paths)

    source_readiness_status = str(source_payload.get("readiness_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(
        source_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
    )

    ready_groups: list[str] = []
    degraded_groups: list[str] = []
    partial_groups: list[str] = []
    not_computable_groups: list[str] = []
    for group in continuity_group_statuses:
        group_id = str(group.get("group_id", "UNKNOWN"))
        status = str(group.get("status", "NOT_COMPUTABLE"))
        if status == "READY":
            ready_groups.append(group_id)
        elif status == "DEGRADED":
            degraded_groups.append(group_id)
        elif status == "PARTIAL":
            partial_groups.append(group_id)
        else:
            not_computable_groups.append(group_id)
    ready_groups = _unique_sorted(ready_groups)
    degraded_groups = _unique_sorted(degraded_groups)
    partial_groups = _unique_sorted(partial_groups)
    not_computable_groups = _unique_sorted(not_computable_groups)

    if missing_evidence_paths or unreadable_evidence_paths:
        evidence_index_status = "MISSING_EVIDENCE_INDEXED"
        recommended_next_lane = "P74_TEMPORAL_CONTINUITY_MISSING_EVIDENCE_RESTORATION_PLAN"
        recommended_next_lane_reason = (
            "One or more required continuity evidence paths are missing, unreadable, or malformed; index restoration planning is required first."
        )
    elif degraded_evidence_inputs:
        evidence_index_status = "DEGRADED_EVIDENCE_INDEXED"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Evidence is readable but degraded-only routing is not explicitly named in repo evidence for P73 outputs."
        )
    else:
        evidence_index_status = "EVIDENCE_READY"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "No explicit repo-evidenced post-P73 lane is named for fully ready evidence indexes."
        )

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "approval_granted": False,
        "authorization_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "spine_implementation_authority": False,
        "source_readiness_audit_path": source_readiness_audit_path,
        "source_readiness_audit_observed": source_observed,
        "source_readiness_audit_hash": source_hash,
        "source_readiness_status": source_readiness_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "supporting_inputs": supporting_inputs,
        "evidence_index_status": evidence_index_status,
        "evidence_items": evidence_items,
        "observed_evidence_paths": observed_evidence_paths,
        "missing_evidence_paths": missing_evidence_paths,
        "unreadable_evidence_paths": unreadable_evidence_paths,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "ready_groups": ready_groups,
        "degraded_groups": degraded_groups,
        "partial_groups": partial_groups,
        "not_computable_groups": not_computable_groups,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "group_evidence_summary": group_evidence_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {
        **packet_base,
        "packet_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_evidence_index(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
