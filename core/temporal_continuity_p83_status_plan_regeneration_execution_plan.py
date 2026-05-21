from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP83StatusPlanRegenerationExecutionPlan.v1"
SOURCE_P87_REGENERATION_PLAN_PATH = (
    "out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json"
)
ALLOWED_FUTURE_RUNNER_COMMAND = (
    "python scripts/run_temporal_continuity_p79_authorization_gate_status_repair_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
)
EXPECTED_OUTPUT_ARTIFACT_TYPE = "TemporalContinuityP79AuthorizationGateStatusRepairPlan.v1"

_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_REGENERATION_EXECUTION_PLAN_READY",
    "P83_REGENERATION_EXECUTION_PLAN_BLOCKED",
    "P83_REGENERATION_EXECUTION_NOT_REQUIRED",
)

_BLOCKED_REASON_ORDER = (
    "P87_SOURCE_MISSING",
    "P87_SOURCE_UNREADABLE",
    "P87_SOURCE_MALFORMED_JSON",
    "P87_BLOCKED_OR_NOT_COMPUTABLE",
    "P83_REGENERATION_EXECUTION_NOT_REQUIRED",
    "P87_COMMAND_MISMATCH",
    "P87_EXPECTED_OUTPUT_PATH_MISMATCH",
    "P87_AUTHORITY_LOCK_VIOLATION",
    "P87_REGENERATION_ALLOWED_NOT_FALSE",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
    "AUTHORIZATION_REQUIRED_EXECUTION_DENIED_IN_P88",
)
_BLOCKED_REASON_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_BLOCKED_REASON_ORDER)
}

_PREFLIGHT_ORDER = (
    "preflight_001_source_p87_exists_readable",
    "preflight_002_source_p87_status_ready",
    "preflight_003_future_runner_command_exact_match",
    "preflight_004_expected_output_path_exact_match",
    "preflight_005_source_authority_fields_false",
    "preflight_006_p83_regeneration_execution_allowed_false",
)
_PREFLIGHT_ORDER_INDEX = {value: idx for idx, value in enumerate(_PREFLIGHT_ORDER)}

_POST_RUN_ORDER = (
    "postrun_001_p83_output_exists",
    "postrun_002_p83_output_readable",
    "postrun_003_p83_artifact_type_expected",
    "postrun_004_p83_status_not_not_computable",
    "postrun_005_p83_authority_flags_false",
    "postrun_006_p83_packet_hash_valid",
)
_POST_RUN_ORDER_INDEX = {value: idx for idx, value in enumerate(_POST_RUN_ORDER)}

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

_P87_AUTHORITY_FIELDS = (
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


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float, bool))]


def _ordered_unique(
    values: list[str], order_index: dict[str, int], *, fallback: int = 10_000
) -> list[str]:
    unique = list(dict.fromkeys(values))
    return sorted(unique, key=lambda value: order_index.get(value, fallback))


def _observe_source(*, root: Path, rel_path: str, status_field: str) -> dict[str, Any]:
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    status = "NOT_COMPUTABLE"
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
                status = str(parsed.get(status_field, "NOT_COMPUTABLE"))
            else:
                malformed_json = True

    return {
        "path": rel_path,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "status": status,
        "payload": payload,
    }


def _all_p87_authority_fields_false(payload: dict[str, Any]) -> bool:
    return all(payload.get(field) is False for field in _P87_AUTHORITY_FIELDS)


def _preflight_checks() -> list[dict[str, str]]:
    checks = [
        {
            "check_id": "preflight_001_source_p87_exists_readable",
            "check_type": "source_exists_readable",
            "path": SOURCE_P87_REGENERATION_PLAN_PATH,
            "required_status": "observed=true;readable=true",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P87_REGENERATION_PLAN_REGENERATION",
        },
        {
            "check_id": "preflight_002_source_p87_status_ready",
            "check_type": "status_exact_match",
            "path": SOURCE_P87_REGENERATION_PLAN_PATH,
            "required_status": "p83_regeneration_plan_status=P83_REGENERATION_PLAN_READY",
            "failure_action": "BLOCK_EXECUTION_PLAN_AND_ROUTE_TO_P87_REGENERATION_PLAN_REGENERATION",
        },
        {
            "check_id": "preflight_003_future_runner_command_exact_match",
            "check_type": "exact_command_match",
            "path": "future_runner_command",
            "required_status": ALLOWED_FUTURE_RUNNER_COMMAND,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P87_REGENERATION_PLAN_REGENERATION",
        },
        {
            "check_id": "preflight_004_expected_output_path_exact_match",
            "check_type": "exact_expected_output_path_match",
            "path": "expected_output_path",
            "required_status": EXPECTED_OUTPUT_PATH,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P87_REGENERATION_PLAN_REGENERATION",
        },
        {
            "check_id": "preflight_005_source_authority_fields_false",
            "check_type": "source_authority_lock_check",
            "path": SOURCE_P87_REGENERATION_PLAN_PATH,
            "required_status": "all_authority_fields=false",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_BLOCK_EXECUTION_WORK",
        },
        {
            "check_id": "preflight_006_p83_regeneration_execution_allowed_false",
            "check_type": "execution_allowed_lock_check",
            "path": "p83_regeneration_execution_allowed",
            "required_status": "false",
            "failure_action": "FAIL_CLOSED_BLOCK_EXECUTION_WORK",
        },
    ]
    return sorted(
        checks,
        key=lambda item: _PREFLIGHT_ORDER_INDEX.get(str(item["check_id"]), 10_000),
    )


def _post_run_validations() -> list[dict[str, str]]:
    validations = [
        {
            "validation_id": "postrun_001_p83_output_exists",
            "validation_type": "output_exists",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "observed=true",
            "failure_action": "FAIL_CLOSED_ROUTE_TO_REPAIR_OR_REGENERATION_PLANNING",
        },
        {
            "validation_id": "postrun_002_p83_output_readable",
            "validation_type": "output_readable_json",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "readable=true",
            "failure_action": "FAIL_CLOSED_ROUTE_TO_REPAIR_OR_REGENERATION_PLANNING",
        },
        {
            "validation_id": "postrun_003_p83_artifact_type_expected",
            "validation_type": "artifact_type_exact_match",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": EXPECTED_OUTPUT_ARTIFACT_TYPE,
            "failure_action": "FAIL_CLOSED_BLOCK_DOWNSTREAM_AUTHORIZATION_WORK",
        },
        {
            "validation_id": "postrun_004_p83_status_not_not_computable",
            "validation_type": "status_not_not_computable",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "p79_status_repair_plan_status!=NOT_COMPUTABLE",
            "failure_action": "ROUTE_TO_P87_REGENERATION_PLAN_REGENERATION",
        },
        {
            "validation_id": "postrun_005_p83_authority_flags_false",
            "validation_type": "authority_lock_check",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "all_authority_flags=false",
            "failure_action": "FAIL_CLOSED_BLOCK_DOWNSTREAM_AUTHORIZATION_WORK",
        },
        {
            "validation_id": "postrun_006_p83_packet_hash_valid",
            "validation_type": "packet_hash_format",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "packet_hash matches ^[a-f0-9]{64}$",
            "failure_action": "FAIL_CLOSED_ROUTE_TO_REGENERATION_PLANNING",
        },
    ]
    return sorted(
        validations,
        key=lambda item: _POST_RUN_ORDER_INDEX.get(str(item["validation_id"]), 10_000),
    )


def _classify(p87: dict[str, Any]) -> dict[str, Any]:
    p87_status = str(p87["status"])
    payload = p87.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}
    source_command = str(payload_dict.get("future_runner_command", "NOT_COMPUTABLE"))
    source_expected_output_path = str(
        payload_dict.get("expected_output_path", "NOT_COMPUTABLE")
    )

    if not p87["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": "P87_REGENERATION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P87 regeneration plan source is missing; regenerate P87 before deriving "
                "the P88 execution plan."
            ),
            "blocked_reasons": ["P87_SOURCE_MISSING"],
            "future_runner_command": "NOT_COMPUTABLE",
            "expected_output_path": "NOT_COMPUTABLE",
        }

    if not p87["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": "P87_REGENERATION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P87 regeneration plan source is unreadable; regenerate P87 before deriving "
                "the P88 execution plan."
            ),
            "blocked_reasons": ["P87_SOURCE_UNREADABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "expected_output_path": "NOT_COMPUTABLE",
        }

    if p87["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": "P87_REGENERATION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P87 regeneration plan source is malformed JSON; regenerate P87 before "
                "deriving the P88 execution plan."
            ),
            "blocked_reasons": ["P87_SOURCE_MALFORMED_JSON"],
            "future_runner_command": "NOT_COMPUTABLE",
            "expected_output_path": "NOT_COMPUTABLE",
        }

    if p87_status in {"NOT_COMPUTABLE", "P83_REGENERATION_PLAN_BLOCKED"}:
        return {
            "status": "P83_REGENERATION_EXECUTION_PLAN_BLOCKED",
            "required": False,
            "recommended_next_lane": "P87_REGENERATION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P87 reports NOT_COMPUTABLE or blocked; regenerate P87 before execution "
                "planning can proceed."
            ),
            "blocked_reasons": ["P87_BLOCKED_OR_NOT_COMPUTABLE"],
            "future_runner_command": source_command,
            "expected_output_path": source_expected_output_path,
        }

    if p87_status == "P83_REGENERATION_NOT_REQUIRED":
        return {
            "status": "P83_REGENERATION_EXECUTION_NOT_REQUIRED",
            "required": False,
            "recommended_next_lane": (
                "P89_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P87 reports P83 regeneration not required; execution planning is not "
                "required and planning continues at P89."
            ),
            "blocked_reasons": ["P83_REGENERATION_EXECUTION_NOT_REQUIRED"],
            "future_runner_command": source_command,
            "expected_output_path": source_expected_output_path,
        }

    if p87_status == "P83_REGENERATION_PLAN_READY":
        authority_locks_ok = _all_p87_authority_fields_false(payload_dict)
        regeneration_allowed_lock_ok = payload_dict.get("p83_regeneration_allowed") is False
        command_match = source_command == ALLOWED_FUTURE_RUNNER_COMMAND
        output_match = source_expected_output_path == EXPECTED_OUTPUT_PATH

        if command_match and output_match and authority_locks_ok and regeneration_allowed_lock_ok:
            return {
                "status": "P83_REGENERATION_EXECUTION_PLAN_READY",
                "required": True,
                "recommended_next_lane": (
                    "P89_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_GATE"
                ),
                "recommended_next_lane_reason": (
                    "P87 is ready and command/output match exactly; emit governed execution "
                    "planning that still denies execution authority."
                ),
                "blocked_reasons": ["AUTHORIZATION_REQUIRED_EXECUTION_DENIED_IN_P88"],
                "future_runner_command": source_command,
                "expected_output_path": source_expected_output_path,
            }

        blocked_reasons: list[str] = []
        if not command_match:
            blocked_reasons.append("P87_COMMAND_MISMATCH")
        if not output_match:
            blocked_reasons.append("P87_EXPECTED_OUTPUT_PATH_MISMATCH")
        if not authority_locks_ok:
            blocked_reasons.append("P87_AUTHORITY_LOCK_VIOLATION")
        if not regeneration_allowed_lock_ok:
            blocked_reasons.append("P87_REGENERATION_ALLOWED_NOT_FALSE")
        if not blocked_reasons:
            blocked_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": "P87_REGENERATION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P87 ready signal is inconsistent with command/path/authority invariants; "
                "regenerate P87 before deriving execution planning."
            ),
            "blocked_reasons": blocked_reasons,
            "future_runner_command": source_command,
            "expected_output_path": source_expected_output_path,
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "recommended_next_lane": "P87_REGENERATION_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P87 regeneration status is missing or unsupported; regenerate P87 before "
            "deriving execution planning."
        ),
        "blocked_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
        "future_runner_command": source_command,
        "expected_output_path": source_expected_output_path,
    }


def build_temporal_continuity_p83_status_plan_regeneration_execution_plan(
    *,
    repo_root: str | Path = ".",
    source_p87_regeneration_plan_path: str = SOURCE_P87_REGENERATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)

    p87 = _observe_source(
        root=root,
        rel_path=source_p87_regeneration_plan_path,
        status_field="p83_regeneration_plan_status",
    )
    p87_payload = p87.get("payload")
    inherited_payload: dict[str, Any] = p87_payload if isinstance(p87_payload, dict) else {}

    classification = _classify(p87)
    status = str(classification["status"])
    required = bool(classification["required"])

    future_runner_command = str(classification["future_runner_command"])
    expected_output_path = str(classification["expected_output_path"])

    degraded_evidence_inputs = _as_str_list(
        inherited_payload.get("degraded_evidence_inputs")
    )
    inherited_blockers = _as_str_list(inherited_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(inherited_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(inherited_payload.get("semantic_overlap_flags"))

    execution_steps: list[dict[str, Any]] = []
    command_allowlist: list[dict[str, Any]] = []
    expected_outputs: list[dict[str, Any]] = []

    if status == "P83_REGENERATION_EXECUTION_PLAN_READY":
        execution_steps.append(
            {
                "step_id": "step_001",
                "lane": "P83",
                "command": ALLOWED_FUTURE_RUNNER_COMMAND,
                "expected_output_path": EXPECTED_OUTPUT_PATH,
                "source_plan_path": source_p87_regeneration_plan_path,
                "preflight_required": True,
                "post_run_validation_required": True,
                "execution_authorized": False,
                "execution_allowed": False,
                "blocking_reason": "AUTHORIZATION_REQUIRED_EXECUTION_DENIED_IN_P88",
            }
        )
        command_allowlist.append(
            {
                "command": ALLOWED_FUTURE_RUNNER_COMMAND,
                "allowlisted_for_future_execution": True,
                "execution_authorized": False,
                "execution_allowed": False,
                "blocking_reason": "AUTHORIZATION_REQUIRED_EXECUTION_DENIED_IN_P88",
            }
        )
        expected_outputs.append(
            {
                "path": EXPECTED_OUTPUT_PATH,
                "expected_artifact_type": EXPECTED_OUTPUT_ARTIFACT_TYPE,
                "currently_observed": (root / EXPECTED_OUTPUT_PATH).exists(),
                "overwrite_policy": "ALLOW_OVERWRITE_ONLY_IN_FUTURE_AUTHORIZED_LANE",
                "validation_required": True,
            }
        )

    execution_steps = sorted(
        execution_steps,
        key=lambda item: (
            str(item["step_id"]),
            str(item["lane"]),
            str(item["expected_output_path"]),
        ),
    )
    command_allowlist = sorted(command_allowlist, key=lambda item: str(item["command"]))
    expected_outputs = sorted(expected_outputs, key=lambda item: str(item["path"]))

    blocked_execution_reasons = _ordered_unique(
        [str(reason) for reason in classification["blocked_reasons"]],
        _BLOCKED_REASON_ORDER_INDEX,
    )

    preflight_checks = _preflight_checks()
    post_run_validations = _post_run_validations()

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "execution_plan_only": True,
        "regeneration_execution_plan_only": True,
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
        "authorization_record_creation_authority": False,
        "spine_implementation_authority": False,
        "source_p87_regeneration_plan_path": source_p87_regeneration_plan_path,
        "source_p87_regeneration_plan_observed": bool(p87["observed"]),
        "source_p87_regeneration_plan_readable": bool(p87["readable"]),
        "source_p87_regeneration_plan_hash": str(p87["file_hash"]),
        "source_p87_regeneration_plan_status": str(p87["status"]),
        "source_p87_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p83_regeneration_execution_plan_status": (
            status if status in _PLAN_STATUSES else "NOT_COMPUTABLE"
        ),
        "p83_regeneration_execution_required": required,
        "p83_regeneration_execution_allowed": False,
        "execution_steps": execution_steps,
        "command_allowlist": command_allowlist,
        "expected_outputs": expected_outputs,
        "preflight_checks": preflight_checks,
        "post_run_validations": post_run_validations,
        "blocked_execution_reasons": blocked_execution_reasons,
        "future_runner_command": future_runner_command,
        "expected_output_path": expected_output_path,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "execution_strategy_summary": {
            "execution_steps_count": len(execution_steps),
            "allowlisted_commands_count": len(command_allowlist),
            "expected_outputs_count": len(expected_outputs),
            "preflight_checks_count": len(preflight_checks),
            "post_run_validations_count": len(post_run_validations),
            "blocked_execution_reasons_count": len(blocked_execution_reasons),
            "p83_regeneration_execution_required": required,
            "p83_regeneration_execution_allowed": False,
            "p83_regeneration_execution_plan_status": (
                status if status in _PLAN_STATUSES else "NOT_COMPUTABLE"
            ),
        },
        "recommended_next_lane": str(classification["recommended_next_lane"]),
        "recommended_next_lane_reason": str(classification["recommended_next_lane_reason"]),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    packet_no_hash = {k: v for k, v in packet_base.items() if k != "packet_hash"}
    packet = {**packet_no_hash, "packet_hash": canonical_hash(packet_no_hash)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_p83_status_plan_regeneration_execution_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
