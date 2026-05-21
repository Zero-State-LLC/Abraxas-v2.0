from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP101ReadinessRepairPlan.v1"

SOURCE_P102_AUDIT_PATH = (
    "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json"
)
SOURCE_P101_GATE_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json"
)
SOURCE_P100_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json"
)
SOURCE_P99_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json"
)

_P102_DEGRADED_STATUS = "COMPRESSION_AUDIT_DEGRADED"
_P102_P101_REGEN_LANE = (
    "P101_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"
)
_P101_ELIGIBLE_STATUS = (
    "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
)
_P101_ELIGIBLE_NEXT_LANE = (
    "P102_TEMPORAL_CONTINUITY_RECURSIVE_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT"
)
_P100_READY_STATUSES = frozenset(
    {
        "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
        "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_NOT_REQUIRED",
    }
)
_P99_READY_STATUSES = frozenset(
    {
        "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
        "P83_SEQUENCE_RECORD_CREATION_RECORD_NOT_REQUIRED",
    }
)

_P99_STATUS_FIELD = "p83_sequence_record_creation_record_plan_status"
_P100_STATUS_FIELD = "p83_sequence_record_creation_record_creation_plan_status"
_P101_STATUS_FIELD = "p83_sequence_record_creation_record_creation_authorization_gate_status"

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

_FUTURE_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "command": "python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan.py",
        "target_artifact_path": SOURCE_P99_PLAN_PATH,
        "purpose": "Regenerate P99 sequence record creation record plan to restore upstream P99 readiness.",
        "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
    },
    {
        "command": "python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan.py",
        "target_artifact_path": SOURCE_P100_PLAN_PATH,
        "purpose": "Regenerate P100 sequence record creation record creation plan to restore upstream P100 readiness.",
        "expected_status_after_run": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
    },
    {
        "command": "python scripts/run_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate.py",
        "target_artifact_path": SOURCE_P101_GATE_PATH,
        "purpose": "Regenerate P101 authorization gate to restore P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE status.",
        "expected_status_after_run": _P101_ELIGIBLE_STATUS,
    },
    {
        "command": "python scripts/run_temporal_continuity_recursive_authorization_chain_compression_audit.py",
        "target_artifact_path": SOURCE_P102_AUDIT_PATH,
        "purpose": "Rerun P102 compression audit after P99/P100/P101 chain is restored.",
        "expected_status_after_run": "COMPRESSION_AUDIT_READY",
    },
)


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


def _preserve_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


def _observe_source(
    *,
    root: Path,
    rel_path: str,
    status_field: str,
) -> dict[str, Any]:
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    status = "NOT_COMPUTABLE"
    recommended_next_lane = "NOT_COMPUTABLE"
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
                recommended_next_lane = str(
                    parsed.get("recommended_next_lane", "NOT_COMPUTABLE")
                )
            else:
                malformed_json = True

    return {
        "path": rel_path,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "status": status,
        "recommended_next_lane": recommended_next_lane,
        "payload": payload,
    }


def _source_unreadable(obs: dict[str, Any]) -> bool:
    return bool(obs["observed"]) and not bool(obs["readable"])


def _source_malformed(obs: dict[str, Any]) -> bool:
    return bool(obs["readable"]) and bool(obs["malformed_json"])


def _source_missing_or_unreadable_or_malformed(obs: dict[str, Any]) -> bool:
    if not bool(obs["observed"]):
        return True
    if not bool(obs["readable"]):
        return True
    if bool(obs["malformed_json"]):
        return True
    return False


def _chain_weak(
    p99: dict[str, Any],
    p100: dict[str, Any],
) -> bool:
    """Return True if P99 or P100 source chain is missing, unreadable, or not in a ready status."""
    if _source_missing_or_unreadable_or_malformed(p99):
        return True
    if _source_missing_or_unreadable_or_malformed(p100):
        return True
    if str(p99["status"]) not in _P99_READY_STATUSES:
        return True
    if str(p100["status"]) not in _P100_READY_STATUSES:
        return True
    return False


def _build_finding(
    *,
    finding_id: str,
    finding_type: str,
    severity: str,
    source_path: str,
    observed_status: str,
    expected_status: str,
    repair_required: bool,
    recommendation: str,
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "finding_type": finding_type,
        "severity": severity,
        "source_path": source_path,
        "observed_status": observed_status,
        "expected_status": expected_status,
        "repair_required": repair_required,
        "recommendation": recommendation,
    }


def _build_repair_item(
    *,
    repair_item_id: str,
    target_lane: str,
    target_artifact_path: str,
    current_status: str,
    required_status: str,
    repair_strategy: str,
    future_command: str,
    blocking_reason: str,
) -> dict[str, Any]:
    return {
        "repair_item_id": repair_item_id,
        "target_lane": target_lane,
        "target_artifact_path": target_artifact_path,
        "current_status": current_status,
        "required_status": required_status,
        "repair_strategy": repair_strategy,
        "future_command": future_command,
        "execution_allowed": False,
        "blocking_reason": blocking_reason,
    }


def _build_future_command_item(
    *,
    sequence_id: str,
    command_spec: dict[str, str],
    preconditions: list[str],
) -> dict[str, Any]:
    return {
        "sequence_id": sequence_id,
        "command": command_spec["command"],
        "target_artifact_path": command_spec["target_artifact_path"],
        "purpose": command_spec["purpose"],
        "execution_allowed": False,
        "preconditions": preconditions,
        "expected_status_after_run": command_spec["expected_status_after_run"],
    }


def _build_validation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "validation_001_p99_exists_readable",
            "description": "P99 output exists and is readable",
            "artifact_path": SOURCE_P99_PLAN_PATH,
            "check": "file_exists_and_readable",
            "failure_action": "REPAIR_P99_FIRST",
        },
        {
            "requirement_id": "validation_002_p99_status_ready",
            "description": "P99 status is ready or not-required",
            "artifact_path": SOURCE_P99_PLAN_PATH,
            "check": "status_in_allowed_set",
            "allowed_statuses": sorted(_P99_READY_STATUSES),
            "failure_action": "REGENERATE_P99",
        },
        {
            "requirement_id": "validation_003_p100_exists_readable",
            "description": "P100 output exists and is readable",
            "artifact_path": SOURCE_P100_PLAN_PATH,
            "check": "file_exists_and_readable",
            "failure_action": "REPAIR_P100_FIRST",
        },
        {
            "requirement_id": "validation_004_p100_status_ready",
            "description": "P100 status is ready or not-required",
            "artifact_path": SOURCE_P100_PLAN_PATH,
            "check": "status_in_allowed_set",
            "allowed_statuses": sorted(_P100_READY_STATUSES),
            "failure_action": "REGENERATE_P100",
        },
        {
            "requirement_id": "validation_005_p101_exists_readable",
            "description": "P101 output exists and is readable",
            "artifact_path": SOURCE_P101_GATE_PATH,
            "check": "file_exists_and_readable",
            "failure_action": "REPAIR_P101_FIRST",
        },
        {
            "requirement_id": "validation_006_p101_status_eligible",
            "description": "P101 status is eligible or not-required",
            "artifact_path": SOURCE_P101_GATE_PATH,
            "check": "status_in_allowed_set",
            "allowed_statuses": sorted(
                {
                    _P101_ELIGIBLE_STATUS,
                    "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED",
                }
            ),
            "failure_action": "REGENERATE_P101",
        },
        {
            "requirement_id": "validation_007_p101_lane_recommends_p102",
            "description": "P101 recommended_next_lane is P102_TEMPORAL_CONTINUITY_RECURSIVE_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT when eligible",
            "artifact_path": SOURCE_P101_GATE_PATH,
            "check": "recommended_next_lane_equals",
            "expected_lane": _P101_ELIGIBLE_NEXT_LANE,
            "failure_action": "REGENERATE_P101",
        },
        {
            "requirement_id": "validation_008_all_authority_fields_false",
            "description": "All authority fields in the repair plan output remain false",
            "artifact_path": "out/temporal_continuity_p101_readiness_repair_plan/latest.json",
            "check": "all_authority_fields_false",
            "authority_fields": sorted(_DENIED_AUTHORITY),
            "failure_action": "REJECT_ARTIFACT_AS_INVALID",
        },
        {
            "requirement_id": "validation_009_p102_rerun_exists_readable",
            "description": "P102 rerun output exists and is readable after future rerun",
            "artifact_path": SOURCE_P102_AUDIT_PATH,
            "check": "file_exists_and_readable",
            "failure_action": "REPAIR_P102_FIRST",
        },
        {
            "requirement_id": "validation_010_p102_no_longer_routes_to_p101_regen",
            "description": "P102 no longer routes to P101 regeneration after future repair unless chain evidence still blocks",
            "artifact_path": SOURCE_P102_AUDIT_PATH,
            "check": "recommended_next_lane_not_equals",
            "disallowed_lane": _P102_P101_REGEN_LANE,
            "failure_action": "RERUN_CHAIN_REPAIR_SEQUENCE",
        },
    ]


def _build_rerun_p102_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "rerun_p102_req_001",
            "required_artifact_path": SOURCE_P99_PLAN_PATH,
            "required_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
            "required_readable": True,
            "failure_action": "REGENERATE_P99_BEFORE_P102_RERUN",
        },
        {
            "requirement_id": "rerun_p102_req_002",
            "required_artifact_path": SOURCE_P100_PLAN_PATH,
            "required_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
            "required_readable": True,
            "failure_action": "REGENERATE_P100_BEFORE_P102_RERUN",
        },
        {
            "requirement_id": "rerun_p102_req_003",
            "required_artifact_path": SOURCE_P101_GATE_PATH,
            "required_status": _P101_ELIGIBLE_STATUS,
            "required_readable": True,
            "failure_action": "REGENERATE_P101_BEFORE_P102_RERUN",
        },
    ]


def _classify(
    *,
    p102: dict[str, Any],
    p101: dict[str, Any],
    p100: dict[str, Any],
    p99: dict[str, Any],
) -> tuple[str, str, str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (status, recommended_next_lane, reason, findings, repair_items, future_commands)."""

    # Rule 1: P102 missing/unreadable/malformed → NOT_COMPUTABLE
    if _source_missing_or_unreadable_or_malformed(p102):
        finding_type = (
            "P102_DEGRADED"
            if bool(p102["observed"]) and bool(p102["readable"])
            else (
                "P102_DEGRADED"
                if bool(p102["observed"])
                else "P102_DEGRADED"
            )
        )
        # More specific finding types for P102 unreadable/malformed cases
        if not bool(p102["observed"]):
            finding_type = "P102_DEGRADED"
            observed_status = "MISSING"
        elif not bool(p102["readable"]):
            finding_type = "P102_DEGRADED"
            observed_status = "UNREADABLE"
        else:
            finding_type = "P102_DEGRADED"
            observed_status = "MALFORMED"

        findings = [
            _build_finding(
                finding_id="finding_001",
                finding_type=finding_type,
                severity="CRITICAL",
                source_path=SOURCE_P102_AUDIT_PATH,
                observed_status=observed_status,
                expected_status=_P102_DEGRADED_STATUS,
                repair_required=True,
                recommendation="Regenerate P102 compression audit before computing P101 readiness repair plan.",
            )
        ]
        return (
            "NOT_COMPUTABLE",
            "P102_COMPRESSION_AUDIT_REGENERATION",
            "P102 compression audit source is missing, unreadable, or malformed; cannot compute P101 readiness repair plan.",
            findings,
            [],
            [],
        )

    p102_status = str(p102["status"])
    p102_next_lane = str(p102["recommended_next_lane"])

    # Rule 2: P102 not degraded or not routing to P101 regen → NOT_REQUIRED
    if p102_status != _P102_DEGRADED_STATUS or p102_next_lane != _P102_P101_REGEN_LANE:
        findings = [
            _build_finding(
                finding_id="finding_001",
                finding_type="NO_REPAIR_REQUIRED",
                severity="INFO",
                source_path=SOURCE_P102_AUDIT_PATH,
                observed_status=p102_status,
                expected_status=_P102_DEGRADED_STATUS,
                repair_required=False,
                recommendation="P102 is not degraded with a P101 regeneration route; no P101 readiness repair is required.",
            )
        ]
        return (
            "P101_READINESS_REPAIR_NOT_REQUIRED",
            "P102_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
            f"P102 chain_compression_audit_status is {p102_status!r} and recommended_next_lane is {p102_next_lane!r}; P101 readiness repair is not required.",
            findings,
            [],
            [],
        )

    # P102 is degraded and routes to P101 regeneration — classify further

    # Rule 3: P101 missing/unreadable/malformed → BLOCKED
    if _source_missing_or_unreadable_or_malformed(p101):
        if not bool(p101["observed"]):
            p101_finding_type = "P101_MISSING"
            p101_obs_status = "MISSING"
        elif not bool(p101["readable"]):
            p101_finding_type = "P101_UNREADABLE"
            p101_obs_status = "UNREADABLE"
        else:
            p101_finding_type = "P101_MALFORMED"
            p101_obs_status = "MALFORMED"

        findings = [
            _build_finding(
                finding_id="finding_001",
                finding_type="P102_DEGRADED",
                severity="HIGH",
                source_path=SOURCE_P102_AUDIT_PATH,
                observed_status=p102_status,
                expected_status="COMPRESSION_AUDIT_READY",
                repair_required=True,
                recommendation="P102 is degraded and routes to P101 regeneration.",
            ),
            _build_finding(
                finding_id="finding_002",
                finding_type=p101_finding_type,
                severity="CRITICAL",
                source_path=SOURCE_P101_GATE_PATH,
                observed_status=p101_obs_status,
                expected_status=_P101_ELIGIBLE_STATUS,
                repair_required=True,
                recommendation="P101 gate artifact must be regenerated before P101 readiness repair can be planned.",
            ),
        ]
        return (
            "P101_READINESS_REPAIR_BLOCKED",
            "P101_GATE_ARTIFACT_REGENERATION_PLAN",
            f"P102 is degraded and routes to P101 regeneration, but P101 source is {p101_obs_status.lower()}; repair plan is blocked until P101 gate artifact is regenerated.",
            findings,
            [],
            [],
        )

    p101_status = str(p101["status"])
    p101_next_lane = str(p101["recommended_next_lane"])

    # Rule 4: P101 readable but not eligible
    if p101_status != _P101_ELIGIBLE_STATUS:
        findings = [
            _build_finding(
                finding_id="finding_001",
                finding_type="P102_DEGRADED",
                severity="HIGH",
                source_path=SOURCE_P102_AUDIT_PATH,
                observed_status=p102_status,
                expected_status="COMPRESSION_AUDIT_READY",
                repair_required=True,
                recommendation="P102 is degraded and routes to P101 regeneration.",
            ),
            _build_finding(
                finding_id="finding_002",
                finding_type="P101_NOT_ELIGIBLE",
                severity="HIGH",
                source_path=SOURCE_P101_GATE_PATH,
                observed_status=p101_status,
                expected_status=_P101_ELIGIBLE_STATUS,
                repair_required=True,
                recommendation="Regenerate P101 authorization gate to restore eligible status.",
            ),
        ]
        repair_items = [
            _build_repair_item(
                repair_item_id="repair_item_001",
                target_lane="P101",
                target_artifact_path=SOURCE_P101_GATE_PATH,
                current_status=p101_status,
                required_status=_P101_ELIGIBLE_STATUS,
                repair_strategy="REGENERATE_P101_AUTHORIZATION_GATE",
                future_command=_FUTURE_COMMANDS[2]["command"],
                blocking_reason="P101_NOT_ELIGIBLE",
            ),
            _build_repair_item(
                repair_item_id="repair_item_002",
                target_lane="P102",
                target_artifact_path=SOURCE_P102_AUDIT_PATH,
                current_status=p102_status,
                required_status="COMPRESSION_AUDIT_READY",
                repair_strategy="RERUN_P102_AFTER_P101_REGENERATION",
                future_command=_FUTURE_COMMANDS[3]["command"],
                blocking_reason="P101_NOT_ELIGIBLE_BLOCKS_P102",
            ),
        ]
        future_commands = [
            _build_future_command_item(
                sequence_id="seq_001",
                command_spec=_FUTURE_COMMANDS[2],
                preconditions=[
                    "P99 output readable and status ready",
                    "P100 output readable and status ready",
                ],
            ),
            _build_future_command_item(
                sequence_id="seq_002",
                command_spec=_FUTURE_COMMANDS[3],
                preconditions=[
                    f"P101 status equals {_P101_ELIGIBLE_STATUS}",
                    f"P101 recommended_next_lane equals {_P101_ELIGIBLE_NEXT_LANE}",
                ],
            ),
        ]
        return (
            "P101_READINESS_REPAIR_PLAN_READY",
            "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN",
            f"P102 degraded and routes to P101 regeneration; P101 is readable but status is {p101_status!r}, not eligible; regenerate P101 gate.",
            findings,
            repair_items,
            future_commands,
        )

    # P101 is eligible — check P99/P100 chain coherence
    chain_is_weak = _chain_weak(p99, p100)

    # Also check lane mismatch on P101
    lane_mismatch = p101_next_lane != _P101_ELIGIBLE_NEXT_LANE

    if chain_is_weak or lane_mismatch:
        # Rule 5: P101 eligible but weak P99/P100 chain
        findings = [
            _build_finding(
                finding_id="finding_001",
                finding_type="P102_DEGRADED",
                severity="HIGH",
                source_path=SOURCE_P102_AUDIT_PATH,
                observed_status=p102_status,
                expected_status="COMPRESSION_AUDIT_READY",
                repair_required=True,
                recommendation="P102 is degraded and routes to P101 regeneration.",
            ),
        ]
        finding_idx = 2

        # P99 findings
        if _source_missing_or_unreadable_or_malformed(p99):
            findings.append(
                _build_finding(
                    finding_id=f"finding_{finding_idx:03d}",
                    finding_type="P99_SOURCE_WEAK",
                    severity="HIGH",
                    source_path=SOURCE_P99_PLAN_PATH,
                    observed_status=(
                        "MISSING"
                        if not bool(p99["observed"])
                        else ("UNREADABLE" if not bool(p99["readable"]) else "MALFORMED")
                    ),
                    expected_status="P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
                    repair_required=True,
                    recommendation="Regenerate P99 record plan to restore source chain coherence.",
                )
            )
            finding_idx += 1
        elif str(p99["status"]) not in _P99_READY_STATUSES:
            findings.append(
                _build_finding(
                    finding_id=f"finding_{finding_idx:03d}",
                    finding_type="P99_SOURCE_WEAK",
                    severity="HIGH",
                    source_path=SOURCE_P99_PLAN_PATH,
                    observed_status=str(p99["status"]),
                    expected_status="P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
                    repair_required=True,
                    recommendation="Regenerate P99 record plan to restore ready status.",
                )
            )
            finding_idx += 1

        # P100 findings
        if _source_missing_or_unreadable_or_malformed(p100):
            findings.append(
                _build_finding(
                    finding_id=f"finding_{finding_idx:03d}",
                    finding_type="P100_SOURCE_WEAK",
                    severity="HIGH",
                    source_path=SOURCE_P100_PLAN_PATH,
                    observed_status=(
                        "MISSING"
                        if not bool(p100["observed"])
                        else ("UNREADABLE" if not bool(p100["readable"]) else "MALFORMED")
                    ),
                    expected_status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
                    repair_required=True,
                    recommendation="Regenerate P100 record creation plan to restore source chain coherence.",
                )
            )
            finding_idx += 1
        elif str(p100["status"]) not in _P100_READY_STATUSES:
            findings.append(
                _build_finding(
                    finding_id=f"finding_{finding_idx:03d}",
                    finding_type="P100_SOURCE_WEAK",
                    severity="HIGH",
                    source_path=SOURCE_P100_PLAN_PATH,
                    observed_status=str(p100["status"]),
                    expected_status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
                    repair_required=True,
                    recommendation="Regenerate P100 record creation plan to restore ready status.",
                )
            )
            finding_idx += 1

        if lane_mismatch and not (chain_is_weak):
            findings.append(
                _build_finding(
                    finding_id=f"finding_{finding_idx:03d}",
                    finding_type="P101_LANE_MISMATCH",
                    severity="MEDIUM",
                    source_path=SOURCE_P101_GATE_PATH,
                    observed_status=p101_next_lane,
                    expected_status=_P101_ELIGIBLE_NEXT_LANE,
                    repair_required=True,
                    recommendation="Regenerate P101 gate to correct the recommended_next_lane mismatch.",
                )
            )
            finding_idx += 1

        findings.append(
            _build_finding(
                finding_id=f"finding_{finding_idx:03d}",
                finding_type="P99_P100_P101_CHAIN_INCONSISTENT",
                severity="HIGH",
                source_path=SOURCE_P101_GATE_PATH,
                observed_status="CHAIN_INCONSISTENT",
                expected_status="CHAIN_COHERENT",
                repair_required=True,
                recommendation="Regenerate P99/P100/P101 chain to restore full coherence before rerunning P102.",
            )
        )

        repair_items = [
            _build_repair_item(
                repair_item_id="repair_item_001",
                target_lane="P99",
                target_artifact_path=SOURCE_P99_PLAN_PATH,
                current_status=str(p99["status"]) if bool(p99["observed"]) and bool(p99["readable"]) and not bool(p99["malformed_json"]) else "NOT_COMPUTABLE",
                required_status="P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
                repair_strategy="REGENERATE_P99_RECORD_PLAN",
                future_command=_FUTURE_COMMANDS[0]["command"],
                blocking_reason="P99_P100_P101_CHAIN_INCONSISTENT",
            ),
            _build_repair_item(
                repair_item_id="repair_item_002",
                target_lane="P100",
                target_artifact_path=SOURCE_P100_PLAN_PATH,
                current_status=str(p100["status"]) if bool(p100["observed"]) and bool(p100["readable"]) and not bool(p100["malformed_json"]) else "NOT_COMPUTABLE",
                required_status="P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
                repair_strategy="REGENERATE_P100_RECORD_CREATION_PLAN",
                future_command=_FUTURE_COMMANDS[1]["command"],
                blocking_reason="P99_P100_P101_CHAIN_INCONSISTENT",
            ),
            _build_repair_item(
                repair_item_id="repair_item_003",
                target_lane="P101",
                target_artifact_path=SOURCE_P101_GATE_PATH,
                current_status=p101_status,
                required_status=_P101_ELIGIBLE_STATUS,
                repair_strategy="REGENERATE_P101_AUTHORIZATION_GATE",
                future_command=_FUTURE_COMMANDS[2]["command"],
                blocking_reason="P99_P100_P101_CHAIN_INCONSISTENT",
            ),
            _build_repair_item(
                repair_item_id="repair_item_004",
                target_lane="P102",
                target_artifact_path=SOURCE_P102_AUDIT_PATH,
                current_status=p102_status,
                required_status="COMPRESSION_AUDIT_READY",
                repair_strategy="RERUN_P102_AFTER_CHAIN_REGENERATION",
                future_command=_FUTURE_COMMANDS[3]["command"],
                blocking_reason="P99_P100_P101_CHAIN_INCONSISTENT",
            ),
        ]
        future_commands = [
            _build_future_command_item(
                sequence_id="seq_001",
                command_spec=_FUTURE_COMMANDS[0],
                preconditions=[
                    "P98 output readable and status eligible",
                ],
            ),
            _build_future_command_item(
                sequence_id="seq_002",
                command_spec=_FUTURE_COMMANDS[1],
                preconditions=[
                    "P99 output readable and status ready",
                ],
            ),
            _build_future_command_item(
                sequence_id="seq_003",
                command_spec=_FUTURE_COMMANDS[2],
                preconditions=[
                    "P99 output readable and status ready",
                    "P100 output readable and status ready",
                ],
            ),
            _build_future_command_item(
                sequence_id="seq_004",
                command_spec=_FUTURE_COMMANDS[3],
                preconditions=[
                    f"P101 status equals {_P101_ELIGIBLE_STATUS}",
                    f"P101 recommended_next_lane equals {_P101_ELIGIBLE_NEXT_LANE}",
                ],
            ),
        ]
        return (
            "P101_READINESS_REPAIR_PLAN_READY",
            "P102B_P99_P100_P101_CHAIN_REGENERATION_EXECUTION_PLAN",
            "P102 degraded and routes to P101 regeneration; P101 is eligible but P99/P100 source chain is weak or inconsistent; regenerate P99/P100/P101 chain.",
            findings,
            repair_items,
            future_commands,
        )

    # Rule 6: P102 degraded but P99/P100/P101 all readable and route coherently
    findings = [
        _build_finding(
            finding_id="finding_001",
            finding_type="P102_DEGRADED",
            severity="HIGH",
            source_path=SOURCE_P102_AUDIT_PATH,
            observed_status=p102_status,
            expected_status="COMPRESSION_AUDIT_READY",
            repair_required=True,
            recommendation="Rerun P102 compression audit after confirming P99/P100/P101 chain is coherent.",
        ),
        _build_finding(
            finding_id="finding_002",
            finding_type="P102_RERUN_REQUIRED",
            severity="MEDIUM",
            source_path=SOURCE_P102_AUDIT_PATH,
            observed_status=p102_status,
            expected_status="COMPRESSION_AUDIT_READY",
            repair_required=True,
            recommendation="P99/P100/P101 chain is coherent; rerun P102 to re-evaluate compression audit.",
        ),
    ]
    repair_items = [
        _build_repair_item(
            repair_item_id="repair_item_001",
            target_lane="P102",
            target_artifact_path=SOURCE_P102_AUDIT_PATH,
            current_status=p102_status,
            required_status="COMPRESSION_AUDIT_READY",
            repair_strategy="RERUN_P102_COMPRESSION_AUDIT",
            future_command=_FUTURE_COMMANDS[3]["command"],
            blocking_reason="P102_DEGRADED_CHAIN_OTHERWISE_COHERENT",
        ),
    ]
    future_commands = [
        _build_future_command_item(
            sequence_id="seq_001",
            command_spec=_FUTURE_COMMANDS[3],
            preconditions=[
                f"P101 status equals {_P101_ELIGIBLE_STATUS}",
                f"P101 recommended_next_lane equals {_P101_ELIGIBLE_NEXT_LANE}",
                "P99 output readable and status ready",
                "P100 output readable and status ready",
            ],
        ),
    ]
    return (
        "P101_READINESS_REPAIR_PLAN_READY",
        "P102B_COMPRESSION_AUDIT_RERUN_EXECUTION_PLAN",
        "P102 degraded and routes to P101 regeneration, but P99/P100/P101 are all readable and route coherently; rerun P102 compression audit.",
        findings,
        repair_items,
        future_commands,
    )


def build_temporal_continuity_p101_readiness_repair_plan(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)

    p102 = _observe_source(
        root=root,
        rel_path=SOURCE_P102_AUDIT_PATH,
        status_field="chain_compression_audit_status",
    )
    p101 = _observe_source(
        root=root,
        rel_path=SOURCE_P101_GATE_PATH,
        status_field=_P101_STATUS_FIELD,
    )
    p100 = _observe_source(
        root=root,
        rel_path=SOURCE_P100_PLAN_PATH,
        status_field=_P100_STATUS_FIELD,
    )
    p99 = _observe_source(
        root=root,
        rel_path=SOURCE_P99_PLAN_PATH,
        status_field=_P99_STATUS_FIELD,
    )

    # Inherit degraded evidence and flags from P102 when available
    p102_payload = p102["payload"] if isinstance(p102["payload"], dict) else {}
    degraded_evidence_inputs = _preserve_list(p102_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _preserve_list(p102_payload.get("inherited_blockers"))
    inherited_drift_flags = _preserve_list(p102_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _preserve_list(p102_payload.get("semantic_overlap_flags"))

    (
        repair_status,
        recommended_next_lane,
        recommended_next_lane_reason,
        findings,
        repair_items,
        future_commands,
    ) = _classify(p102=p102, p101=p101, p100=p100, p99=p99)

    # Build repair strategy summary
    repair_plan_strategies = sorted({item["repair_strategy"] for item in repair_items})
    repair_strategy_summary: dict[str, Any] = {
        "p102_audit_status": str(p102["status"]),
        "p101_gate_status": str(p101["status"]),
        "p100_plan_status": str(p100["status"]),
        "p99_plan_status": str(p99["status"]),
        "findings_count": len(findings),
        "repair_plan_items_count": len(repair_items),
        "future_command_sequence_count": len(future_commands),
        "repair_strategies": repair_plan_strategies,
        "p101_readiness_repair_status": repair_status,
    }

    # Full future command sequence (all 4 planned commands always present)
    full_future_command_sequence = [
        _build_future_command_item(
            sequence_id=f"seq_{i + 1:03d}",
            command_spec=cmd,
            preconditions=(
                future_commands[i]["preconditions"]
                if i < len(future_commands) and future_commands[i]["command"] == cmd["command"]
                else _default_preconditions(i)
            ),
        )
        for i, cmd in enumerate(_FUTURE_COMMANDS)
    ]

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "repair_plan_only": True,
        "readiness_repair_plan_only": True,
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
        # P102 source fields
        "source_p102_audit_path": SOURCE_P102_AUDIT_PATH,
        "source_p102_audit_observed": bool(p102["observed"]),
        "source_p102_audit_readable": bool(p102["readable"]),
        "source_p102_audit_hash": str(p102["file_hash"]),
        "source_p102_audit_status": str(p102["status"]),
        "source_p102_chain_recommendation": str(
            p102_payload.get("chain_recommendation", "NOT_COMPUTABLE")
        ),
        "source_p102_recommended_next_lane": str(p102["recommended_next_lane"]),
        # P101 source fields
        "source_p101_gate_path": SOURCE_P101_GATE_PATH,
        "source_p101_gate_observed": bool(p101["observed"]),
        "source_p101_gate_readable": bool(p101["readable"]),
        "source_p101_gate_hash": str(p101["file_hash"]),
        "source_p101_gate_status": str(p101["status"]),
        "source_p101_recommended_next_lane": str(p101["recommended_next_lane"]),
        # P100 source fields
        "source_p100_plan_path": SOURCE_P100_PLAN_PATH,
        "source_p100_plan_observed": bool(p100["observed"]),
        "source_p100_plan_readable": bool(p100["readable"]),
        "source_p100_plan_hash": str(p100["file_hash"]),
        "source_p100_plan_status": str(p100["status"]),
        "source_p100_recommended_next_lane": str(p100["recommended_next_lane"]),
        # P99 source fields
        "source_p99_plan_path": SOURCE_P99_PLAN_PATH,
        "source_p99_plan_observed": bool(p99["observed"]),
        "source_p99_plan_readable": bool(p99["readable"]),
        "source_p99_plan_hash": str(p99["file_hash"]),
        "source_p99_plan_status": str(p99["status"]),
        "source_p99_recommended_next_lane": str(p99["recommended_next_lane"]),
        # Readiness repair fields
        "p101_readiness_repair_status": repair_status,
        "p101_readiness_repair_required": repair_status
        not in {"NOT_COMPUTABLE", "P101_READINESS_REPAIR_NOT_REQUIRED"},
        "p101_readiness_repair_allowed": False,
        "p101_readiness_findings": sorted(findings, key=lambda f: str(f["finding_id"])),
        "repair_plan_items": sorted(repair_items, key=lambda r: str(r["repair_item_id"])),
        "future_command_sequence": full_future_command_sequence,
        "validation_requirements": _build_validation_requirements(),
        "rerun_p102_requirements": _build_rerun_p102_requirements(),
        # Inherited evidence
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        # Summary and routing
        "repair_strategy_summary": repair_strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": list(_DENIED_AUTHORITY),
    }

    packet = {
        **packet_base,
        "packet_hash": canonical_hash(packet_base),
    }
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _default_preconditions(index: int) -> list[str]:
    """Default preconditions for each command index when not overridden by classify."""
    if index == 0:
        return ["P98 output readable and status eligible"]
    if index == 1:
        return ["P99 output readable and status ready"]
    if index == 2:
        return [
            "P99 output readable and status ready",
            "P100 output readable and status ready",
        ]
    return [
        f"P101 status equals {_P101_ELIGIBLE_STATUS}",
        f"P101 recommended_next_lane equals {_P101_ELIGIBLE_NEXT_LANE}",
    ]


def write_temporal_continuity_p101_readiness_repair_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
