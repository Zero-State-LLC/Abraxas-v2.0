from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP83RegenerationAuthorizationGate.v1"
SOURCE_P88_EXECUTION_PLAN_PATH = (
    "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json"
)
EXPECTED_SOURCE_RECOMMENDED_NEXT_LANE = (
    "P89_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_GATE"
)
ALLOWED_FUTURE_RUNNER_COMMAND = (
    "python scripts/run_temporal_continuity_p79_authorization_gate_status_repair_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
)

_GATE_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_REGENERATION_AUTHORIZATION_ELIGIBLE",
    "P83_REGENERATION_AUTHORIZATION_DENIED",
    "P83_REGENERATION_AUTHORIZATION_NOT_REQUIRED",
)

_ELIGIBILITY_REASON_ORDER = (
    "P88_EXECUTION_PLAN_READY",
    "P88_RECOMMENDS_P89_GATE",
    "P88_COMMAND_EXACT_MATCH",
    "P88_EXPECTED_OUTPUT_EXACT_MATCH",
    "P88_AUTHORITY_LOCKS_FALSE",
    "P83_REGENERATION_ELIGIBLE_BUT_NOT_GRANTED",
)
_ELIGIBILITY_REASON_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_ELIGIBILITY_REASON_ORDER)
}

_DENIAL_REASON_ORDER = (
    "P88_SOURCE_MISSING",
    "P88_SOURCE_UNREADABLE",
    "P88_SOURCE_MALFORMED_JSON",
    "P88_NOT_COMPUTABLE",
    "P88_EXECUTION_PLAN_BLOCKED",
    "P88_REGENERATION_NOT_REQUIRED",
    "P88_RECOMMENDED_LANE_MISMATCH",
    "P88_COMMAND_MISMATCH",
    "P88_EXPECTED_OUTPUT_PATH_MISMATCH",
    "P88_AUTHORITY_LOCK_VIOLATION",
    "AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P89",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_DENIAL_REASON_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_DENIAL_REASON_ORDER)
}

_PREREQUISITE_CHECK_ORDER = (
    "prerequisite_001_source_exists_readable",
    "prerequisite_002_source_status_ready",
    "prerequisite_003_source_lane_exact_match",
    "prerequisite_004_command_exact_match",
    "prerequisite_005_expected_output_exact_match",
    "prerequisite_006_authority_locks_false",
)
_PREREQUISITE_CHECK_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_PREREQUISITE_CHECK_ORDER)
}

_DENIED_AUTHORITY = (
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

_P88_AUTHORITY_FIELDS = (
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


def _all_p88_authority_fields_false(payload: dict[str, Any]) -> bool:
    return all(payload.get(field) is False for field in _P88_AUTHORITY_FIELDS) and (
        payload.get("p83_regeneration_execution_allowed") is False
    )


def _prerequisite_checks(
    *,
    source_observed: bool,
    source_readable: bool,
    source_status: str,
    source_recommended_lane: str,
    source_command: str,
    source_expected_output_path: str,
    authority_locks_false: bool,
) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "prerequisite_001_source_exists_readable",
            "check_type": "source_exists_readable",
            "path": SOURCE_P88_EXECUTION_PLAN_PATH,
            "required_status": "observed=true;readable=true",
            "satisfied": source_observed and source_readable,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_002_source_status_ready",
            "check_type": "status_exact_match",
            "path": SOURCE_P88_EXECUTION_PLAN_PATH,
            "required_status": (
                "p83_regeneration_execution_plan_status=P83_REGENERATION_EXECUTION_PLAN_READY"
            ),
            "satisfied": source_status == "P83_REGENERATION_EXECUTION_PLAN_READY",
            "failure_action": "DENY_AUTHORIZATION_ELIGIBILITY_AND_ROUTE_TO_P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_003_source_lane_exact_match",
            "check_type": "recommended_lane_exact_match",
            "path": "recommended_next_lane",
            "required_status": EXPECTED_SOURCE_RECOMMENDED_NEXT_LANE,
            "satisfied": source_recommended_lane == EXPECTED_SOURCE_RECOMMENDED_NEXT_LANE,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_004_command_exact_match",
            "check_type": "exact_command_match",
            "path": "future_runner_command",
            "required_status": ALLOWED_FUTURE_RUNNER_COMMAND,
            "satisfied": source_command == ALLOWED_FUTURE_RUNNER_COMMAND,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_005_expected_output_exact_match",
            "check_type": "exact_expected_output_path_match",
            "path": "expected_output_path",
            "required_status": EXPECTED_OUTPUT_PATH,
            "satisfied": source_expected_output_path == EXPECTED_OUTPUT_PATH,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_006_authority_locks_false",
            "check_type": "source_authority_lock_check",
            "path": SOURCE_P88_EXECUTION_PLAN_PATH,
            "required_status": (
                "all_authority_fields=false_and_p83_regeneration_execution_allowed=false"
            ),
            "satisfied": authority_locks_false,
            "failure_action": "DENY_AUTHORIZATION_ELIGIBILITY_AND_FAIL_CLOSED_ON_AUTHORITY_LOCK_VIOLATION",
        },
    ]
    return sorted(
        checks,
        key=lambda item: _PREREQUISITE_CHECK_ORDER_INDEX.get(
            str(item["check_id"]), 10_000
        ),
    )


def _classify(p88: dict[str, Any]) -> dict[str, Any]:
    p88_status = str(p88["status"])
    payload = p88.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}
    source_recommended_lane = str(payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE"))
    source_command = str(payload_dict.get("future_runner_command", "NOT_COMPUTABLE"))
    source_expected_output_path = str(payload_dict.get("expected_output_path", "NOT_COMPUTABLE"))

    if not p88["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P88 execution plan source is missing; regenerate P88 before deriving P89 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P88_SOURCE_MISSING"],
            "source_recommended_lane": source_recommended_lane,
            "source_command": "NOT_COMPUTABLE",
            "source_expected_output_path": "NOT_COMPUTABLE",
            "authority_locks_false": False,
        }

    if not p88["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P88 execution plan source is unreadable; regenerate P88 before deriving P89 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P88_SOURCE_UNREADABLE"],
            "source_recommended_lane": source_recommended_lane,
            "source_command": "NOT_COMPUTABLE",
            "source_expected_output_path": "NOT_COMPUTABLE",
            "authority_locks_false": False,
        }

    if p88["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P88 execution plan source is malformed JSON; regenerate P88 before deriving P89 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P88_SOURCE_MALFORMED_JSON"],
            "source_recommended_lane": source_recommended_lane,
            "source_command": "NOT_COMPUTABLE",
            "source_expected_output_path": "NOT_COMPUTABLE",
            "authority_locks_false": False,
        }

    if p88_status == "NOT_COMPUTABLE":
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_DENIED",
            "eligible": False,
            "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P88 reports NOT_COMPUTABLE; authorization eligibility is denied until P88 is regenerated."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P88_NOT_COMPUTABLE"],
            "source_recommended_lane": source_recommended_lane,
            "source_command": source_command,
            "source_expected_output_path": source_expected_output_path,
            "authority_locks_false": _all_p88_authority_fields_false(payload_dict),
        }

    if p88_status == "P83_REGENERATION_EXECUTION_PLAN_BLOCKED":
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_DENIED",
            "eligible": False,
            "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P88 reports execution planning blocked; authorization eligibility is denied until P88 is regenerated."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P88_EXECUTION_PLAN_BLOCKED"],
            "source_recommended_lane": source_recommended_lane,
            "source_command": source_command,
            "source_expected_output_path": source_expected_output_path,
            "authority_locks_false": _all_p88_authority_fields_false(payload_dict),
        }

    if p88_status == "P83_REGENERATION_EXECUTION_NOT_REQUIRED":
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_NOT_REQUIRED",
            "eligible": False,
            "recommended_next_lane": (
                "P90_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P88 reports P83 regeneration execution not required; P89 authorization remains not required."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P88_REGENERATION_NOT_REQUIRED"],
            "source_recommended_lane": source_recommended_lane,
            "source_command": source_command,
            "source_expected_output_path": source_expected_output_path,
            "authority_locks_false": _all_p88_authority_fields_false(payload_dict),
        }

    if p88_status == "P83_REGENERATION_EXECUTION_PLAN_READY":
        lane_match = source_recommended_lane == EXPECTED_SOURCE_RECOMMENDED_NEXT_LANE
        command_match = source_command == ALLOWED_FUTURE_RUNNER_COMMAND
        output_match = source_expected_output_path == EXPECTED_OUTPUT_PATH
        authority_locks_false = _all_p88_authority_fields_false(payload_dict)

        if lane_match and command_match and output_match and authority_locks_false:
            return {
                "status": "P83_REGENERATION_AUTHORIZATION_ELIGIBLE",
                "eligible": True,
                "recommended_next_lane": (
                    "P90_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_PLAN"
                ),
                "recommended_next_lane_reason": (
                    "P88 is ready with exact lane/command/path and authority locks false; P83 regeneration is authorization-eligible but not granted in P89."
                ),
                "eligibility_reasons": [
                    "P88_EXECUTION_PLAN_READY",
                    "P88_RECOMMENDS_P89_GATE",
                    "P88_COMMAND_EXACT_MATCH",
                    "P88_EXPECTED_OUTPUT_EXACT_MATCH",
                    "P88_AUTHORITY_LOCKS_FALSE",
                    "P83_REGENERATION_ELIGIBLE_BUT_NOT_GRANTED",
                ],
                "denial_reasons": ["AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P89"],
                "source_recommended_lane": source_recommended_lane,
                "source_command": source_command,
                "source_expected_output_path": source_expected_output_path,
                "authority_locks_false": authority_locks_false,
            }

        denial_reasons: list[str] = []
        if not lane_match:
            denial_reasons.append("P88_RECOMMENDED_LANE_MISMATCH")
        if not command_match:
            denial_reasons.append("P88_COMMAND_MISMATCH")
        if not output_match:
            denial_reasons.append("P88_EXPECTED_OUTPUT_PATH_MISMATCH")
        if not authority_locks_false:
            denial_reasons.append("P88_AUTHORITY_LOCK_VIOLATION")
        if not denial_reasons:
            denial_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")

        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P88 ready signal is inconsistent with lane/command/path/authority invariants; regenerate P88 before deriving P89 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": denial_reasons,
            "source_recommended_lane": source_recommended_lane,
            "source_command": source_command,
            "source_expected_output_path": source_expected_output_path,
            "authority_locks_false": authority_locks_false,
        }

    return {
        "status": "NOT_COMPUTABLE",
        "eligible": False,
        "recommended_next_lane": "P88_REGENERATION_EXECUTION_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P88 execution plan status is missing or unsupported; regenerate P88 before deriving P89 authorization gating."
        ),
        "eligibility_reasons": [],
        "denial_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
        "source_recommended_lane": source_recommended_lane,
        "source_command": source_command,
        "source_expected_output_path": source_expected_output_path,
        "authority_locks_false": _all_p88_authority_fields_false(payload_dict),
    }


def build_temporal_continuity_p83_regeneration_authorization_gate(
    *,
    repo_root: str | Path = ".",
    source_p88_execution_plan_path: str = SOURCE_P88_EXECUTION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p88 = _observe_source(
        root=root,
        rel_path=source_p88_execution_plan_path,
        status_field="p83_regeneration_execution_plan_status",
    )
    p88_payload = p88.get("payload")
    inherited_payload: dict[str, Any] = p88_payload if isinstance(p88_payload, dict) else {}

    classification = _classify(p88)
    status = str(classification["status"])
    eligible = bool(classification["eligible"])
    source_recommended_lane = str(classification["source_recommended_lane"])
    source_command = str(classification["source_command"])
    source_expected_output_path = str(classification["source_expected_output_path"])
    authority_locks_false = bool(classification["authority_locks_false"])

    eligibility_reasons = _ordered_unique(
        [str(reason) for reason in classification["eligibility_reasons"]],
        _ELIGIBILITY_REASON_ORDER_INDEX,
    )
    denial_reasons = _ordered_unique(
        [str(reason) for reason in classification["denial_reasons"]],
        _DENIAL_REASON_ORDER_INDEX,
    )

    degraded_evidence_inputs = _as_str_list(
        inherited_payload.get("degraded_evidence_inputs")
    )
    inherited_blockers = _as_str_list(inherited_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(inherited_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(inherited_payload.get("semantic_overlap_flags"))

    prerequisite_checks = _prerequisite_checks(
        source_observed=bool(p88["observed"]),
        source_readable=bool(p88["readable"]),
        source_status=str(p88["status"]),
        source_recommended_lane=source_recommended_lane,
        source_command=source_command,
        source_expected_output_path=source_expected_output_path,
        authority_locks_false=authority_locks_false,
    )

    gate_items: list[dict[str, Any]] = [
        {
            "gate_item_id": "gate_item_001",
            "lane": "P83",
            "source_plan_path": source_p88_execution_plan_path,
            "future_command": source_command,
            "expected_output_path": source_expected_output_path,
            "authorization_eligible": eligible,
            "authorization_granted": False,
            "execution_allowed": False,
            "blocking_reason": (
                str(denial_reasons[0]) if denial_reasons else "AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P89"
            ),
        }
    ]
    gate_items = sorted(
        gate_items,
        key=lambda item: (
            str(item["gate_item_id"]),
            str(item["lane"]),
            str(item["source_plan_path"]),
        ),
    )

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
        "spine_implementation_authority": False,
        "source_p88_execution_plan_path": source_p88_execution_plan_path,
        "source_p88_execution_plan_observed": bool(p88["observed"]),
        "source_p88_execution_plan_readable": bool(p88["readable"]),
        "source_p88_execution_plan_hash": str(p88["file_hash"]),
        "source_p88_execution_plan_status": str(p88["status"]),
        "source_p88_recommended_next_lane": source_recommended_lane,
        "p83_regeneration_authorization_gate_status": (
            status if status in _GATE_STATUSES else "NOT_COMPUTABLE"
        ),
        "p83_regeneration_authorization_eligible": eligible,
        "p83_regeneration_authorization_granted": False,
        "p83_regeneration_execution_allowed": False,
        "eligibility_reasons": eligibility_reasons,
        "denial_reasons": denial_reasons,
        "prerequisite_checks": prerequisite_checks,
        "gate_items": gate_items,
        "eligible_future_command": (
            ALLOWED_FUTURE_RUNNER_COMMAND if eligible else "NOT_COMPUTABLE"
        ),
        "eligible_expected_output_path": EXPECTED_OUTPUT_PATH if eligible else "NOT_COMPUTABLE",
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "gate_strategy_summary": {
            "prerequisite_checks_count": len(prerequisite_checks),
            "gate_items_count": len(gate_items),
            "eligibility_reasons_count": len(eligibility_reasons),
            "denial_reasons_count": len(denial_reasons),
            "p83_regeneration_authorization_gate_status": (
                status if status in _GATE_STATUSES else "NOT_COMPUTABLE"
            ),
            "p83_regeneration_authorization_eligible": eligible,
            "authorization_granted": False,
            "execution_authority": False,
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


def write_temporal_continuity_p83_regeneration_authorization_gate(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
