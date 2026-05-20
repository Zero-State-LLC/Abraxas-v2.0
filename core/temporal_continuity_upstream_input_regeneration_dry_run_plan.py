from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityUpstreamInputRegenerationDryRunPlan.v1"
SOURCE_UPSTREAM_RESTORATION_PLAN_PATH = "out/temporal_continuity_upstream_input_restoration_plan/latest.json"

_DRY_RUN_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "DRY_RUN_BLOCKED_GENERATORS_MISSING",
    "DRY_RUN_BLOCKED_INPUTS_UNREADABLE",
    "DRY_RUN_READY_WITH_MISSING_INPUTS",
    "DRY_RUN_NOT_REQUIRED",
    "DRY_RUN_READY",
)

_DRY_RUN_STRATEGIES = (
    "UPSTREAM_GENERATOR_DISCOVERY_REQUIRED",
    "UPSTREAM_GENERATOR_IMPLEMENTATION_PLAN",
    "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
    "UPSTREAM_INPUT_REPAIR_PLAN",
    "UPSTREAM_INPUT_NOT_REQUIRED",
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
    "generator_execution_authority",
    "upstream_input_generation_authority",
    "artifact_regeneration_authority",
    "spine_implementation_authority",
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def _build_dry_run_item(source_item: dict[str, Any]) -> dict[str, Any]:
    target_input_path = str(source_item.get("path", ""))
    generator_script = str(source_item.get("likely_upstream_generator_script", "NOT_COMPUTABLE"))
    generator_observed = bool(source_item.get("upstream_generator_observed", False))
    generator_readable = bool(source_item.get("upstream_generator_readable", False))
    restoration_strategy = str(source_item.get("restoration_strategy", "NOT_COMPUTABLE"))
    input_observed = bool(source_item.get("input_observed", False))
    input_readable = bool(source_item.get("input_readable", False))
    malformed_json = bool(source_item.get("malformed_json", False))

    blocked_by_paths: list[str] = []
    future_execution_candidate = False

    if restoration_strategy == "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN":
        if generator_script == "NOT_COMPUTABLE":
            blocked_by_paths.append(target_input_path)
        elif (not generator_observed) or (not generator_readable):
            blocked_by_paths.append(generator_script)
        else:
            future_execution_candidate = True
    elif restoration_strategy == "UPSTREAM_GENERATOR_DISCOVERY_REQUIRED":
        blocked_by_paths.append(target_input_path)
    elif restoration_strategy == "UPSTREAM_GENERATOR_IMPLEMENTATION_PLAN":
        if generator_script != "NOT_COMPUTABLE":
            blocked_by_paths.append(generator_script)
        else:
            blocked_by_paths.append(target_input_path)
    elif restoration_strategy == "UPSTREAM_INPUT_REPAIR_PLAN":
        blocked_by_paths.append(target_input_path)
    elif restoration_strategy == "UPSTREAM_INPUT_NOT_REQUIRED":
        pass
    else:
        blocked_by_paths.append(target_input_path)

    blocked_by_paths = _unique_sorted(blocked_by_paths)

    if future_execution_candidate:
        blocking_reason = "FUTURE_EXECUTION_LANE_REQUIRED_P77_DRY_RUN_ONLY"
    elif restoration_strategy == "UPSTREAM_INPUT_NOT_REQUIRED":
        blocking_reason = "UPSTREAM_INPUT_ALREADY_PRESENT_NO_REGENERATION_REQUIRED"
    elif restoration_strategy == "UPSTREAM_INPUT_REPAIR_PLAN" and input_observed and (
        (not input_readable) or malformed_json
    ):
        blocking_reason = "UPSTREAM_INPUT_UNREADABLE_OR_MALFORMED_P77_DRY_RUN_ONLY"
    else:
        blocking_reason = str(
            source_item.get("blocking_reason", "WEAK_OR_INCONSISTENT_SIGNAL_P77_FAIL_CLOSED")
        )

    proposed_command = (
        f"python {generator_script}"
        if (generator_script != "NOT_COMPUTABLE") and generator_observed and generator_readable
        else "NOT_COMPUTABLE"
    )

    safe_to_execute = False

    return {
        "target_input_path": target_input_path,
        "owning_output_path": str(source_item.get("owning_output_path", "")),
        "group_id": str(source_item.get("group_id", "UNKNOWN")),
        "source_category": str(source_item.get("source_category", "unknown")),
        "prerequisite_role": str(source_item.get("prerequisite_role", "unknown")),
        "restoration_strategy": restoration_strategy,
        "generator_script": generator_script,
        "generator_observed": generator_observed,
        "generator_readable": generator_readable,
        "proposed_command": proposed_command,
        "expected_output_path": target_input_path,
        "blocked_by_paths": blocked_by_paths,
        "future_execution_candidate": future_execution_candidate,
        "blocking_reason": blocking_reason,
        "safe_to_execute": safe_to_execute,
    }


def _build_recommended_lane(
    *,
    source_status: str,
    degraded_evidence_inputs: list[str],
    dry_run_items: list[dict[str, Any]],
    missing_upstream_input_paths: list[str],
) -> tuple[str, str, str]:
    if source_status == "UPSTREAM_GENERATORS_MISSING":
        return (
            "DRY_RUN_BLOCKED_GENERATORS_MISSING",
            "P78_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN",
            "P76 reports missing upstream generators; discovery planning is required before any regeneration plan.",
        )

    if source_status == "UPSTREAM_INPUTS_UNREADABLE":
        return (
            "DRY_RUN_BLOCKED_INPUTS_UNREADABLE",
            "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN",
            "P76 reports unreadable upstream inputs; repair planning is required before regeneration planning.",
        )

    if source_status == "UPSTREAM_RESTORATION_NOT_REQUIRED":
        if degraded_evidence_inputs:
            return (
                "DRY_RUN_NOT_REQUIRED",
                "P78_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
                "Upstream restoration is not required but degraded evidence remains and must be repaired.",
            )
        return (
            "DRY_RUN_NOT_REQUIRED",
            "P78_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
            "Upstream restoration is not required and no degraded evidence remains.",
        )

    if source_status == "UPSTREAM_INPUTS_READY":
        return (
            "DRY_RUN_READY",
            "P78_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
            "All upstream inputs are ready; proceed to downstream artifact regeneration dry-run planning.",
        )

    if source_status == "UPSTREAM_INPUTS_MISSING":
        missing_item_paths = {
            str(item.get("target_input_path", ""))
            for item in dry_run_items
            if str(item.get("target_input_path", "")) in set(missing_upstream_input_paths)
        }
        if (not missing_item_paths) and missing_upstream_input_paths:
            return (
                "DRY_RUN_BLOCKED_GENERATORS_MISSING",
                "P78_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN",
                "Missing inputs were declared but no aligned dry-run items were discovered; fail closed.",
            )

        missing_items = [
            item
            for item in dry_run_items
            if str(item.get("target_input_path", "")) in set(missing_upstream_input_paths)
        ]
        all_missing_have_generator = bool(missing_items) and all(
            bool(item.get("generator_observed", False))
            and bool(item.get("generator_readable", False))
            and str(item.get("generator_script", "NOT_COMPUTABLE")) != "NOT_COMPUTABLE"
            for item in missing_items
        )

        if all_missing_have_generator:
            return (
                "DRY_RUN_READY_WITH_MISSING_INPUTS",
                "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN",
                "All missing upstream inputs have observed/readable generators; execution planning can be prepared.",
            )

        return (
            "DRY_RUN_BLOCKED_GENERATORS_MISSING",
            "P78_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN",
            "At least one missing upstream input lacks an observed/readable generator binding.",
        )

    return (
        "NOT_COMPUTABLE",
        "P76_UPSTREAM_INPUT_RESTORATION_PLAN_REGENERATION",
        "P76 restoration plan status is missing or inconsistent; regenerate P76 before P77 planning.",
    )


def _build_not_computable_packet(
    *,
    source_path: str,
    source_observed: bool,
) -> dict[str, Any]:
    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "dry_run_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "spine_implementation_authority": False,
        "source_upstream_restoration_plan_path": source_path,
        "source_upstream_restoration_plan_observed": source_observed,
        "source_upstream_restoration_plan_hash": "NOT_COMPUTABLE",
        "source_upstream_restoration_plan_status": "NOT_COMPUTABLE",
        "source_recommended_next_lane": "NOT_COMPUTABLE",
        "dry_run_plan_status": "NOT_COMPUTABLE",
        "dry_run_items": [],
        "dry_run_commands": [],
        "missing_upstream_input_paths": [source_path],
        "observed_generator_scripts": [],
        "missing_generator_scripts": [],
        "outputs_blocked_by_upstream_inputs": [],
        "still_blocked_inputs": [source_path],
        "executable_future_candidates": [],
        "degraded_evidence_inputs": [],
        "inherited_blockers": [f"source_upstream_restoration_plan_not_computable:{source_path}"],
        "inherited_drift_flags": ["SOURCE_UPSTREAM_RESTORATION_PLAN_NOT_COMPUTABLE"],
        "semantic_overlap_flags": [],
        "dry_run_strategy_summary": {strategy: 0 for strategy in _DRY_RUN_STRATEGIES},
        "recommended_next_lane": "P76_UPSTREAM_INPUT_RESTORATION_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P76 upstream input restoration plan is missing, unreadable, or malformed; regenerate P76 before P77 planning."
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_upstream_input_regeneration_dry_run_plan(
    *,
    repo_root: str | Path = ".",
    source_upstream_restoration_plan_path: str = SOURCE_UPSTREAM_RESTORATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_upstream_restoration_plan_path
    source_observed = source_path.exists()

    source_payload = _load_json_dict(source_path)
    if source_payload is None:
        return _build_not_computable_packet(
            source_path=source_upstream_restoration_plan_path,
            source_observed=source_observed,
        )

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_status = str(source_payload.get("upstream_restoration_plan_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(source_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))

    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    raw_upstream_input_items = _as_dict_list(source_payload.get("upstream_input_items"))
    dry_run_items = [_build_dry_run_item(item) for item in raw_upstream_input_items]
    dry_run_items = sorted(
        dry_run_items,
        key=lambda item: (
            str(item["target_input_path"]),
            str(item["owning_output_path"]),
            str(item["group_id"]),
        ),
    )

    dry_run_commands = _unique_sorted(
        [
            str(item["proposed_command"])
            for item in dry_run_items
            if str(item["proposed_command"]) != "NOT_COMPUTABLE"
        ]
    )
    missing_upstream_input_paths = _unique_sorted(
        _as_str_list(source_payload.get("missing_upstream_input_paths"))
    )
    observed_generator_scripts = _unique_sorted(
        [
            str(item["generator_script"])
            for item in dry_run_items
            if str(item["generator_script"]) != "NOT_COMPUTABLE"
            and bool(item["generator_observed"])
            and bool(item["generator_readable"])
        ]
    )
    missing_generator_scripts = _unique_sorted(
        [
            str(item["generator_script"])
            for item in dry_run_items
            if str(item["generator_script"]) != "NOT_COMPUTABLE"
            and ((not bool(item["generator_observed"])) or (not bool(item["generator_readable"])))
        ]
    )

    outputs_blocked_by_upstream_inputs = [
        item
        for item in _as_dict_list(source_payload.get("outputs_blocked_by_upstream_inputs"))
    ]

    still_blocked_inputs = _unique_sorted(
        [
            str(item["target_input_path"])
            for item in dry_run_items
            if not bool(item["safe_to_execute"])
            and str(item["target_input_path"]) in set(missing_upstream_input_paths)
        ]
    )
    executable_future_candidates = _unique_sorted(
        [
            str(item["target_input_path"])
            for item in dry_run_items
            if bool(item["future_execution_candidate"])
        ]
    )

    dry_run_strategy_summary = {
        strategy: sum(
            1 for item in dry_run_items if str(item.get("restoration_strategy", "NOT_COMPUTABLE")) == strategy
        )
        for strategy in _DRY_RUN_STRATEGIES
    }

    dry_run_plan_status, recommended_next_lane, recommended_next_lane_reason = _build_recommended_lane(
        source_status=source_status,
        degraded_evidence_inputs=degraded_evidence_inputs,
        dry_run_items=dry_run_items,
        missing_upstream_input_paths=missing_upstream_input_paths,
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "dry_run_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "spine_implementation_authority": False,
        "source_upstream_restoration_plan_path": source_upstream_restoration_plan_path,
        "source_upstream_restoration_plan_observed": source_observed,
        "source_upstream_restoration_plan_hash": source_hash,
        "source_upstream_restoration_plan_status": source_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "dry_run_plan_status": dry_run_plan_status,
        "dry_run_items": dry_run_items,
        "dry_run_commands": dry_run_commands,
        "missing_upstream_input_paths": missing_upstream_input_paths,
        "observed_generator_scripts": observed_generator_scripts,
        "missing_generator_scripts": missing_generator_scripts,
        "outputs_blocked_by_upstream_inputs": outputs_blocked_by_upstream_inputs,
        "still_blocked_inputs": still_blocked_inputs,
        "executable_future_candidates": executable_future_candidates,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "dry_run_strategy_summary": dry_run_strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_upstream_input_regeneration_dry_run_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
