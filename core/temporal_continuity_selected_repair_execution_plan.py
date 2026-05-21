from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuitySelectedRepairExecutionPlan.v1"
SOURCE_P102B_ROUTER_PATH = "out/temporal_continuity_repair_execution_plan_router/latest.json"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_P102B_READY = "REPAIR_EXECUTION_PLAN_ROUTER_READY"
_P102B_BLOCKED = "REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED"
_P102B_NOT_REQUIRED = "REPAIR_EXECUTION_PLAN_NOT_REQUIRED"

_P102C_READY = "SELECTED_REPAIR_EXECUTION_PLAN_READY"
_P102C_BLOCKED = "SELECTED_REPAIR_EXECUTION_PLAN_BLOCKED"
_P102C_NOT_REQUIRED = "SELECTED_REPAIR_EXECUTION_NOT_REQUIRED"

_BRANCH_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_BRANCH_P101_ONLY = "P101_GATE_ONLY"
_BRANCH_FULL_CHAIN = "P99_P100_P101_CHAIN"
_BRANCH_P102_RERUN_ONLY = "P102_RERUN_ONLY"
_BRANCH_NONE = "NO_REPAIR_REQUIRED"

_LANE_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_LANE_P101_ONLY = "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN"
_LANE_FULL_CHAIN = "P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN"
_LANE_RERUN_ONLY = "P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN"
_LANE_NONE = "NO_REPAIR_REQUIRED"

_COMMAND_P99 = (
    "python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan.py"
)
_COMMAND_P100 = (
    "python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan.py"
)
_COMMAND_P101 = (
    "python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate.py"
)
_COMMAND_P102 = "python scripts/run_temporal_continuity_recursive_authorization_chain_compression_audit.py"

_COMMAND_SPECS: tuple[dict[str, str], ...] = (
    {
        "command": _COMMAND_P99,
        "target_artifact_path": (
            "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json"
        ),
        "purpose": "Regenerate the P99 sequence record creation record plan in advisory-only selected execution planning.",
        "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
    },
    {
        "command": _COMMAND_P100,
        "target_artifact_path": (
            "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json"
        ),
        "purpose": "Regenerate the P100 sequence record creation record creation plan in advisory-only selected execution planning.",
        "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
    },
    {
        "command": _COMMAND_P101,
        "target_artifact_path": (
            "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json"
        ),
        "purpose": "Regenerate the P101 authorization gate surface in advisory-only selected execution planning.",
        "expected_status_after_run": (
            "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
        ),
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
    },
    {
        "command": _COMMAND_P102,
        "target_artifact_path": (
            "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json"
        ),
        "purpose": "Rerun the P102 compression audit only after upstream selected plan steps are externally authorized and completed.",
        "expected_status_after_run": "COMPRESSION_AUDIT_READY",
        "failure_action": "FAIL_CLOSED_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
    },
)
_COMMAND_INDEX: dict[str, dict[str, str]] = {
    spec["command"]: spec for spec in _COMMAND_SPECS
}
_COMMAND_ALLOWLIST: tuple[str, ...] = tuple(spec["command"] for spec in _COMMAND_SPECS)

_EXECUTION_BLOCKER_ORDER: tuple[str, ...] = (
    "P102B_SOURCE_MISSING",
    "P102B_SOURCE_UNREADABLE",
    "P102B_SOURCE_MALFORMED",
    "P102B_ROUTER_BLOCKED",
    "P102B_NOT_COMPUTABLE",
    "P102B_NO_REPAIR_REQUIRED",
    "SELECTED_COMMAND_SEQUENCE_EMPTY",
    "UNSUPPORTED_COMMAND",
    "DYNAMIC_COMMAND_SYNTAX",
    "COMMAND_EXECUTION_ALLOWED_TRUE",
    "COMMAND_EXECUTION_AUTHORITY_TRUE",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_EXECUTION_BLOCKER_INDEX: dict[str, int] = {
    blocker: index for index, blocker in enumerate(_EXECUTION_BLOCKER_ORDER)
}

_DENIED_AUTHORITY: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "repair_execution_authority",
    "regeneration_authority",
    "regeneration_execution_authority",
    "evidence_generation_authority",
    "restoration_execution_authority",
    "generator_execution_authority",
    "upstream_input_generation_authority",
    "artifact_regeneration_authority",
    "execution_authority",
    "authorization_authority",
    "authorization_record_creation_authority",
    "spine_implementation_authority",
)

_DYNAMIC_COMMAND_PATTERN = re.compile(
    r"(^[A-Za-z_][A-Za-z0-9_]*=)|(^export\b)|(&&)|(\|\|)|(\|)|(>)|(<)|(;)|(`)|(\$\()|(\$\{)|[\r\n]"
)


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


def _normalize_blockers(values: list[str]) -> list[str]:
    unique = list(dict.fromkeys(values))
    return sorted(
        unique,
        key=lambda value: (_EXECUTION_BLOCKER_INDEX.get(value, 10_000), value),
    )


def _observe_source(*, root: Path) -> dict[str, Any]:
    source_path = root / SOURCE_P102B_ROUTER_PATH
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    payload: dict[str, Any] | None = None

    if observed:
        try:
            source_bytes = source_path.read_bytes()
            readable = True
            file_hash = hashlib.sha256(source_bytes).hexdigest()
        except OSError:
            readable = False
            source_bytes = b""

        if readable:
            try:
                parsed = json.loads(source_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                malformed_json = True
                parsed = None

            if isinstance(parsed, dict):
                payload = parsed
            else:
                malformed_json = True

    return {
        "path": SOURCE_P102B_ROUTER_PATH,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "payload": payload,
    }


def _allowlist_from_source(payload: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for item in _as_list(payload.get("command_allowlist")):
        if isinstance(item, dict):
            commands.append(str(item.get("command", "NOT_COMPUTABLE")))
        else:
            commands.append(str(item))
    return commands


def _selected_commands_for_lane(lane: str) -> list[str]:
    if lane == _LANE_P101_ONLY:
        return [_COMMAND_P101, _COMMAND_P102]
    if lane == _LANE_FULL_CHAIN:
        return [_COMMAND_P99, _COMMAND_P100, _COMMAND_P101, _COMMAND_P102]
    if lane == _LANE_RERUN_ONLY:
        return [_COMMAND_P102]
    return []


def _selected_branch_for_lane(lane: str) -> str:
    if lane == _LANE_P101_ONLY:
        return _BRANCH_P101_ONLY
    if lane == _LANE_FULL_CHAIN:
        return _BRANCH_FULL_CHAIN
    if lane == _LANE_RERUN_ONLY:
        return _BRANCH_P102_RERUN_ONLY
    if lane == _LANE_NONE:
        return _BRANCH_NONE
    return _BRANCH_NOT_COMPUTABLE


def _selected_branch_reason(lane: str) -> str:
    if lane == _LANE_P101_ONLY:
        return "P102B selected the P101-only repair route, so P102C emits a P101 gate regeneration execution plan only."
    if lane == _LANE_FULL_CHAIN:
        return "P102B selected the full P99→P102 repair route, so P102C emits the full regeneration chain execution plan only."
    if lane == _LANE_RERUN_ONLY:
        return "P102B selected the rerun-only repair route, so P102C emits the compression-audit rerun execution plan only."
    if lane == _LANE_NONE:
        return "P102B reported that no repair execution plan is required, so P102C preserves the no-repair-required branch."
    return "P102C could not safely classify the selected repair execution branch from P102B."


def _sequence_has_dynamic_syntax(command: str) -> bool:
    return bool(_DYNAMIC_COMMAND_PATTERN.search(command))


def _planned_execution_steps(sequence: list[Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for index, item in enumerate(sequence, start=1):
        if not isinstance(item, dict):
            continue
        command = str(item.get("command", "NOT_COMPUTABLE"))
        spec = _COMMAND_INDEX.get(command)
        target_artifact_path = (
            spec["target_artifact_path"]
            if spec is not None
            else str(item.get("target_artifact_path", "NOT_COMPUTABLE"))
        )
        purpose = (
            spec["purpose"]
            if spec is not None
            else str(item.get("purpose", "NOT_COMPUTABLE"))
        )
        expected_status_after_run = (
            spec["expected_status_after_run"]
            if spec is not None
            else str(item.get("expected_status_after_run", "NOT_COMPUTABLE"))
        )
        steps.append(
            {
                "step_id": f"planned_step_{index:03d}",
                "source_sequence_id": str(
                    item.get(
                        "sequence_id",
                        item.get("source_sequence_id", "NOT_COMPUTABLE"),
                    )
                ),
                "command": command,
                "target_artifact_path": target_artifact_path,
                "purpose": purpose,
                "preconditions": [
                    "P102D authorization gate approval remains required before any external execution.",
                    "Each planned step remains advisory-only and execution-locked in P102C.",
                ],
                "expected_status_after_run": expected_status_after_run,
                "execution_allowed": False,
                "execution_authority": False,
                "rollback_on_failure": False,
                "failure_action": (
                    spec["failure_action"]
                    if spec is not None
                    else "FAIL_CLOSED_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION"
                ),
            }
        )
    return steps


def _preflight_checks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = [
        {
            "check_id": "preflight_001_source_p102b_readable",
            "check_type": "source_artifact_readable",
            "artifact_path": SOURCE_P102B_ROUTER_PATH,
            "required_status": "observed=true;readable=true",
            "required_readable": True,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
        },
        {
            "check_id": "preflight_002_source_p102b_status_locked",
            "check_type": "source_router_status_lock",
            "artifact_path": SOURCE_P102B_ROUTER_PATH,
            "required_status": str(payload.get("p102b_router_status", "NOT_COMPUTABLE")),
            "required_readable": True,
            "failure_action": "BLOCK_SELECTED_REPAIR_EXECUTION_PLAN_AND_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
        },
        {
            "check_id": "preflight_003_source_selected_lane_locked",
            "check_type": "selected_lane_lock",
            "artifact_path": SOURCE_P102B_ROUTER_PATH,
            "required_status": str(
                payload.get("selected_execution_plan_lane", "NOT_COMPUTABLE")
            ),
            "required_readable": True,
            "failure_action": "BLOCK_SELECTED_REPAIR_EXECUTION_PLAN_AND_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
        },
    ]
    for index, item in enumerate(_as_list(payload.get("validation_requirements")), start=1):
        if not isinstance(item, dict):
            continue
        checks.append(
            {
                "check_id": f"preflight_{index + 3:03d}_{str(item.get('requirement_id', f'validation_{index:03d}'))}",
                "check_type": "router_validation_requirement",
                "artifact_path": str(item.get("artifact_path", "NOT_COMPUTABLE")),
                "required_status": str(item.get("required_status", "NOT_COMPUTABLE")),
                "required_readable": bool(item.get("required_readable", False)),
                "failure_action": str(
                    item.get(
                        "failure_action",
                        "BLOCK_SELECTED_REPAIR_EXECUTION_PLAN_AND_ROUTE_TO_P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
                    )
                ),
            }
        )
    return checks


def _postrun_validation_requirements(
    planned_execution_steps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for index, step in enumerate(planned_execution_steps, start=1):
        requirements.append(
            {
                "requirement_id": f"postrun_{index:03d}_{step['source_sequence_id']}",
                "artifact_path": str(step["target_artifact_path"]),
                "required_status": str(step["expected_status_after_run"]),
                "required_readable": True,
                "failure_action": str(step["failure_action"]),
            }
        )
    return requirements


def _rerun_p102_requirements(
    planned_execution_steps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for index, step in enumerate(planned_execution_steps, start=1):
        if str(step["command"]) == _COMMAND_P102:
            break
        requirements.append(
            {
                "requirement_id": f"rerun_p102_{index:03d}_{step['source_sequence_id']}",
                "artifact_path": str(step["target_artifact_path"]),
                "required_status": str(step["expected_status_after_run"]),
                "required_readable": True,
                "failure_action": "REGENERATE_REQUIRED_SELECTED_STEP_BEFORE_P102_RERUN",
            }
        )
    return requirements


def _classify(source: dict[str, Any]) -> dict[str, Any]:
    if not bool(source["observed"]):
        return {
            "p102c_execution_plan_status": _NOT_COMPUTABLE,
            "selected_execution_plan_lane": _LANE_NOT_COMPUTABLE,
            "selected_branch_type": _BRANCH_NOT_COMPUTABLE,
            "selected_branch_reason": "P102B source is missing, so P102C cannot derive a deterministic selected repair execution plan.",
            "recommended_next_lane": "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
            "recommended_next_lane_reason": "P102B must be regenerated before P102C can classify a selected repair execution plan.",
            "execution_blockers": ["P102B_SOURCE_MISSING"],
            "planned_execution_steps": [],
        }
    if not bool(source["readable"]):
        return {
            "p102c_execution_plan_status": _NOT_COMPUTABLE,
            "selected_execution_plan_lane": _LANE_NOT_COMPUTABLE,
            "selected_branch_type": _BRANCH_NOT_COMPUTABLE,
            "selected_branch_reason": "P102B source is unreadable, so P102C cannot derive a deterministic selected repair execution plan.",
            "recommended_next_lane": "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
            "recommended_next_lane_reason": "P102B must be readable before P102C can classify a selected repair execution plan.",
            "execution_blockers": ["P102B_SOURCE_UNREADABLE"],
            "planned_execution_steps": [],
        }
    if bool(source["malformed_json"]):
        return {
            "p102c_execution_plan_status": _NOT_COMPUTABLE,
            "selected_execution_plan_lane": _LANE_NOT_COMPUTABLE,
            "selected_branch_type": _BRANCH_NOT_COMPUTABLE,
            "selected_branch_reason": "P102B source is malformed, so P102C cannot derive a deterministic selected repair execution plan.",
            "recommended_next_lane": "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
            "recommended_next_lane_reason": "P102B must be valid canonical JSON before P102C can classify a selected repair execution plan.",
            "execution_blockers": ["P102B_SOURCE_MALFORMED"],
            "planned_execution_steps": [],
        }

    payload = source["payload"] if isinstance(source["payload"], dict) else {}
    source_status = str(payload.get("p102b_router_status", _NOT_COMPUTABLE))
    source_lane = str(payload.get("selected_execution_plan_lane", _LANE_NOT_COMPUTABLE))
    source_sequence = _as_list(payload.get("selected_command_sequence"))
    source_sequence_commands = [
        str(item.get("command", "NOT_COMPUTABLE"))
        for item in source_sequence
        if isinstance(item, dict)
    ]
    source_allowlist = _allowlist_from_source(payload)

    if source_status == _NOT_COMPUTABLE:
        return {
            "p102c_execution_plan_status": _P102C_BLOCKED,
            "selected_execution_plan_lane": _LANE_NOT_COMPUTABLE,
            "selected_branch_type": _BRANCH_NOT_COMPUTABLE,
            "selected_branch_reason": "P102B reported NOT_COMPUTABLE, so P102C remains fail-closed and blocked.",
            "recommended_next_lane": "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
            "recommended_next_lane_reason": "P102B must become computable before a selected repair execution plan can be trusted.",
            "execution_blockers": ["P102B_NOT_COMPUTABLE"],
            "planned_execution_steps": [],
        }

    if source_status == _P102B_BLOCKED:
        return {
            "p102c_execution_plan_status": _P102C_BLOCKED,
            "selected_execution_plan_lane": _LANE_NOT_COMPUTABLE,
            "selected_branch_type": _BRANCH_NOT_COMPUTABLE,
            "selected_branch_reason": "P102B is blocked, so P102C preserves the fail-closed advisory-only blocked state.",
            "recommended_next_lane": "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
            "recommended_next_lane_reason": "P102B blockers must clear before a selected repair execution plan can be trusted.",
            "execution_blockers": ["P102B_ROUTER_BLOCKED"],
            "planned_execution_steps": [],
        }

    if source_status == _P102B_NOT_REQUIRED:
        return {
            "p102c_execution_plan_status": _P102C_NOT_REQUIRED,
            "selected_execution_plan_lane": _LANE_NONE,
            "selected_branch_type": _BRANCH_NONE,
            "selected_branch_reason": _selected_branch_reason(_LANE_NONE),
            "recommended_next_lane": "P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
            "recommended_next_lane_reason": "P102B already reported that no repair execution plan is required.",
            "execution_blockers": ["P102B_NO_REPAIR_REQUIRED"],
            "planned_execution_steps": [],
        }

    blocked_reasons: list[str] = []
    expected_commands = _selected_commands_for_lane(source_lane)
    if not expected_commands:
        blocked_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")
    if not source_sequence:
        blocked_reasons.append("SELECTED_COMMAND_SEQUENCE_EMPTY")
    if source_allowlist != list(_COMMAND_ALLOWLIST):
        blocked_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")

    for item in source_sequence:
        if not isinstance(item, dict):
            blocked_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")
            continue
        command = str(item.get("command", "NOT_COMPUTABLE"))
        if command not in _COMMAND_INDEX:
            blocked_reasons.append("UNSUPPORTED_COMMAND")
        if _sequence_has_dynamic_syntax(command):
            blocked_reasons.append("DYNAMIC_COMMAND_SYNTAX")
        if item.get("execution_allowed") is True:
            blocked_reasons.append("COMMAND_EXECUTION_ALLOWED_TRUE")
        if item.get("execution_authority") is True:
            blocked_reasons.append("COMMAND_EXECUTION_AUTHORITY_TRUE")

    if expected_commands and source_sequence_commands != expected_commands:
        blocked_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")

    normalized_blockers = _normalize_blockers(blocked_reasons)
    if normalized_blockers:
        return {
            "p102c_execution_plan_status": _P102C_BLOCKED,
            "selected_execution_plan_lane": _LANE_NOT_COMPUTABLE,
            "selected_branch_type": _BRANCH_NOT_COMPUTABLE,
            "selected_branch_reason": "P102B selected command sequence failed deterministic safety checks, so P102C remains advisory-only and blocked.",
            "recommended_next_lane": "P102B_REPAIR_EXECUTION_PLAN_ROUTER_REGENERATION",
            "recommended_next_lane_reason": "P102B selected command sequence must be regenerated into a safe deterministic route before P102C can proceed.",
            "execution_blockers": normalized_blockers,
            "planned_execution_steps": [],
        }

    return {
        "p102c_execution_plan_status": _P102C_READY,
        "selected_execution_plan_lane": source_lane,
        "selected_branch_type": _selected_branch_for_lane(source_lane),
        "selected_branch_reason": _selected_branch_reason(source_lane),
        "recommended_next_lane": "P102D_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_GATE",
        "recommended_next_lane_reason": "P102C prepared a safe advisory-only selected repair execution plan; any real execution still requires a downstream authorization gate.",
        "execution_blockers": [],
        "planned_execution_steps": _planned_execution_steps(source_sequence),
    }


def build_temporal_continuity_selected_repair_execution_plan(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _observe_source(root=root)
    payload = source["payload"] if isinstance(source["payload"], dict) else {}
    source_status = str(payload.get("p102b_router_status", _NOT_COMPUTABLE))
    source_lane = str(payload.get("selected_execution_plan_lane", _LANE_NOT_COMPUTABLE))
    source_recommended_next_lane = str(
        payload.get("recommended_next_lane", _NOT_COMPUTABLE)
    )
    source_sequence = _as_list(payload.get("selected_command_sequence"))
    degraded_evidence_inputs = _as_list(payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_list(payload.get("inherited_blockers"))
    inherited_drift_flags = _as_list(payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_list(payload.get("semantic_overlap_flags"))

    classification = _classify(source)
    planned_execution_steps = list(classification["planned_execution_steps"])

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "selected_execution_plan_only": True,
        "repair_execution_plan_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "repair_execution_authority": False,
        "regeneration_authority": False,
        "regeneration_execution_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_token_created": False,
        "authorization_record_creation_authority": False,
        "authorization_record_created": False,
        "spine_implementation_authority": False,
        "source_p102b_router_path": SOURCE_P102B_ROUTER_PATH,
        "source_p102b_router_observed": bool(source["observed"]),
        "source_p102b_router_readable": bool(source["readable"]),
        "source_p102b_router_hash": str(source["file_hash"]),
        "source_p102b_router_status": source_status,
        "source_selected_execution_plan_lane": source_lane,
        "source_recommended_next_lane": source_recommended_next_lane,
        "source_selected_command_sequence_count": len(source_sequence),
        "p102c_execution_plan_status": str(
            classification["p102c_execution_plan_status"]
        ),
        "selected_execution_plan_lane": str(
            classification["selected_execution_plan_lane"]
        ),
        "selected_branch_type": str(classification["selected_branch_type"]),
        "selected_branch_reason": str(classification["selected_branch_reason"]),
        "planned_execution_steps": planned_execution_steps,
        "command_allowlist": list(_COMMAND_ALLOWLIST),
        "preflight_checks": _preflight_checks(payload),
        "postrun_validation_requirements": _postrun_validation_requirements(
            planned_execution_steps
        ),
        "rerun_p102_requirements": _rerun_p102_requirements(planned_execution_steps),
        "execution_blockers": list(classification["execution_blockers"]),
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "execution_plan_strategy_summary": {
            "source_p102b_router_status": source_status,
            "source_selected_execution_plan_lane": source_lane,
            "source_selected_command_sequence_count": len(source_sequence),
            "selected_branch_type": str(classification["selected_branch_type"]),
            "planned_execution_steps_count": len(planned_execution_steps),
            "execution_blocker_count": len(classification["execution_blockers"]),
            "p102c_execution_plan_status": str(
                classification["p102c_execution_plan_status"]
            ),
        },
        "recommended_next_lane": str(classification["recommended_next_lane"]),
        "recommended_next_lane_reason": str(
            classification["recommended_next_lane_reason"]
        ),
        "denied_authority": list(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_selected_repair_execution_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
