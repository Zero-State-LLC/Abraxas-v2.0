from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityMissingEvidenceRestorationPlan.v1"
SOURCE_EVIDENCE_INDEX_PATH = "out/temporal_continuity_evidence_index/latest.json"

_RESTORATION_STRATEGIES = (
    "SCRIPT_DISCOVERY_REQUIRED",
    "GENERATOR_EXISTS_REGENERATION_PLAN",
    "UPSTREAM_INPUT_REQUIRED",
    "UNREADABLE_SOURCE_REPAIR_PLAN",
    "RESTORATION_NOT_REQUIRED",
    "NOT_COMPUTABLE",
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

_ROLE_PRIORITY = {
    "missing_path": 0,
    "unknown": 1,
    "degraded_input": 2,
    "blocker_path": 3,
    "semantic_overlap_path": 4,
    "observed_path": 5,
}

_INDEX_SUFFIX_RE = re.compile(r"_\d+$")
_TEMPORAL_COHERENCE_CHAIN_RECEIPT_PATH = "out/audit/temporal_coherence_chain_001.latest.json"


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


def _infer_likely_generator_script(root: Path, path: str) -> str:
    file_name = Path(path).name
    if not file_name.endswith(".json"):
        return "NOT_COMPUTABLE"

    stem = file_name[: -len(".json")]
    if stem.endswith(".latest"):
        stem = stem[: -len(".latest")]
    stem = _INDEX_SUFFIX_RE.sub("", stem)
    if not stem:
        return "NOT_COMPUTABLE"

    candidate = f"scripts/run_{stem}.py"
    if (root / candidate).exists():
        return candidate
    return "NOT_COMPUTABLE"


def _path_state(root: Path, path: str) -> dict[str, bool]:
    target = root / path
    if not target.exists():
        return {"observed": False, "readable": False, "malformed_json": False}

    try:
        raw = target.read_bytes()
    except OSError:
        return {"observed": True, "readable": False, "malformed_json": False}

    malformed = False
    if path.endswith(".json"):
        try:
            json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            malformed = True

    return {"observed": True, "readable": True, "malformed_json": malformed}


def _infer_prerequisites(
    *,
    path: str,
    group_id: str,
    likely_generator_script: str,
    group_paths: dict[str, set[str]],
    path_status: dict[str, dict[str, bool]],
) -> list[str]:
    prerequisites: set[str] = set()

    if likely_generator_script != "NOT_COMPUTABLE":
        prerequisites.add(likely_generator_script)

    if group_id == "temporal_coherence_chain":
        chain_receipt = _TEMPORAL_COHERENCE_CHAIN_RECEIPT_PATH
        if path != chain_receipt:
            prerequisites.add(chain_receipt)
        for group_path in sorted(group_paths.get(group_id, set())):
            if group_path == path:
                continue
            state = path_status.get(group_path)
            if state is None:
                continue
            if state["observed"] and state["readable"] and not state["malformed_json"]:
                prerequisites.add(group_path)

    return sorted(prerequisites)


def _is_ready_prerequisite(root: Path, path_status: dict[str, dict[str, bool]], prerequisite: str) -> bool:
    state = path_status.get(prerequisite)
    if state is None:
        state = _path_state(root, prerequisite)
        path_status[prerequisite] = state
    return state["observed"] and state["readable"] and not state["malformed_json"]


def _missing_prerequisites(
    *,
    root: Path,
    path_status: dict[str, dict[str, bool]],
    prerequisite_paths: list[str],
) -> list[str]:
    return sorted(
        prerequisite
        for prerequisite in prerequisite_paths
        if not _is_ready_prerequisite(root, path_status, prerequisite)
    )


def _determine_strategy(
    *,
    root: Path,
    source_usable: bool,
    observed: bool,
    readable: bool,
    malformed_json: bool,
    group_id: str,
    path: str,
    likely_generator_script: str,
    prerequisite_paths: list[str],
    path_status: dict[str, dict[str, bool]],
) -> tuple[str, str]:
    if not source_usable:
        return "NOT_COMPUTABLE", "SOURCE_EVIDENCE_INDEX_NOT_COMPUTABLE"

    if observed and ((not readable) or malformed_json):
        return "UNREADABLE_SOURCE_REPAIR_PLAN", "SOURCE_UNREADABLE_OR_MALFORMED"

    if observed and readable and not malformed_json:
        return "RESTORATION_NOT_REQUIRED", "RESTORATION_NOT_REQUIRED_PATH_READABLE"

    if not observed:
        missing_prerequisites = _missing_prerequisites(
            root=root,
            path_status=path_status,
            prerequisite_paths=prerequisite_paths,
        )
        if missing_prerequisites:
            return (
                "UPSTREAM_INPUT_REQUIRED",
                "UPSTREAM_PREREQUISITES_MISSING_OR_NOT_COMPUTABLE:"
                + "|".join(missing_prerequisites),
            )
        if group_id == "temporal_coherence_chain" and path != _TEMPORAL_COHERENCE_CHAIN_RECEIPT_PATH:
            chain_receipt_state = path_status.get(_TEMPORAL_COHERENCE_CHAIN_RECEIPT_PATH)
            if chain_receipt_state is not None and not chain_receipt_state["observed"]:
                return (
                    "UPSTREAM_INPUT_REQUIRED",
                    "UPSTREAM_TEMPORAL_COHERENCE_CHAIN_MISSING",
                )
        if likely_generator_script != "NOT_COMPUTABLE":
            return "GENERATOR_EXISTS_REGENERATION_PLAN", "PLANNING_ONLY_NO_EXECUTION_AUTHORITY"
        return "SCRIPT_DISCOVERY_REQUIRED", "NO_KNOWN_GENERATOR_SCRIPT"

    return "NOT_COMPUTABLE", "INSUFFICIENT_SIGNAL"


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
            "restoration_strategy_summary": {strategy: 0 for strategy in _RESTORATION_STRATEGIES},
            "recommended_next_lane": "P73_EVIDENCE_INDEX_REGENERATION",
            "recommended_next_lane_reason": (
                "P73 evidence index is missing, unreadable, or malformed; regenerate P73 before restoration planning."
            ),
            "denied_authority": sorted(_DENIED_AUTHORITY),
        }
        packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
        return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))

    missing_evidence_paths = _as_str_list(source_payload.get("missing_evidence_paths"))
    unreadable_evidence_paths = _as_str_list(source_payload.get("unreadable_evidence_paths"))
    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    missing_set = set(missing_evidence_paths)
    unreadable_set = set(unreadable_evidence_paths)

    raw_evidence_items = source_payload.get("evidence_items")
    evidence_items = [item for item in raw_evidence_items if isinstance(item, dict)] if isinstance(raw_evidence_items, list) else []

    grouped_entries: dict[tuple[str, str], list[dict[str, Any]]] = {}
    group_paths: dict[str, set[str]] = {}

    for item in evidence_items:
        path = str(item.get("path", ""))
        group_id = str(item.get("group_id", "UNKNOWN"))
        if not path:
            continue
        grouped_entries.setdefault((path, group_id), []).append(item)
        group_paths.setdefault(group_id, set()).add(path)

    for missing_path in missing_set | unreadable_set:
        if not any(path == missing_path for path, _ in grouped_entries):
            grouped_entries.setdefault((missing_path, "UNKNOWN"), []).append(
                {
                    "path": missing_path,
                    "group_id": "UNKNOWN",
                    "evidence_role": "unknown",
                    "inherited_status": "NOT_COMPUTABLE",
                    "source_category": _source_category(missing_path),
                }
            )

    path_status: dict[str, dict[str, bool]] = {}
    for path, _group_id in grouped_entries:
        raw_entries = grouped_entries[(path, _group_id)]
        any_observed = any(bool(entry.get("observed", False)) for entry in raw_entries)
        any_readable = any(bool(entry.get("readable", False)) for entry in raw_entries)
        any_malformed = any(bool(entry.get("malformed_json", False)) for entry in raw_entries)
        status = (
            {
                "observed": any_observed,
                "readable": any_readable,
                "malformed_json": any_malformed,
            }
            if any_observed or any_readable or any_malformed
            else _path_state(root, path)
        )
        if path in missing_set:
            status = {"observed": False, "readable": False, "malformed_json": False}
        elif path in unreadable_set:
            status = {
                "observed": True,
                "readable": False,
                "malformed_json": status["malformed_json"],
            }
        path_status[path] = status

    restoration_items: list[dict[str, Any]] = []
    for path, group_id in sorted(grouped_entries.keys(), key=lambda item: (item[0], item[1])):
        entries = sorted(
            grouped_entries[(path, group_id)],
            key=lambda item: _ROLE_PRIORITY.get(str(item.get("evidence_role", "unknown")), 99),
        )
        representative = entries[0]
        evidence_role = str(representative.get("evidence_role", "unknown"))
        inherited_status = str(representative.get("inherited_status", "NOT_COMPUTABLE"))
        source_category = str(representative.get("source_category", _source_category(path)))

        state = path_status[path]
        likely_generator_script = _infer_likely_generator_script(root, path)
        prerequisite_paths = _infer_prerequisites(
            path=path,
            group_id=group_id,
            likely_generator_script=likely_generator_script,
            group_paths=group_paths,
            path_status=path_status,
        )
        restoration_strategy, blocking_reason = _determine_strategy(
            root=root,
            source_usable=source_usable,
            observed=state["observed"],
            readable=state["readable"],
            malformed_json=state["malformed_json"],
            group_id=group_id,
            path=path,
            likely_generator_script=likely_generator_script,
            prerequisite_paths=prerequisite_paths,
            path_status=path_status,
        )

        restoration_items.append(
            {
                "path": path,
                "group_id": group_id,
                "source_category": source_category,
                "evidence_role": evidence_role,
                "inherited_status": inherited_status,
                "observed": state["observed"],
                "readable": state["readable"],
                "malformed_json": state["malformed_json"],
                "restoration_strategy": restoration_strategy,
                "likely_generator_script": likely_generator_script,
                "prerequisite_paths": prerequisite_paths,
                "blocking_reason": blocking_reason,
                "safe_to_restore": False,
            }
        )

    restoration_items = sorted(
        restoration_items,
        key=lambda item: (item["path"], item["group_id"], item["restoration_strategy"]),
    )

    restoration_strategy_summary = {
        strategy: sum(1 for item in restoration_items if item["restoration_strategy"] == strategy)
        for strategy in _RESTORATION_STRATEGIES
    }

    missing_items = [item for item in restoration_items if item["path"] in missing_set]

    if unreadable_evidence_paths:
        restoration_plan_status = "RESTORATION_PLAN_READY_WITH_UNREADABLE_EVIDENCE"
    elif missing_evidence_paths:
        restoration_plan_status = "RESTORATION_PLAN_READY_WITH_MISSING_EVIDENCE"
    else:
        restoration_plan_status = "RESTORATION_NOT_REQUIRED"

    has_script_discovery = restoration_strategy_summary["SCRIPT_DISCOVERY_REQUIRED"] > 0
    has_upstream_required = restoration_strategy_summary["UPSTREAM_INPUT_REQUIRED"] > 0

    if unreadable_evidence_paths:
        recommended_next_lane = "P75_TEMPORAL_CONTINUITY_UNREADABLE_EVIDENCE_REPAIR_PLAN"
        recommended_next_lane_reason = (
            "One or more indexed evidence paths are unreadable or malformed; advisory repair planning is required before restoration execution."
        )
    elif has_script_discovery:
        recommended_next_lane = "P75_TEMPORAL_CONTINUITY_GENERATOR_DISCOVERY_PLAN"
        recommended_next_lane_reason = (
            "At least one missing evidence path has no directly inferable generator script; deterministic script discovery planning is required first."
        )
    elif has_upstream_required:
        recommended_next_lane = "P75_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN"
        recommended_next_lane_reason = (
            "At least one missing evidence path depends on missing or not-computable upstream prerequisites; upstream restoration planning is required first."
        )
    elif missing_items and all(
        item["restoration_strategy"] == "GENERATOR_EXISTS_REGENERATION_PLAN" for item in missing_items
    ):
        recommended_next_lane = "P75_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN"
        recommended_next_lane_reason = (
            "All missing evidence paths have directly inferable generator scripts and no blocked prerequisites; regeneration dry-run planning is the next advisory lane."
        )
    elif restoration_plan_status == "RESTORATION_NOT_REQUIRED" and degraded_evidence_inputs:
        recommended_next_lane = "P75_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"
        recommended_next_lane_reason = (
            "No missing or unreadable evidence remains, but degraded evidence inputs are inherited from P73 and require advisory repair planning."
        )
    elif restoration_plan_status == "RESTORATION_NOT_REQUIRED" and not degraded_evidence_inputs:
        recommended_next_lane = "P75_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE"
        recommended_next_lane_reason = (
            "No missing, unreadable, or degraded evidence remains; safe to proceed to advisory spine implementation planning gate."
        )
    else:
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Restoration strategy state is ambiguous under current source evidence; manual advisory triage is required."
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
        "source_evidence_index_status": str(source_payload.get("evidence_index_status", "NOT_COMPUTABLE")),
        "source_recommended_next_lane": str(source_payload.get("recommended_next_lane", "NOT_COMPUTABLE")),
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
