from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityRepairExecutionPlanRouter.v1"
SOURCE_P102A_REPAIR_PLAN_PATH = "out/temporal_continuity_p101_readiness_repair_plan/latest.json"

_P99_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json"
)
_P100_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json"
)
_P101_GATE_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json"
)
_P102_AUDIT_PATH = "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json"

_P101_REPAIR_PLAN_READY = "P101_READINESS_REPAIR_PLAN_READY"
_P101_REPAIR_NOT_REQUIRED = "P101_READINESS_REPAIR_NOT_REQUIRED"
_P101_REPAIR_BLOCKED = "P101_READINESS_REPAIR_BLOCKED"
_NOT_COMPUTABLE = "NOT_COMPUTABLE"

_ROUTER_READY = "REPAIR_EXECUTION_PLAN_ROUTER_READY"
_ROUTER_BLOCKED = "REPAIR_EXECUTION_PLAN_ROUTER_BLOCKED"
_ROUTER_NOT_REQUIRED = "REPAIR_EXECUTION_PLAN_NOT_REQUIRED"

_LANE_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_LANE_P101_ONLY = "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN"
_LANE_FULL_CHAIN = "P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN"
_LANE_RERUN_ONLY = "P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN"
_LANE_NO_REPAIR_REQUIRED = "NO_REPAIR_REQUIRED"

_P102C_LANE_P101_ONLY = "P102C_P101_GATE_REGENERATION_EXECUTION_PLAN"
_P102C_LANE_FULL_CHAIN = "P102C_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN"
_P102C_LANE_RERUN_ONLY = "P102C_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN"

_COMMAND_P99 = (
    "python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan.py"
)
_COMMAND_P100 = (
    "python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan.py"
)
_COMMAND_P101 = (
    "python scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate.py"
)
_COMMAND_P102 = "python scripts/temporal/run_temporal_continuity_recursive_authorization_chain_compression_audit.py"

_COMMAND_SPECS: tuple[dict[str, str], ...] = (
    {
        "command": _COMMAND_P99,
        "target_artifact_path": _P99_PLAN_PATH,
        "purpose": "Planned P99 sequence record creation record plan regeneration in execution-plan lane only.",
        "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
        "rationale": "Required planning surface for full P99→P102 repair chain routing.",
    },
    {
        "command": _COMMAND_P100,
        "target_artifact_path": _P100_PLAN_PATH,
        "purpose": "Planned P100 sequence record creation record creation plan regeneration in execution-plan lane only.",
        "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
        "rationale": "Required planning surface for full P99→P102 repair chain routing.",
    },
    {
        "command": _COMMAND_P101,
        "target_artifact_path": _P101_GATE_PATH,
        "purpose": "Planned P101 authorization gate regeneration in execution-plan lane only.",
        "expected_status_after_run": (
            "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
        ),
        "rationale": "Required planning surface for P101 gate restoration before P102 rerun.",
    },
    {
        "command": _COMMAND_P102,
        "target_artifact_path": _P102_AUDIT_PATH,
        "purpose": "Planned P102 compression audit rerun in execution-plan lane only.",
        "expected_status_after_run": "COMPRESSION_AUDIT_READY",
        "rationale": "Required planning surface to re-evaluate recursive chain compression state.",
    },
)

_COMMAND_INDEX: dict[str, dict[str, str]] = {spec["command"]: spec for spec in _COMMAND_SPECS}
_ALLOWED_COMMANDS: frozenset[str] = frozenset(_COMMAND_INDEX)

_SUPPORTED_P102A_NEXT_LANES: frozenset[str] = frozenset(
    {_LANE_P101_ONLY, _LANE_FULL_CHAIN, _LANE_RERUN_ONLY}
)

_DENIED_AUTHORITY: tuple[str, ...] = (
    "artifact_regeneration_authority",
    "authorization_authority",
    "authorization_record_creation_authority",
    "canon_promotion",
    "evidence_generation_authority",
    "execution_authority",
    "forecast_influence",
    "generator_execution_authority",
    "production_activation",
    "regeneration_authority",
    "regeneration_execution_authority",
    "repair_authority",
    "repair_execution_authority",
    "restoration_execution_authority",
    "runtime_authority",
    "scheduler_mutation",
    "spine_implementation_authority",
    "upstream_input_generation_authority",
)

_BLOCKED_REASON_ORDER: tuple[str, ...] = (
    "P102A_SOURCE_MISSING",
    "P102A_SOURCE_UNREADABLE",
    "P102A_SOURCE_MALFORMED",
    "P102A_NOT_COMPUTABLE",
    "P102A_REPAIR_BLOCKED",
    "P102A_RECOMMENDED_LANE_UNSUPPORTED",
    "FUTURE_COMMAND_SEQUENCE_EMPTY",
    "FUTURE_COMMAND_SEQUENCE_CONTAINS_UNSUPPORTED_COMMAND",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_BLOCKED_REASON_PRIORITY: dict[str, int] = {
    reason: index for index, reason in enumerate(_BLOCKED_REASON_ORDER)
}


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


def _observe_source(*, root: Path) -> dict[str, Any]:
    source_path = root / SOURCE_P102A_REPAIR_PLAN_PATH
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
        "path": SOURCE_P102A_REPAIR_PLAN_PATH,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "payload": payload,
    }


def _normalize_blocked_reasons(values: list[str]) -> list[str]:
    unique = sorted(
        set(values),
        key=lambda reason: (_BLOCKED_REASON_PRIORITY.get(reason, 999), reason),
    )
    return unique


def _command_allowlist() -> list[dict[str, Any]]:
    return [
        {
            "command": spec["command"],
            "allowed_for_planning": True,
            "execution_allowed": False,
            "rationale": spec["rationale"],
        }
        for spec in _COMMAND_SPECS
    ]


def _validation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "validation_001_p102a_readable",
            "artifact_path": SOURCE_P102A_REPAIR_PLAN_PATH,
            "required_readable": True,
            "required_status": _P101_REPAIR_PLAN_READY,
            "failure_action": "REGENERATE_P102A_READINESS_REPAIR_PLAN",
        },
        {
            "requirement_id": "validation_002_p99_readable_ready",
            "artifact_path": _P99_PLAN_PATH,
            "required_readable": True,
            "required_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
            "failure_action": "PREPARE_P99_EXECUTION_PLAN_SURFACE",
        },
        {
            "requirement_id": "validation_003_p100_readable_ready",
            "artifact_path": _P100_PLAN_PATH,
            "required_readable": True,
            "required_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
            "failure_action": "PREPARE_P100_EXECUTION_PLAN_SURFACE",
        },
        {
            "requirement_id": "validation_004_p101_readable_eligible",
            "artifact_path": _P101_GATE_PATH,
            "required_readable": True,
            "required_status": (
                "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
            ),
            "failure_action": "PREPARE_P101_EXECUTION_PLAN_SURFACE",
        },
        {
            "requirement_id": "validation_005_p102_readable_ready",
            "artifact_path": _P102_AUDIT_PATH,
            "required_readable": True,
            "required_status": "COMPRESSION_AUDIT_READY",
            "failure_action": "PREPARE_P102_EXECUTION_PLAN_SURFACE",
        },
    ]


def _rerun_p102_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "rerun_p102_req_001",
            "artifact_path": _P99_PLAN_PATH,
            "required_readable": True,
            "required_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
            "failure_action": "REGENERATE_P99_BEFORE_P102_RERUN",
        },
        {
            "requirement_id": "rerun_p102_req_002",
            "artifact_path": _P100_PLAN_PATH,
            "required_readable": True,
            "required_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
            "failure_action": "REGENERATE_P100_BEFORE_P102_RERUN",
        },
        {
            "requirement_id": "rerun_p102_req_003",
            "artifact_path": _P101_GATE_PATH,
            "required_readable": True,
            "required_status": (
                "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
            ),
            "failure_action": "REGENERATE_P101_BEFORE_P102_RERUN",
        },
    ]


def _selected_commands_for_lane(lane: str) -> list[str]:
    if lane == _LANE_P101_ONLY:
        return [_COMMAND_P101, _COMMAND_P102]
    if lane == _LANE_FULL_CHAIN:
        return [_COMMAND_P99, _COMMAND_P100, _COMMAND_P101, _COMMAND_P102]
    if lane == _LANE_RERUN_ONLY:
        return [_COMMAND_P102]
    return []


def _build_selected_sequence(
    *,
    selected_lane: str,
    source_future_sequence: list[Any],
) -> list[dict[str, Any]]:
    source_seq_by_command: dict[str, str] = {}
    for item in source_future_sequence:
        if isinstance(item, dict):
            command = str(item.get("command", "NOT_COMPUTABLE"))
            source_seq_by_command.setdefault(
                command,
                str(item.get("sequence_id", "NOT_COMPUTABLE")),
            )

    selected_commands = _selected_commands_for_lane(selected_lane)
    sequence: list[dict[str, Any]] = []
    for index, command in enumerate(selected_commands, start=1):
        spec = _COMMAND_INDEX[command]
        sequence.append(
            {
                "sequence_id": f"seq_{index:03d}",
                "command": command,
                "target_artifact_path": spec["target_artifact_path"],
                "purpose": spec["purpose"],
                "execution_allowed": False,
                "source_sequence_id": source_seq_by_command.get(command, "NOT_COMPUTABLE"),
                "expected_status_after_run": spec["expected_status_after_run"],
            }
        )
    return sequence


def _classify(
    *,
    source_observation: dict[str, Any],
) -> tuple[str, str, str, str, str, list[str], list[dict[str, Any]]]:
    if not bool(source_observation["observed"]):
        return (
            _NOT_COMPUTABLE,
            _LANE_NOT_COMPUTABLE,
            "P102A source is missing; P102B cannot compute execution-plan routing.",
            "P102A_READINESS_REPAIR_PLAN_REGENERATION",
            "Missing P102A source blocks deterministic repair execution plan routing.",
            ["P102A_SOURCE_MISSING"],
            [],
        )
    if not bool(source_observation["readable"]):
        return (
            _NOT_COMPUTABLE,
            _LANE_NOT_COMPUTABLE,
            "P102A source is unreadable; P102B cannot compute execution-plan routing.",
            "P102A_READINESS_REPAIR_PLAN_REGENERATION",
            "Unreadable P102A source blocks deterministic repair execution plan routing.",
            ["P102A_SOURCE_UNREADABLE"],
            [],
        )
    if bool(source_observation["malformed_json"]):
        return (
            _NOT_COMPUTABLE,
            _LANE_NOT_COMPUTABLE,
            "P102A source is malformed; P102B cannot compute execution-plan routing.",
            "P102A_READINESS_REPAIR_PLAN_REGENERATION",
            "Malformed P102A source blocks deterministic repair execution plan routing.",
            ["P102A_SOURCE_MALFORMED"],
            [],
        )

    payload = (
        source_observation["payload"]
        if isinstance(source_observation["payload"], dict)
        else {}
    )
    source_repair_status = str(payload.get("p101_readiness_repair_status", _NOT_COMPUTABLE))
    source_recommended_lane = str(payload.get("recommended_next_lane", _NOT_COMPUTABLE))
    source_future_sequence = _as_list(payload.get("future_command_sequence"))
    source_commands = [
        str(item.get("command", "NOT_COMPUTABLE"))
        for item in source_future_sequence
        if isinstance(item, dict)
    ]

    if source_repair_status == _NOT_COMPUTABLE:
        return (
            _ROUTER_BLOCKED,
            _LANE_NOT_COMPUTABLE,
            "P102A repair status is NOT_COMPUTABLE; P102B is blocked.",
            "P102A_READINESS_REPAIR_PLAN_REGENERATION",
            "P102A status NOT_COMPUTABLE blocks safe execution-plan routing.",
            ["P102A_NOT_COMPUTABLE"],
            [],
        )

    if source_repair_status == _P101_REPAIR_NOT_REQUIRED:
        return (
            _ROUTER_NOT_REQUIRED,
            _LANE_NO_REPAIR_REQUIRED,
            "P102A indicates repair not required; no P102B execution plan selection is needed.",
            "P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
            "P102A reports no readiness repair required; passthrough preserved.",
            [],
            [],
        )

    if source_repair_status == _P101_REPAIR_BLOCKED:
        return (
            _ROUTER_BLOCKED,
            _LANE_NOT_COMPUTABLE,
            "P102A repair status is blocked; P102B is blocked.",
            "P101_GATE_ARTIFACT_REGENERATION_PLAN",
            "P102A reports blocked readiness repair; execution-plan routing remains fail-closed.",
            ["P102A_REPAIR_BLOCKED"],
            [],
        )

    if source_repair_status == _P101_REPAIR_PLAN_READY:
        if source_recommended_lane not in _SUPPORTED_P102A_NEXT_LANES:
            return (
                _NOT_COMPUTABLE,
                _LANE_NOT_COMPUTABLE,
                "P102A recommended_next_lane is unsupported for P102B routing.",
                "P102A_READINESS_REPAIR_PLAN_REGENERATION",
                "Unsupported P102A lane prevents deterministic execution-plan routing.",
                ["P102A_RECOMMENDED_LANE_UNSUPPORTED"],
                [],
            )

        blocked_reasons: list[str] = []
        if not source_future_sequence:
            blocked_reasons.append("FUTURE_COMMAND_SEQUENCE_EMPTY")
        unsupported_source_commands = [
            command for command in source_commands if command not in _ALLOWED_COMMANDS
        ]
        if unsupported_source_commands:
            blocked_reasons.append("FUTURE_COMMAND_SEQUENCE_CONTAINS_UNSUPPORTED_COMMAND")
        required_commands = _selected_commands_for_lane(source_recommended_lane)
        if any(command not in source_commands for command in required_commands):
            blocked_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")

        blocked_reasons = _normalize_blocked_reasons(blocked_reasons)
        if blocked_reasons:
            return (
                _ROUTER_BLOCKED,
                _LANE_NOT_COMPUTABLE,
                "P102A future command sequence is empty, unsafe, or inconsistent for required route.",
                "P102A_READINESS_REPAIR_PLAN_REGENERATION",
                "P102A future sequence failed deterministic safety checks; router stays blocked.",
                blocked_reasons,
                [],
            )

        selected_command_sequence = _build_selected_sequence(
            selected_lane=source_recommended_lane,
            source_future_sequence=source_future_sequence,
        )
        if source_recommended_lane == _LANE_P101_ONLY:
            return (
                _ROUTER_READY,
                _LANE_P101_ONLY,
                "P102A ready status and P101-only recommendation map to P102B P101-gate regeneration execution plan surface.",
                _P102C_LANE_P101_ONLY,
                "P102A requested P101-only plan; router selected matching P102B execution-plan surface.",
                [],
                selected_command_sequence,
            )
        if source_recommended_lane == _LANE_FULL_CHAIN:
            return (
                _ROUTER_READY,
                _LANE_FULL_CHAIN,
                "P102A ready status and full-chain recommendation map to P102B full-chain regeneration execution plan surface.",
                _P102C_LANE_FULL_CHAIN,
                "P102A requested full P99→P102 chain plan; router selected matching P102B execution-plan surface.",
                [],
                selected_command_sequence,
            )
        return (
            _ROUTER_READY,
            _LANE_RERUN_ONLY,
            "P102A ready status and rerun-only recommendation map to P102B compression-audit rerun execution plan surface.",
            _P102C_LANE_RERUN_ONLY,
            "P102A requested P102 rerun-only plan; router selected matching P102B execution-plan surface.",
            [],
            selected_command_sequence,
        )

    return (
        _NOT_COMPUTABLE,
        _LANE_NOT_COMPUTABLE,
        "P102A repair status is unsupported; P102B cannot compute execution-plan routing.",
        "P102A_READINESS_REPAIR_PLAN_REGENERATION",
        "Unsupported P102A readiness repair status prevents deterministic routing.",
        ["P102A_RECOMMENDED_LANE_UNSUPPORTED"],
        [],
    )


def build_temporal_continuity_repair_execution_plan_router(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _observe_source(root=root)
    payload = source["payload"] if isinstance(source["payload"], dict) else {}
    source_repair_status = str(payload.get("p101_readiness_repair_status", _NOT_COMPUTABLE))
    source_recommended_lane = str(payload.get("recommended_next_lane", _NOT_COMPUTABLE))
    source_future_sequence = _as_list(payload.get("future_command_sequence"))

    (
        p102b_router_status,
        selected_execution_plan_lane,
        selected_execution_plan_reason,
        recommended_next_lane,
        recommended_next_lane_reason,
        blocked_reasons,
        selected_command_sequence,
    ) = _classify(source_observation=source)

    blocked_reasons = _normalize_blocked_reasons(blocked_reasons)
    degraded_evidence_inputs = _as_list(payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_list(payload.get("inherited_blockers"))
    inherited_drift_flags = _as_list(payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_list(payload.get("semantic_overlap_flags"))

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "execution_plan_router_only": True,
        "repair_execution_plan_router_only": True,
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
        "source_p102a_repair_plan_path": SOURCE_P102A_REPAIR_PLAN_PATH,
        "source_p102a_repair_plan_observed": bool(source["observed"]),
        "source_p102a_repair_plan_readable": bool(source["readable"]),
        "source_p102a_repair_plan_hash": str(source["file_hash"]),
        "source_p102a_repair_status": source_repair_status,
        "source_p102a_recommended_next_lane": source_recommended_lane,
        "source_future_command_sequence_count": len(source_future_sequence),
        "p102b_router_status": p102b_router_status,
        "selected_execution_plan_lane": selected_execution_plan_lane,
        "selected_execution_plan_reason": selected_execution_plan_reason,
        "selected_command_sequence": selected_command_sequence,
        "command_allowlist": _command_allowlist(),
        "validation_requirements": _validation_requirements(),
        "rerun_p102_requirements": _rerun_p102_requirements(),
        "blocked_reasons": blocked_reasons,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "router_strategy_summary": {
            "source_p102a_repair_status": source_repair_status,
            "source_p102a_recommended_next_lane": source_recommended_lane,
            "source_future_command_sequence_count": len(source_future_sequence),
            "selected_execution_plan_lane": selected_execution_plan_lane,
            "selected_command_sequence_count": len(selected_command_sequence),
            "blocked_reason_count": len(blocked_reasons),
            "p102b_router_status": p102b_router_status,
        },
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": list(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_repair_execution_plan_router(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
