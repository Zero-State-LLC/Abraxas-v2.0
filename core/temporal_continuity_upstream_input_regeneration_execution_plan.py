from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityUpstreamInputRegenerationExecutionPlan.v1"
SOURCE_DRY_RUN_PLAN_PATH = "out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json"

_EXECUTION_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "EXECUTION_PLAN_BLOCKED",
    "EXECUTION_PLAN_READY",
    "EXECUTION_PLAN_NOT_REQUIRED",
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
    "execution_authority",
    "spine_implementation_authority",
)

_COMMAND_PATTERN = re.compile(r"^python scripts/[A-Za-z0-9_./-]+\.py$")
_DESTRUCTIVE_TOKENS = ("--delete", "--remove", "--rm", "--force", "-rf")
_CHAINING_TOKENS = (";", "&&", "||", "|", ">", "<", "`", "$(")


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


def _command_shape_allowed(command: str) -> bool:
    if not _COMMAND_PATTERN.fullmatch(command):
        return False
    return not any(token in command for token in (*_CHAINING_TOKENS, *_DESTRUCTIVE_TOKENS))


def _script_readable(root: Path, script_path: str) -> bool:
    if not script_path or script_path == "NOT_COMPUTABLE":
        return False
    target = root / script_path
    if not target.exists():
        return False
    try:
        target.read_bytes()
    except OSError:
        return False
    return True


def _build_lane_decision(
    *,
    source_status: str,
    degraded_evidence_inputs: list[str],
    executable_future_candidates: list[str],
) -> tuple[str, str, str]:
    if source_status == "DRY_RUN_READY_WITH_MISSING_INPUTS" and executable_future_candidates:
        return (
            "EXECUTION_PLAN_READY",
            "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE",
            "P77 identified executable future candidates; authorization gate is required before any execution.",
        )

    if source_status == "DRY_RUN_BLOCKED_GENERATORS_MISSING":
        return (
            "EXECUTION_PLAN_BLOCKED",
            "P79_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN",
            "P77 remains blocked by missing generator bindings.",
        )

    if source_status == "DRY_RUN_BLOCKED_INPUTS_UNREADABLE":
        return (
            "EXECUTION_PLAN_BLOCKED",
            "P79_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN",
            "P77 remains blocked by unreadable upstream inputs.",
        )

    if source_status == "DRY_RUN_READY":
        return (
            "EXECUTION_PLAN_NOT_REQUIRED",
            "P79_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
            "P77 reports upstream inputs ready; upstream execution planning is not required.",
        )

    if source_status == "DRY_RUN_NOT_REQUIRED":
        if degraded_evidence_inputs:
            return (
                "EXECUTION_PLAN_NOT_REQUIRED",
                "P79_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
                "No upstream regeneration required, but degraded evidence remains.",
            )
        return (
            "EXECUTION_PLAN_NOT_REQUIRED",
            "P79_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
            "No upstream regeneration required and no degraded evidence remains.",
        )

    return (
        "NOT_COMPUTABLE",
        "P77_DRY_RUN_PLAN_REGENERATION",
        "P77 dry-run plan status is missing or inconsistent; regenerate P77 before P78 planning.",
    )


def _build_not_computable_packet(*, source_path: str, source_observed: bool) -> dict[str, Any]:
    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "execution_plan_only": True,
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
        "execution_authority": False,
        "spine_implementation_authority": False,
        "source_dry_run_plan_path": source_path,
        "source_dry_run_plan_observed": source_observed,
        "source_dry_run_plan_hash": "NOT_COMPUTABLE",
        "source_dry_run_plan_status": "NOT_COMPUTABLE",
        "source_recommended_next_lane": "NOT_COMPUTABLE",
        "execution_plan_status": "NOT_COMPUTABLE",
        "execution_steps": [],
        "command_allowlist": [],
        "expected_outputs": [],
        "preflight_checks": [],
        "post_run_validations": [],
        "still_blocked_inputs": [source_path],
        "executable_future_candidates": [],
        "inherited_dry_run_commands": [],
        "degraded_evidence_inputs": [],
        "inherited_blockers": [f"source_dry_run_plan_not_computable:{source_path}"],
        "inherited_drift_flags": ["SOURCE_DRY_RUN_PLAN_NOT_COMPUTABLE"],
        "semantic_overlap_flags": [],
        "execution_strategy_summary": {
            "total_candidates": 0,
            "allowlisted_commands": 0,
            "blocked_candidates": 0,
            "execution_steps_planned": 0,
        },
        "recommended_next_lane": "P77_DRY_RUN_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P77 dry-run plan is missing, unreadable, or malformed; regenerate P77 before P78 execution planning."
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_upstream_input_regeneration_execution_plan(
    *,
    repo_root: str | Path = ".",
    source_dry_run_plan_path: str = SOURCE_DRY_RUN_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_dry_run_plan_path
    source_observed = source_path.exists()

    source_payload = _load_json_dict(source_path)
    if source_payload is None:
        return _build_not_computable_packet(
            source_path=source_dry_run_plan_path,
            source_observed=source_observed,
        )

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_status = str(source_payload.get("dry_run_plan_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(source_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))

    inherited_dry_run_commands = _as_str_list(source_payload.get("dry_run_commands"))
    executable_future_candidates = _as_str_list(source_payload.get("executable_future_candidates"))
    still_blocked_inputs = _as_str_list(source_payload.get("still_blocked_inputs"))
    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))
    dry_run_items = _as_dict_list(source_payload.get("dry_run_items"))

    command_set = set(inherited_dry_run_commands)
    candidate_set = set(executable_future_candidates)

    execution_steps: list[dict[str, Any]] = []
    command_allowlist: list[dict[str, Any]] = []
    expected_outputs: list[dict[str, Any]] = []
    preflight_checks: list[dict[str, Any]] = []
    post_run_validations: list[dict[str, Any]] = []

    for index, item in enumerate(
        sorted(
            dry_run_items,
            key=lambda value: (
                str(value.get("target_input_path", "")),
                str(value.get("owning_output_path", "")),
                str(value.get("group_id", "")),
            ),
        ),
        start=1,
    ):
        target_input_path = str(item.get("target_input_path", ""))
        proposed_command = str(item.get("proposed_command", "NOT_COMPUTABLE"))
        generator_script = str(item.get("generator_script", "NOT_COMPUTABLE"))
        expected_output_path = str(item.get("expected_output_path", ""))
        owning_output_path = str(item.get("owning_output_path", ""))
        group_id = str(item.get("group_id", "UNKNOWN"))
        prerequisite_role = str(item.get("prerequisite_role", "unknown"))
        candidate_selected = target_input_path in candidate_set
        generator_readable = _script_readable(root, generator_script)
        expected_matches_target = expected_output_path == target_input_path
        command_inherited = proposed_command in command_set
        allowlisted = (
            candidate_selected
            and command_inherited
            and generator_readable
            and expected_matches_target
            and _command_shape_allowed(proposed_command)
        )

        if candidate_selected:
            blocking_reason = (
                "FUTURE_AUTHORIZATION_GATE_REQUIRED_P78_EXECUTION_PLAN_ONLY"
                if allowlisted
                else "P78_ALLOWLIST_CRITERIA_NOT_SATISFIED"
            )
            execution_steps.append(
                {
                    "step_id": f"step_{index:03d}",
                    "target_input_path": target_input_path,
                    "proposed_command": proposed_command,
                    "generator_script": generator_script,
                    "expected_output_path": expected_output_path,
                    "owning_output_path": owning_output_path,
                    "group_id": group_id,
                    "prerequisite_role": prerequisite_role,
                    "preflight_required": True,
                    "post_run_validation_required": True,
                    "rollback_strategy": "NO_OP_P78_ADVISORY_ONLY_EXECUTION_NOT_PERMITTED",
                    "execution_authorized": False,
                    "blocking_reason": blocking_reason,
                }
            )
            command_allowlist.append(
                {
                    "command": proposed_command,
                    "generator_script": generator_script,
                    "expected_output_path": expected_output_path,
                    "allowlisted_for_future_execution": allowlisted,
                    "execution_authorized": False,
                }
            )
            expected_outputs.append(
                {
                    "path": expected_output_path,
                    "produced_by_command": proposed_command,
                    "currently_observed": (root / expected_output_path).exists(),
                    "validation_required": True,
                    "overwrite_policy": "ALLOW_OVERWRITE_ONLY_IN_AUTHORIZED_P79_PLUS_LANE",
                }
            )
            preflight_checks.extend(
                [
                    {
                        "check_id": f"preflight_{index:03d}_generator_readable",
                        "check_type": "generator_script_readable",
                        "path": generator_script,
                        "required_status": "READABLE",
                        "failure_action": "FAIL_CLOSED_REQUIRE_GENERATOR_DISCOVERY_OR_REPAIR_PLAN",
                    },
                    {
                        "check_id": f"preflight_{index:03d}_command_allowlisted",
                        "check_type": "command_allowlist_compliance",
                        "path": proposed_command,
                        "required_status": "ALLOWLISTED",
                        "failure_action": "BLOCK_EXECUTION_AND_RETURN_TO_P78_PLANNING",
                    },
                ]
            )
            post_run_validations.extend(
                [
                    {
                        "validation_id": f"postrun_{index:03d}_output_exists",
                        "validation_type": "expected_output_observed",
                        "path": expected_output_path,
                        "required_status": "OBSERVED",
                        "failure_action": "FAIL_CLOSED_REVERT_AND_ROUTE_TO_INPUT_REPAIR_PLAN",
                    },
                    {
                        "validation_id": f"postrun_{index:03d}_output_readable_json",
                        "validation_type": "expected_output_readable_json",
                        "path": expected_output_path,
                        "required_status": "READABLE_JSON",
                        "failure_action": "FAIL_CLOSED_REVERT_AND_ROUTE_TO_INPUT_REPAIR_PLAN",
                    },
                ]
            )

    execution_steps = sorted(execution_steps, key=lambda item: str(item["step_id"]))
    command_allowlist = sorted(
        command_allowlist,
        key=lambda item: (
            str(item["command"]),
            str(item["generator_script"]),
            str(item["expected_output_path"]),
        ),
    )
    expected_outputs = sorted(expected_outputs, key=lambda item: str(item["path"]))
    preflight_checks = sorted(preflight_checks, key=lambda item: str(item["check_id"]))
    post_run_validations = sorted(post_run_validations, key=lambda item: str(item["validation_id"]))

    execution_plan_status, recommended_next_lane, recommended_next_lane_reason = _build_lane_decision(
        source_status=source_status,
        degraded_evidence_inputs=degraded_evidence_inputs,
        executable_future_candidates=executable_future_candidates,
    )
    if (
        source_status == "DRY_RUN_READY_WITH_MISSING_INPUTS"
        and not executable_future_candidates
        and execution_plan_status == "NOT_COMPUTABLE"
    ):
        recommended_next_lane_reason = (
            "P77 reports missing inputs but no executable candidates were provided; regenerate P77 before P78 planning."
        )

    allowlisted_count = sum(1 for item in command_allowlist if bool(item["allowlisted_for_future_execution"]))
    strategy_summary = {
        "total_candidates": len(executable_future_candidates),
        "allowlisted_commands": allowlisted_count,
        "blocked_candidates": max(len(executable_future_candidates) - allowlisted_count, 0),
        "execution_steps_planned": len(execution_steps),
    }

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "execution_plan_only": True,
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
        "execution_authority": False,
        "spine_implementation_authority": False,
        "source_dry_run_plan_path": source_dry_run_plan_path,
        "source_dry_run_plan_observed": source_observed,
        "source_dry_run_plan_hash": source_hash,
        "source_dry_run_plan_status": source_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "execution_plan_status": (
            execution_plan_status
            if execution_plan_status in _EXECUTION_PLAN_STATUSES
            else "NOT_COMPUTABLE"
        ),
        "execution_steps": execution_steps,
        "command_allowlist": command_allowlist,
        "expected_outputs": expected_outputs,
        "preflight_checks": preflight_checks,
        "post_run_validations": post_run_validations,
        "still_blocked_inputs": still_blocked_inputs,
        "executable_future_candidates": executable_future_candidates,
        "inherited_dry_run_commands": inherited_dry_run_commands,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "execution_strategy_summary": strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_upstream_input_regeneration_execution_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
