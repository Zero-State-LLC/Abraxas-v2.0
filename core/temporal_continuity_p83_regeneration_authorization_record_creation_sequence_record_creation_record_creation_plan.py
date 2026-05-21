from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceRecordCreationRecordCreationPlan.v1"
)
SOURCE_P99_RECORD_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json"
)
EXPECTED_P99_RECOMMENDED_NEXT_LANE = (
    "P100_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN"
)

_P99_REGENERATION_LANE = "P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION"
_NOT_REQUIRED_NEXT_LANE = "P102_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
_READY_NEXT_LANE = "P101_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE"

_ALLOWED_SEQUENCE_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
    "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_DENIED",
    "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_NOT_REQUIRED",
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


def _preserve_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


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


def _classify(p99: dict[str, Any]) -> dict[str, Any]:
    payload = p99.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}
    planned_sequence_creation_record = (
        payload_dict.get("planned_sequence_creation_record")
        if isinstance(payload_dict.get("planned_sequence_creation_record"), dict)
        else {}
    )

    source_status = str(p99["status"])
    source_recommended_lane = str(
        payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE")
    )

    if not p99["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P99_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P99 source record plan is missing; regenerate P99 before deriving P100 sequence record creation record creation planning."
            ),
            "blocking_reason": "P99_SOURCE_MISSING",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if not p99["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P99_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P99 source record plan is unreadable; regenerate P99 before deriving P100 sequence record creation record creation planning."
            ),
            "blocking_reason": "P99_SOURCE_UNREADABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if p99["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P99_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P99 source record plan is malformed JSON; regenerate P99 before deriving P100 sequence record creation record creation planning."
            ),
            "blocking_reason": "P99_SOURCE_MALFORMED_JSON",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status in {
        "NOT_COMPUTABLE",
        "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED",
    }:
        return {
            "status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_DENIED",
            "required": False,
            "recommended_next_lane": _P99_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P99 record plan is denied or NOT_COMPUTABLE; P100 record creation planning is denied until P99 is regenerated."
            ),
            "blocking_reason": "P99_PLAN_DENIED_OR_NOT_COMPUTABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_SEQUENCE_RECORD_CREATION_RECORD_NOT_REQUIRED":
        return {
            "status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_NOT_REQUIRED",
            "required": False,
            "recommended_next_lane": _NOT_REQUIRED_NEXT_LANE,
            "recommended_next_lane_reason": (
                "P99 says record creation record is not required; P100 record creation planning is not required."
            ),
            "blocking_reason": "P99_PLAN_NOT_REQUIRED",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY":
        conditions = (
            payload_dict.get("p83_sequence_record_creation_record_required") is True,
            payload_dict.get("p83_sequence_record_creation_record_allowed") is False,
            payload_dict.get("authorization_record_created") is False,
            payload_dict.get("authorization_granted") is False,
            payload_dict.get("authorization_token_created") is False,
            payload_dict.get("record_created") is False,
            payload_dict.get("execution_allowed") is False,
            planned_sequence_creation_record.get("record_creation_allowed") is False,
            planned_sequence_creation_record.get("record_created") is False,
            planned_sequence_creation_record.get("authorization_granted") is False,
            planned_sequence_creation_record.get("authorization_token_created") is False,
            planned_sequence_creation_record.get("execution_allowed") is False,
            source_recommended_lane == EXPECTED_P99_RECOMMENDED_NEXT_LANE,
        )
        if all(conditions):
            return {
                "status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_READY",
                "required": True,
                "recommended_next_lane": _READY_NEXT_LANE,
                "recommended_next_lane_reason": (
                    "P99 plan is ready with lock invariants false; emit advisory-only P100 record creation planning without creating an authorization record."
                ),
                "blocking_reason": "AUTHORIZATION_RECORD_CREATION_RESERVED_FOR_FUTURE_AUTHORIZED_RECORD_CREATION_GATE",
                "eligible_future_command": str(
                    payload_dict.get("eligible_future_command", "NOT_COMPUTABLE")
                ),
                "eligible_expected_output_path": str(
                    payload_dict.get("eligible_expected_output_path", "NOT_COMPUTABLE")
                ),
            }

        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P99_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P99 ready signal is weak or inconsistent with required lock/lane invariants; regenerate P99 before deriving P100."
            ),
            "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "recommended_next_lane": _P99_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P99 status is missing or unsupported; regenerate P99 before deriving P100 sequence record creation record creation planning."
        ),
        "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
    }


def _sequence_creation_record_creation_steps(
    *,
    source_record_plan_path: str,
    planned_record_output_path: str,
    planned_record_artifact_type: str,
    blocking_reason: str,
) -> list[dict[str, Any]]:
    steps = [
        {
            "step_id": "step_001_validate_p99_record_plan_locks",
            "lane": "P100_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN",
            "source_record_plan_path": source_record_plan_path,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "action_type": "VALIDATE_PRECONDITIONS",
            "action_description": "Validate that P99 status, lane, and all governance locks remain fail-closed before any hypothetical sequence record creation record creation is considered.",
            "creation_allowed": False,
            "record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_allowed": False,
            "blocking_reason": blocking_reason,
        },
        {
            "step_id": "step_002_plan_hypothetical_record_write",
            "lane": "P101_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE",
            "source_record_plan_path": source_record_plan_path,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "action_type": "PLAN_ONLY",
            "action_description": "Define the ordered advisory creation sequence for a future governed lane without creating any record or token in this lane.",
            "creation_allowed": False,
            "record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_allowed": False,
            "blocking_reason": blocking_reason,
        },
    ]
    return sorted(steps, key=lambda item: str(item["step_id"]))


def _pre_creation_checks(*, source_record_plan_path: str, source_record_plan_hash: str) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "precheck_001_source_record_plan_exists",
            "check_type": "source_exists_readable",
            "path": source_record_plan_path,
            "required_status": "observed=true;readable=true",
            "satisfied": source_record_plan_hash != "NOT_COMPUTABLE",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "precheck_002_source_record_plan_hash_bound",
            "check_type": "source_hash_bound",
            "path": source_record_plan_path,
            "required_status": source_record_plan_hash,
            "satisfied": source_record_plan_hash != "NOT_COMPUTABLE",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "precheck_003_source_record_plan_status_ready",
            "check_type": "status_exact_match",
            "path": source_record_plan_path,
            "required_status": "p83_sequence_record_creation_record_plan_status=P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
            "satisfied": False,
            "failure_action": "MARK_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_DENIED_AND_ROUTE_TO_P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION",
        },
    ]
    return sorted(checks, key=lambda item: str(item["check_id"]))


def _planned_record_output() -> dict[str, Any]:
    return {
        "path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
        "overwrite_policy": "WRITE_ON_AUTHORIZED_FUTURE_LANE_ONLY",
        "creation_allowed": False,
        "creation_authority": False,
        "record_created": False,
        "authorization_granted": False,
        "authorization_token_created": False,
        "execution_allowed": False,
    }


def _replay_validation_requirements(
    *, source_record_plan_path: str, source_record_plan_hash: str
) -> list[dict[str, Any]]:
    requirements = [
        {
            "validation_id": "replay_validation_001_source_record_plan_exists",
            "validation_type": "source_exists_readable",
            "path": source_record_plan_path,
            "required_status": "observed=true;readable=true",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_002_source_record_plan_hash_match",
            "validation_type": "source_hash_exact_match",
            "path": source_record_plan_path,
            "required_status": source_record_plan_hash,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_003_source_record_plan_lane",
            "validation_type": "recommended_lane_exact_match",
            "path": "recommended_next_lane",
            "required_status": EXPECTED_P99_RECOMMENDED_NEXT_LANE,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P99_SEQUENCE_RECORD_CREATION_RECORD_PLAN_REGENERATION",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["validation_id"]))


def _expiration_policy() -> dict[str, Any]:
    return {
        "expiration_required": True,
        "expiration_basis": "requires_fresh_record_creation_authorization_gate",
        "max_validity_scope": "sequence_record_creation_record_creation_plan_only",
        "renewal_requires_new_gate": True,
    }


def _revocation_policy() -> dict[str, Any]:
    return {
        "revocation_supported": True,
        "revocation_triggers": [
            "source_record_plan_status_change",
            "source_record_plan_hash_mismatch",
            "operator_revocation",
            "governance_policy_change",
        ],
        "revocation_effect": "invalidate_sequence_record_creation_record_creation_plan_and_require_new_gate",
        "revocation_requires_new_gate": True,
    }


def _rollback_policy() -> dict[str, Any]:
    return {
        "rollback_supported": True,
        "rollback_scope": "sequence_record_creation_record_creation_plan_only",
        "rollback_trigger_conditions": [
            "source_record_plan_missing_or_unreadable",
            "source_record_plan_hash_mismatch",
            "source_record_plan_status_or_lane_mismatch",
            "sequence_lock_violation",
        ],
        "rollback_resulting_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_DENIED",
    }


def _denial_propagation_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "denial_id": "denial_rule_001_missing_or_unreadable_source",
            "source_condition": "source_p99_record_plan_observed=false OR source_p99_record_plan_readable=false",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _P99_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_002_p99_denied_or_not_computable",
            "source_condition": "source_p99_record_plan_status in {NOT_COMPUTABLE,P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED}",
            "propagated_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN_DENIED",
            "recommended_lane": _P99_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_003_weak_or_inconsistent_signal",
            "source_condition": "eligible_signal_violates_required_locks_or_lane",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _P99_REGENERATION_LANE,
        },
    ]
    return sorted(rules, key=lambda item: str(item["denial_id"]))


def _downstream_routing_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "route_id": "route_001_missing_unreadable_or_malformed",
            "source_condition": "source_p99_record_plan_missing_or_unreadable_or_malformed",
            "next_lane": _P99_REGENERATION_LANE,
            "routing_reason": "Source record plan unavailable; fail closed and regenerate P99.",
        },
        {
            "route_id": "route_002_p99_denied_or_not_computable",
            "source_condition": "source_p99_record_plan_status in {NOT_COMPUTABLE,P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED}",
            "next_lane": _P99_REGENERATION_LANE,
            "routing_reason": "Record plan denied/not computable; re-run P99 before record creation planning progression.",
        },
        {
            "route_id": "route_003_p99_not_required",
            "source_condition": "source_p99_record_plan_status=P83_SEQUENCE_RECORD_CREATION_RECORD_NOT_REQUIRED",
            "next_lane": _NOT_REQUIRED_NEXT_LANE,
            "routing_reason": "Record creation is not required; continue continuity chain to P84 regeneration-plan branch.",
        },
        {
            "route_id": "route_004_p99_ready_locks_false",
            "source_condition": "source_p99_record_plan_status=P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY with lock invariants false",
            "next_lane": _READY_NEXT_LANE,
            "routing_reason": "Eligible record topology converted into advisory creation record creation planning for the next gate lane.",
        },
    ]
    return sorted(rules, key=lambda item: str(item["route_id"]))


def build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan(
    *,
    repo_root: str | Path = ".",
    source_p99_record_plan_path: str = SOURCE_P99_RECORD_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p99 = _observe_source(
        root=root,
        rel_path=source_p99_record_plan_path,
        status_field="p83_sequence_record_creation_record_plan_status",
    )

    payload = p99.get("payload")
    inherited_payload: dict[str, Any] = payload if isinstance(payload, dict) else {}

    classification = _classify(p99)
    plan_status = str(classification["status"])
    required = bool(classification["required"])
    source_record_plan_hash = str(p99["file_hash"])

    planned_record_output = _planned_record_output()
    sequence_creation_record_creation_steps = _sequence_creation_record_creation_steps(
        source_record_plan_path=source_p99_record_plan_path,
        planned_record_output_path=planned_record_output["path"],
        planned_record_artifact_type=planned_record_output["artifact_type"],
        blocking_reason=str(classification["blocking_reason"]),
    )
    pre_creation_checks = _pre_creation_checks(
        source_record_plan_path=source_p99_record_plan_path,
        source_record_plan_hash=source_record_plan_hash,
    )
    replay_validation_requirements = _replay_validation_requirements(
        source_record_plan_path=source_p99_record_plan_path,
        source_record_plan_hash=source_record_plan_hash,
    )

    expiration_policy = _expiration_policy()
    revocation_policy = _revocation_policy()
    rollback_policy = _rollback_policy()
    denial_propagation_rules = _denial_propagation_rules()
    downstream_routing_rules = _downstream_routing_rules()

    degraded_evidence_inputs = _preserve_list(
        inherited_payload.get("degraded_evidence_inputs")
    )
    inherited_blockers = _preserve_list(inherited_payload.get("inherited_blockers"))
    inherited_drift_flags = _preserve_list(inherited_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _preserve_list(inherited_payload.get("semantic_overlap_flags"))

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_creation_sequence_record_creation_record_creation_plan_only": True,
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
        "source_p99_record_plan_path": source_p99_record_plan_path,
        "source_p99_record_plan_observed": bool(p99["observed"]),
        "source_p99_record_plan_readable": bool(p99["readable"]),
        "source_p99_record_plan_hash": source_record_plan_hash,
        "source_p99_record_plan_status": str(p99["status"]),
        "source_p99_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p83_sequence_record_creation_record_creation_plan_status": (
            plan_status
            if plan_status in _ALLOWED_SEQUENCE_PLAN_STATUSES
            else "NOT_COMPUTABLE"
        ),
        "p83_sequence_record_creation_record_creation_required": required,
        "p83_sequence_record_creation_record_creation_allowed": False,
        "record_created": False,
        "execution_allowed": False,
        "sequence_creation_record_creation_steps": sequence_creation_record_creation_steps,
        "pre_creation_checks": pre_creation_checks,
        "planned_record_output": planned_record_output,
        "replay_validation_requirements": replay_validation_requirements,
        "expiration_policy": expiration_policy,
        "revocation_policy": revocation_policy,
        "rollback_policy": rollback_policy,
        "denial_propagation_rules": denial_propagation_rules,
        "downstream_routing_rules": downstream_routing_rules,
        "eligible_future_command": str(classification["eligible_future_command"]),
        "eligible_expected_output_path": str(
            classification["eligible_expected_output_path"]
        ),
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "record_creation_strategy_summary": {
            "sequence_creation_record_creation_steps_count": len(sequence_creation_record_creation_steps),
            "pre_creation_checks_count": len(pre_creation_checks),
            "replay_validation_requirements_count": len(replay_validation_requirements),
            "denial_propagation_rules_count": len(denial_propagation_rules),
            "downstream_routing_rules_count": len(downstream_routing_rules),
            "p83_sequence_record_creation_record_creation_plan_status": (
                plan_status
                if plan_status in _ALLOWED_SEQUENCE_PLAN_STATUSES
                else "NOT_COMPUTABLE"
            ),
            "p83_sequence_record_creation_record_creation_required": required,
            "p83_sequence_record_creation_record_creation_allowed": False,
        "record_created": False,
        "execution_allowed": False,
            "authorization_record_creation_authority": False,
            "authorization_record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_authority": False,
            "regeneration_execution_authority": False,
        },
        "recommended_next_lane": str(classification["recommended_next_lane"]),
        "recommended_next_lane_reason": str(
            classification["recommended_next_lane_reason"]
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    packet_no_hash = {k: v for k, v in packet_base.items() if k != "packet_hash"}
    packet = {**packet_no_hash, "packet_hash": canonical_hash(packet_no_hash)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
