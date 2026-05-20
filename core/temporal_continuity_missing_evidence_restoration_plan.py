from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityMissingEvidenceRestorationPlan.v1"
SOURCE_EVIDENCE_INDEX_PATH = "out/temporal_continuity_evidence_index/latest.json"

_STRATEGIES = (
    "SCRIPT_DISCOVERY_REQUIRED",
    "GENERATOR_EXISTS_REGENERATION_PLAN",
    "UPSTREAM_INPUT_REQUIRED",
    "UNREADABLE_SOURCE_REPAIR_PLAN",
    "RESTORATION_NOT_REQUIRED",
    "NOT_COMPUTABLE",
)

_ROLE_PRIORITY = (
    "missing_path",
    "blocker_path",
    "degraded_input",
    "observed_path",
    "semantic_overlap_path",
    "unknown",
)

_DENIED_AUTHORITY = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "evidence_generation_authority",
    "restoration_execution_authority",
    "spine_implementation_authority",
)


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


def _read_path_state(root: Path, path: str) -> tuple[bool, bool, bool]:
    target = root / path
    observed = target.exists()
    if not observed:
        return False, False, False

    try:
        raw = target.read_bytes()
    except OSError:
        return True, False, False

    malformed_json = False
    if path.endswith(".json"):
        try:
            json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            malformed_json = True

    return True, True, malformed_json


def _infer_likely_generator_script(root: Path, evidence_path: str) -> str:
    if not evidence_path.startswith("out/") or not evidence_path.endswith(".json"):
        return "NOT_COMPUTABLE"

    file_name = evidence_path.rsplit("/", 1)[-1]
    stem = file_name
    for suffix in ("_001.latest.json", ".latest.json", ".json"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break

    if not stem:
        return "NOT_COMPUTABLE"

    candidate = f"scripts/run_{stem}.py"
    return candidate if (root / candidate).exists() else "NOT_COMPUTABLE"


def _build_path_metadata(
    evidence_items: list[dict[str, Any]],
) -> tuple[
    dict[str, set[str]],
    dict[str, set[str]],
    dict[str, set[str]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[str]],
]:
    path_to_groups: dict[str, set[str]] = {}
    path_to_roles: dict[str, set[str]] = {}
    group_to_observed_paths: dict[str, set[str]] = {}
    path_records: dict[str, list[dict[str, Any]]] = {}
    group_to_paths: dict[str, list[str]] = {}

    for item in evidence_items:
        path = str(item.get("path", ""))
        if not path:
            continue

        group_id = str(item.get("group_id", "UNKNOWN"))
        role = str(item.get("evidence_role", "unknown"))
        observed = bool(item.get("observed", False))

        path_to_groups.setdefault(path, set()).add(group_id)
        path_to_roles.setdefault(path, set()).add(role)
        path_records.setdefault(path, []).append(item)
        group_to_paths.setdefault(group_id, []).append(path)
        if observed:
            group_to_observed_paths.setdefault(group_id, set()).add(path)

    return path_to_groups, path_to_roles, group_to_observed_paths, path_records, group_to_paths


def _select_group_id(path_to_groups: dict[str, set[str]], path: str) -> str:
    groups = sorted(path_to_groups.get(path, set()))
    return groups[0] if groups else "UNKNOWN"


def _select_evidence_role(path_to_roles: dict[str, set[str]], path: str) -> str:
    roles = path_to_roles.get(path, set())
    for role in _ROLE_PRIORITY:
        if role in roles:
            return role
    return "unknown"


def _select_inherited_status(path_records: dict[str, list[dict[str, Any]]], path: str, role: str) -> str:
    records = path_records.get(path, [])
    for record in records:
        if str(record.get("evidence_role", "unknown")) == role:
            return str(record.get("inherited_status", "NOT_COMPUTABLE"))
    if records:
        return str(records[0].get("inherited_status", "NOT_COMPUTABLE"))
    return "NOT_COMPUTABLE"


def _infer_prerequisite_paths(
    *,
    path: str,
    group_id: str,
    likely_generator_script: str,
    group_to_observed_paths: dict[str, set[str]],
    all_known_paths: set[str],
) -> list[str]:
    prerequisites: set[str] = set()

    if likely_generator_script != "NOT_COMPUTABLE":
        prerequisites.add(likely_generator_script)

    for observed_path in group_to_observed_paths.get(group_id, set()):
        if observed_path != path:
            prerequisites.add(observed_path)

    if group_id == "temporal_coherence_chain":
        chain_audit = "out/audit/temporal_coherence_chain_001.latest.json"
        if chain_audit in all_known_paths and chain_audit != path:
            prerequisites.add(chain_audit)
        for candidate in all_known_paths:
            if "temporal_state_diff" in candidate and candidate != path:
                prerequisites.add(candidate)

    return sorted(prerequisites)


def _has_missing_or_unreadable_upstream(
    *, repo_root: Path, prerequisites: list[str]
) -> bool:
    for prereq in prerequisites:
        if not prereq.startswith("out/"):
            continue
        observed, readable, malformed_json = _read_path_state(repo_root, prereq)
        if (not observed) or (not readable) or malformed_json:
            return True
    return False


def _build_recommended_lane(
    *,
    source_usable: bool,
    restoration_items: list[dict[str, Any]],
    unreadable_evidence_paths: list[str],
    restoration_plan_status: str,
    degraded_evidence_inputs: list[str],
) -> tuple[str, str]:
    if not source_usable:
        return (
            "P73_EVIDENCE_INDEX_REGENERATION",
            "P73 evidence index is missing, unreadable, or malformed; regenerate P73 before P74 planning.",
        )

    strategies = [str(item.get("restoration_strategy", "NOT_COMPUTABLE")) for item in restoration_items]
    missing_items = [item for item in restoration_items if not bool(item.get("observed", False))]

    if "SCRIPT_DISCOVERY_REQUIRED" in strategies:
        return (
            "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN",
            "One or more missing evidence paths have no directly inferable generator script; discovery planning is required first.",
        )
    if "UPSTREAM_INPUT_REQUIRED" in strategies:
        return (
            "P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN",
            "One or more missing temporal coherence paths depend on upstream evidence that is missing or not computable.",
        )
    if missing_items and all(
        str(item.get("restoration_strategy")) == "GENERATOR_EXISTS_REGENERATION_PLAN"
        for item in missing_items
    ):
        return (
            "P75_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
            "All missing evidence paths have directly inferable generator scripts; proceed with advisory-only regeneration dry-run planning.",
        )
    if unreadable_evidence_paths:
        return (
            "P75_TEMPORAL_CONTINUITY_UNREADABLE_EVIDENCE_REPAIR_PLAN",
            "One or more evidence paths are unreadable or malformed; repair planning is required before restoration execution.",
        )
    if restoration_plan_status == "RESTORATION_NOT_REQUIRED" and degraded_evidence_inputs:
        return (
            "P75_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
            "Missing/unreadable restoration is not required, but degraded evidence remains and needs repair planning.",
        )
    if restoration_plan_status == "RESTORATION_NOT_REQUIRED" and not degraded_evidence_inputs:
        return (
            "P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
            "No missing or unreadable restoration is required and no degraded evidence remains.",
        )

    return (
        "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN",
        "Restoration signals remain incomplete; conservative generator discovery planning is required before any restoration execution.",
    )


def build_temporal_continuity_missing_evidence_restoration_plan(
    *,
    repo_root: str | Path = ".",
    source_evidence_index_path: str = SOURCE_EVIDENCE_INDEX_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_evidence_index_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)
    source_usable = source_payload is not None
    source_hash = _sha256_file(source_path) if source_usable else "NOT_COMPUTABLE"

    if not source_usable:
        packet_base: dict[str, Any] = {
            "artifact_type": ARTIFACT_TYPE,
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "production_activation": False,
            "canon_promotion": False,
            "forecast_influence": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "repair_authority": False,
            "evidence_generation_authority": False,
            "restoration_execution_authority": False,
            "spine_implementation_authority": False,
            "source_evidence_index_path": source_evidence_index_path,
            "source_evidence_index_observed": source_observed,
            "source_evidence_index_hash": source_hash,
            "source_evidence_index_status": "NOT_COMPUTABLE",
            "source_recommended_next_lane": "NOT_COMPUTABLE",
            "restoration_plan_status": "NOT_COMPUTABLE",
            "restoration_items": [],
            "missing_evidence_paths": [source_evidence_index_path],
            "unreadable_evidence_paths": [],
            "degraded_evidence_inputs": [],
            "inherited_blockers": [f"source_evidence_index_not_computable:{source_evidence_index_path}"],
            "inherited_drift_flags": ["SOURCE_EVIDENCE_INDEX_NOT_COMPUTABLE"],
            "semantic_overlap_flags": [],
            "restoration_strategy_summary": {strategy: 0 for strategy in _STRATEGIES},
            "recommended_next_lane": "P73_EVIDENCE_INDEX_REGENERATION",
            "recommended_next_lane_reason": (
                "P73 evidence index is missing, unreadable, or malformed; regenerate P73 before P74 planning."
            ),
            "denied_authority": sorted(_DENIED_AUTHORITY),
        }
        packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
        return json.loads(
            json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        )

    source_evidence_index_status = str(source_payload.get("evidence_index_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(source_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))

    missing_evidence_paths = _unique_sorted(_as_str_list(source_payload.get("missing_evidence_paths")))
    unreadable_evidence_paths = _unique_sorted(_as_str_list(source_payload.get("unreadable_evidence_paths")))
    observed_evidence_paths = _unique_sorted(_as_str_list(source_payload.get("observed_evidence_paths")))

    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    raw_items = source_payload.get("evidence_items")
    evidence_items = [item for item in raw_items if isinstance(item, dict)] if isinstance(raw_items, list) else []

    (
        path_to_groups,
        path_to_roles,
        group_to_observed_paths,
        path_records,
        group_to_paths,
    ) = _build_path_metadata(evidence_items)

    known_paths = set(missing_evidence_paths) | set(unreadable_evidence_paths) | set(observed_evidence_paths)
    known_paths |= {str(item.get("path")) for item in evidence_items if str(item.get("path", ""))}

    restoration_items: list[dict[str, Any]] = []
    for path in sorted(known_paths):
        observed, readable, malformed_json = _read_path_state(root, path)
        group_id = _select_group_id(path_to_groups, path)
        evidence_role = _select_evidence_role(path_to_roles, path)
        inherited_status = _select_inherited_status(path_records, path, evidence_role)
        likely_generator_script = _infer_likely_generator_script(root, path)
        prerequisite_paths = _infer_prerequisite_paths(
            path=path,
            group_id=group_id,
            likely_generator_script=likely_generator_script,
            group_to_observed_paths=group_to_observed_paths,
            all_known_paths=known_paths,
        )

        if observed and readable and not malformed_json:
            restoration_strategy = "RESTORATION_NOT_REQUIRED"
            blocking_reason = "EVIDENCE_PRESENT_AND_READABLE_P74_PLANNING_ONLY"
        elif observed and ((not readable) or malformed_json or path in unreadable_evidence_paths):
            restoration_strategy = "UNREADABLE_SOURCE_REPAIR_PLAN"
            blocking_reason = "UNREADABLE_OR_MALFORMED_SOURCE_P74_PLANNING_ONLY"
        elif (not observed) or (path in missing_evidence_paths):
            requires_upstream = False
            if group_id == "temporal_coherence_chain":
                requires_upstream = _has_missing_or_unreadable_upstream(
                    repo_root=root, prerequisites=prerequisite_paths
                )
            if requires_upstream:
                restoration_strategy = "UPSTREAM_INPUT_REQUIRED"
                blocking_reason = "UPSTREAM_INPUT_MISSING_OR_NOT_COMPUTABLE_P74_PLANNING_ONLY"
            elif likely_generator_script != "NOT_COMPUTABLE":
                restoration_strategy = "GENERATOR_EXISTS_REGENERATION_PLAN"
                blocking_reason = "GENERATOR_AVAILABLE_BUT_EXECUTION_DENIED_IN_P74"
            else:
                restoration_strategy = "SCRIPT_DISCOVERY_REQUIRED"
                blocking_reason = "NO_DIRECT_GENERATOR_SCRIPT_INFERENCE_P74_PLANNING_ONLY"
        else:
            restoration_strategy = "NOT_COMPUTABLE"
            blocking_reason = "WEAK_OR_INCONSISTENT_SIGNAL_P74_FAIL_CLOSED"

        restoration_items.append(
            {
                "path": path,
                "group_id": group_id,
                "source_category": _source_category(path),
                "evidence_role": evidence_role,
                "inherited_status": inherited_status,
                "observed": observed,
                "readable": readable,
                "malformed_json": malformed_json,
                "restoration_strategy": restoration_strategy,
                "likely_generator_script": likely_generator_script,
                "prerequisite_paths": prerequisite_paths,
                "blocking_reason": blocking_reason,
                "safe_to_restore": False,
            }
        )

    restoration_items = sorted(
        restoration_items,
        key=lambda item: (
            str(item["path"]),
            str(item["group_id"]),
            str(item["restoration_strategy"]),
        ),
    )

    missing_evidence_paths = _unique_sorted(
        [str(item["path"]) for item in restoration_items if not bool(item["observed"])]
    )
    unreadable_evidence_paths = _unique_sorted(
        [
            str(item["path"])
            for item in restoration_items
            if bool(item["observed"]) and ((not bool(item["readable"])) or bool(item["malformed_json"]))
        ]
    )

    if unreadable_evidence_paths:
        restoration_plan_status = "RESTORATION_PLAN_READY_WITH_UNREADABLE_EVIDENCE"
    elif missing_evidence_paths:
        restoration_plan_status = "RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE"
    else:
        restoration_plan_status = "RESTORATION_NOT_REQUIRED"

    restoration_strategy_summary = {
        strategy: sum(
            1
            for item in restoration_items
            if str(item.get("restoration_strategy", "NOT_COMPUTABLE")) == strategy
        )
        for strategy in _STRATEGIES
    }

    recommended_next_lane, recommended_next_lane_reason = _build_recommended_lane(
        source_usable=source_usable,
        restoration_items=restoration_items,
        unreadable_evidence_paths=unreadable_evidence_paths,
        restoration_plan_status=restoration_plan_status,
        degraded_evidence_inputs=degraded_evidence_inputs,
    )

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "spine_implementation_authority": False,
        "source_evidence_index_path": source_evidence_index_path,
        "source_evidence_index_observed": source_observed,
        "source_evidence_index_hash": source_hash,
        "source_evidence_index_status": source_evidence_index_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "restoration_plan_status": restoration_plan_status,
        "restoration_items": restoration_items,
        "missing_evidence_paths": missing_evidence_paths,
        "unreadable_evidence_paths": unreadable_evidence_paths,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "restoration_strategy_summary": restoration_strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_missing_evidence_restoration_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
