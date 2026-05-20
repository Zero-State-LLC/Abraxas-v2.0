from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityUpstreamInputRegenerationAuthorizationGate.v1"
SOURCE_EXECUTION_PLAN_PATH = "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json"
AUTHORIZATION_RECORD_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record/latest.json"
)

_AUTHORIZATION_GATE_STATUSES = (
    "NOT_COMPUTABLE",
    "AUTHORIZATION_BLOCKED",
    "AUTHORIZATION_ELIGIBLE",
    "AUTHORIZATION_NOT_REQUIRED",
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
    "authorization_authority",
    "spine_implementation_authority",
)

_REQUIRED_RECORD_FIELDS = [
    "artifact_type",
    "authorization_scope",
    "authorized_commands",
    "authorized_expected_outputs",
    "source_authorization_gate_hash",
    "operator_approval_required",
    "operator_approved",
    "authorization_granted",
    "execution_authority",
    "packet_hash",
]


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


def _authorization_required_record(*, required: bool) -> dict[str, Any]:
    if required:
        return {
            "required": True,
            "required_record_type": "OPERATOR_AUTHORIZATION_TOKEN_V1",
            "required_record_path": AUTHORIZATION_RECORD_PATH,
            "required_fields": list(_REQUIRED_RECORD_FIELDS),
            "authorization_token_observed": False,
            "authorization_token_hash": "NOT_COMPUTABLE",
        }
    return {
        "required": False,
        "required_record_type": "NOT_REQUIRED",
        "required_record_path": "NOT_COMPUTABLE",
        "required_fields": [],
        "authorization_token_observed": False,
        "authorization_token_hash": "NOT_COMPUTABLE",
    }


def _not_computable_packet(*, source_path: str, source_observed: bool) -> dict[str, Any]:
    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_gate_only": True,
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
        "authorization_authority": False,
        "spine_implementation_authority": False,
        "source_execution_plan_path": source_path,
        "source_execution_plan_observed": source_observed,
        "source_execution_plan_hash": "NOT_COMPUTABLE",
        "source_execution_plan_status": "NOT_COMPUTABLE",
        "source_recommended_next_lane": "NOT_COMPUTABLE",
        "authorization_gate_status": "NOT_COMPUTABLE",
        "authorization_eligible": False,
        "authorization_granted": False,
        "authorization_required_record": _authorization_required_record(required=False),
        "eligible_execution_steps": [],
        "blocked_execution_steps": [],
        "eligible_commands": [],
        "blocked_commands": [],
        "operator_review_requirements": [],
        "preflight_review_requirements": [],
        "post_authorization_requirements": [],
        "degraded_evidence_inputs": [],
        "inherited_blockers": [f"source_execution_plan_not_computable:{source_path}"],
        "inherited_drift_flags": ["SOURCE_EXECUTION_PLAN_NOT_COMPUTABLE"],
        "semantic_overlap_flags": [],
        "authorization_strategy_summary": {
            "source_execution_steps_count": 0,
            "eligible_execution_steps_count": 0,
            "blocked_execution_steps_count": 0,
            "eligible_commands_count": 0,
            "blocked_commands_count": 0,
            "operator_review_requirements_count": 0,
            "preflight_review_requirements_count": 0,
            "post_authorization_requirements_count": 0,
            "authorization_required": False,
        },
        "recommended_next_lane": "P78_EXECUTION_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P78 execution plan is missing, unreadable, or malformed; regenerate P78 before P79 authorization gating."
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _normalized_step(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "step_id": str(step.get("step_id", "NOT_COMPUTABLE")),
        "target_input_path": str(step.get("target_input_path", "NOT_COMPUTABLE")),
        "proposed_command": str(step.get("proposed_command", "NOT_COMPUTABLE")),
        "generator_script": str(step.get("generator_script", "NOT_COMPUTABLE")),
        "expected_output_path": str(step.get("expected_output_path", "NOT_COMPUTABLE")),
        "owning_output_path": str(step.get("owning_output_path", "NOT_COMPUTABLE")),
        "group_id": str(step.get("group_id", "NOT_COMPUTABLE")),
        "prerequisite_role": str(step.get("prerequisite_role", "NOT_COMPUTABLE")),
        "preflight_required": bool(step.get("preflight_required", True)),
        "post_run_validation_required": bool(step.get("post_run_validation_required", True)),
        "rollback_strategy": str(step.get("rollback_strategy", "NO_OP_P79_ADVISORY_ONLY")),
        "execution_authorized": False,
        "blocking_reason": str(step.get("blocking_reason", "NOT_COMPUTABLE")),
    }


def _normalized_command(command: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": str(command.get("command", "NOT_COMPUTABLE")),
        "generator_script": str(command.get("generator_script", "NOT_COMPUTABLE")),
        "expected_output_path": str(command.get("expected_output_path", "NOT_COMPUTABLE")),
        "allowlisted_for_future_execution": bool(
            command.get("allowlisted_for_future_execution", False)
        ),
        "execution_authorized": False,
    }


def _sort_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        steps,
        key=lambda item: (
            str(item["step_id"]),
            str(item["target_input_path"]),
            str(item["proposed_command"]),
        ),
    )


def _sort_commands(commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        commands,
        key=lambda item: (
            str(item["command"]),
            str(item["generator_script"]),
            str(item["expected_output_path"]),
        ),
    )


def _operator_review_requirements(
    *, eligible_commands: list[dict[str, Any]], eligible_steps: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    commands = [str(item["command"]) for item in eligible_commands]
    outputs = [str(item["expected_output_path"]) for item in eligible_commands]
    scope = [str(item["target_input_path"]) for item in eligible_steps]
    requirements = [
        {
            "requirement_id": "operator_review_001_approval",
            "requirement_type": "operator_approval",
            "requirement": "Explicit operator approval is required before any future authorization record can be generated.",
        },
        {
            "requirement_id": "operator_review_002_scope",
            "requirement_type": "authorization_scope",
            "scope_paths": sorted(scope),
            "requirement": "Authorization scope must match the eligible execution step input paths exactly.",
        },
        {
            "requirement_id": "operator_review_003_commands",
            "requirement_type": "command_review",
            "commands": sorted(commands),
            "requirement": "Authorized commands must match the P79 eligible command allowlist exactly.",
        },
        {
            "requirement_id": "operator_review_004_outputs",
            "requirement_type": "expected_output_review",
            "expected_outputs": sorted(outputs),
            "requirement": "Authorized expected outputs must match the eligible command output set exactly.",
        },
        {
            "requirement_id": "operator_review_005_rollback",
            "requirement_type": "rollback_no_op_review",
            "requirement": "Rollback posture remains no-op/advisory-only until a future authorization record explicitly permits execution.",
        },
        {
            "requirement_id": "operator_review_006_validation",
            "requirement_type": "validation_check_review",
            "requirement": "Preflight and post-run validation requirements must be reviewed before any future authorization record is issued.",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["requirement_id"]))


def _post_authorization_requirements() -> list[dict[str, Any]]:
    requirements = [
        {
            "requirement_id": "post_authorization_001_future_record_only",
            "requirement_type": "future_authorization_record_generation",
            "target_record_path": AUTHORIZATION_RECORD_PATH,
            "execution_authority": False,
            "generator_execution_authority": False,
            "artifact_regeneration_authority": False,
            "requirement": "Only a future operator authorization record may be generated after P79; P79 itself never grants execution authority or executes commands.",
        }
    ]
    return sorted(requirements, key=lambda item: str(item["requirement_id"]))


def _build_status_and_recommendation(
    *,
    source_status: str,
    eligible_steps: list[dict[str, Any]],
    execution_steps: list[dict[str, Any]],
    eligible_commands: list[dict[str, Any]],
    degraded_evidence_inputs: list[str],
    source_recommended_next_lane: str,
) -> tuple[str, bool, str, str]:
    if source_status == "EXECUTION_PLAN_READY":
        if not execution_steps:
            return (
                "NOT_COMPUTABLE",
                False,
                "P78_EXECUTION_PLAN_REGENERATION",
                "P78 reported EXECUTION_PLAN_READY without execution steps; regenerate P78 before P79 authorization gating.",
            )
        if eligible_commands and eligible_steps:
            return (
                "AUTHORIZATION_ELIGIBLE",
                True,
                "P80_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_RECORD_PLAN",
                "P78 is structurally eligible for future operator authorization, but P79 remains advisory-only and requires a future authorization record plan.",
            )
        return (
            "AUTHORIZATION_BLOCKED",
            False,
            "P80_TEMPORAL_CONTINUITY_EXECUTION_BLOCKER_REPAIR_PLAN",
            "P78 reported EXECUTION_PLAN_READY but no allowlisted future-execution command remained eligible; repair the execution blockers before any authorization planning.",
        )

    if source_status == "EXECUTION_PLAN_BLOCKED":
        return (
            "AUTHORIZATION_BLOCKED",
            False,
            "P80_TEMPORAL_CONTINUITY_EXECUTION_BLOCKER_REPAIR_PLAN",
            "P78 execution planning remains blocked, so P79 cannot advance beyond blocker repair planning.",
        )

    if source_status == "EXECUTION_PLAN_NOT_REQUIRED":
        if degraded_evidence_inputs:
            return (
                "AUTHORIZATION_NOT_REQUIRED",
                False,
                "P80_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
                "Authorization is not required because execution is not required, but degraded evidence still routes the lane to repair planning.",
            )
        if source_recommended_next_lane == "P79_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN":
            return (
                "AUTHORIZATION_NOT_REQUIRED",
                False,
                "P80_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
                "P78 reports execution not required and routes next to artifact regeneration dry-run planning.",
            )
        if source_recommended_next_lane == "P79_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE":
            return (
                "AUTHORIZATION_NOT_REQUIRED",
                False,
                "P80_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
                "P78 reports execution not required with no degraded evidence, so P79 routes to the non-execution spine implementation planning gate.",
            )
        return (
            "NOT_COMPUTABLE",
            False,
            "P78_EXECUTION_PLAN_REGENERATION",
            "P78 reports execution not required but its recommended next lane is inconsistent; regenerate P78 before P79 authorization gating.",
        )

    return (
        "NOT_COMPUTABLE",
        False,
        "P78_EXECUTION_PLAN_REGENERATION",
        "P78 execution plan status is missing or inconsistent; regenerate P78 before P79 authorization gating.",
    )


def build_temporal_continuity_upstream_input_regeneration_authorization_gate(
    *,
    repo_root: str | Path = ".",
    source_execution_plan_path: str = SOURCE_EXECUTION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_execution_plan_path
    source_observed = source_path.exists()

    source_payload = _load_json_dict(source_path)
    if source_payload is None:
        return _not_computable_packet(
            source_path=source_execution_plan_path,
            source_observed=source_observed,
        )

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_status = str(source_payload.get("execution_plan_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(
        source_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
    )
    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))
    execution_steps = [_normalized_step(step) for step in _as_dict_list(source_payload.get("execution_steps"))]
    command_allowlist = [
        _normalized_command(item)
        for item in _as_dict_list(source_payload.get("command_allowlist"))
    ]
    preflight_review_requirements = _as_dict_list(source_payload.get("preflight_checks"))

    allowlisted_command_keys = {
        (
            str(item["command"]),
            str(item["generator_script"]),
            str(item["expected_output_path"]),
        )
        for item in command_allowlist
        if bool(item["allowlisted_for_future_execution"])
    }

    eligible_execution_steps: list[dict[str, Any]] = []
    blocked_execution_steps: list[dict[str, Any]] = []
    for step in execution_steps:
        key = (
            str(step["proposed_command"]),
            str(step["generator_script"]),
            str(step["expected_output_path"]),
        )
        if key in allowlisted_command_keys:
            eligible_execution_steps.append(step)
        else:
            blocked_execution_steps.append(step)

    eligible_commands = [
        item for item in command_allowlist if bool(item["allowlisted_for_future_execution"])
    ]
    blocked_commands = [
        item for item in command_allowlist if not bool(item["allowlisted_for_future_execution"])
    ]

    eligible_execution_steps = _sort_steps(eligible_execution_steps)
    blocked_execution_steps = _sort_steps(blocked_execution_steps)
    eligible_commands = _sort_commands(eligible_commands)
    blocked_commands = _sort_commands(blocked_commands)
    preflight_review_requirements = sorted(
        preflight_review_requirements,
        key=lambda item: str(item.get("check_id", json.dumps(item, sort_keys=True))),
    )

    (
        authorization_gate_status,
        authorization_eligible,
        recommended_next_lane,
        recommended_next_lane_reason,
    ) = _build_status_and_recommendation(
        source_status=source_status,
        eligible_steps=eligible_execution_steps,
        execution_steps=execution_steps,
        eligible_commands=eligible_commands,
        degraded_evidence_inputs=degraded_evidence_inputs,
        source_recommended_next_lane=source_recommended_next_lane,
    )

    operator_review_requirements = (
        _operator_review_requirements(
            eligible_commands=eligible_commands,
            eligible_steps=eligible_execution_steps,
        )
        if authorization_gate_status == "AUTHORIZATION_ELIGIBLE"
        else []
    )
    post_authorization_requirements = (
        _post_authorization_requirements()
        if authorization_gate_status == "AUTHORIZATION_ELIGIBLE"
        else []
    )

    authorization_required_record = _authorization_required_record(
        required=authorization_gate_status == "AUTHORIZATION_ELIGIBLE"
    )

    strategy_summary = {
        "source_execution_steps_count": len(execution_steps),
        "eligible_execution_steps_count": len(eligible_execution_steps),
        "blocked_execution_steps_count": len(blocked_execution_steps),
        "eligible_commands_count": len(eligible_commands),
        "blocked_commands_count": len(blocked_commands),
        "operator_review_requirements_count": len(operator_review_requirements),
        "preflight_review_requirements_count": len(preflight_review_requirements),
        "post_authorization_requirements_count": len(post_authorization_requirements),
        "authorization_required": bool(authorization_required_record["required"]),
    }

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_gate_only": True,
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
        "authorization_authority": False,
        "spine_implementation_authority": False,
        "source_execution_plan_path": source_execution_plan_path,
        "source_execution_plan_observed": source_observed,
        "source_execution_plan_hash": source_hash,
        "source_execution_plan_status": source_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "authorization_gate_status": (
            authorization_gate_status
            if authorization_gate_status in _AUTHORIZATION_GATE_STATUSES
            else "NOT_COMPUTABLE"
        ),
        "authorization_eligible": authorization_eligible,
        "authorization_granted": False,
        "authorization_required_record": authorization_required_record,
        "eligible_execution_steps": eligible_execution_steps,
        "blocked_execution_steps": blocked_execution_steps,
        "eligible_commands": eligible_commands,
        "blocked_commands": blocked_commands,
        "operator_review_requirements": operator_review_requirements,
        "preflight_review_requirements": preflight_review_requirements,
        "post_authorization_requirements": post_authorization_requirements,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "authorization_strategy_summary": strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_upstream_input_regeneration_authorization_gate(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
