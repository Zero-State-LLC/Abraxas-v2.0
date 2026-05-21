from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP83RegenerationAuthorizationRecordCreationPlan.v1"
SOURCE_P90_RECORD_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json"
)
EXPECTED_P90_RECOMMENDED_NEXT_LANE = (
    "P91_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN"
)

_RECORD_PLAN_REGENERATION_LANE = "P90_AUTHORIZATION_RECORD_PLAN_REGENERATION"
_NOT_REQUIRED_NEXT_LANE = (
    "P92_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
)
_READY_NEXT_LANE = (
    "P92_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
)

_ALLOWED_CREATION_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY",
    "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
    "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_NOT_REQUIRED",
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


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


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


def _classify(p90: dict[str, Any]) -> dict[str, Any]:
    payload = p90.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}

    source_status = str(p90["status"])
    source_recommended_lane = str(
        payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE")
    )

    if not p90["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _RECORD_PLAN_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P90 authorization record plan source is missing; regenerate P90 before deriving P91 creation planning."
            ),
            "blocking_reason": "P90_SOURCE_MISSING",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if not p90["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _RECORD_PLAN_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P90 authorization record plan source is unreadable; regenerate P90 before deriving P91 creation planning."
            ),
            "blocking_reason": "P90_SOURCE_UNREADABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if p90["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _RECORD_PLAN_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P90 authorization record plan source is malformed JSON; regenerate P90 before deriving P91 creation planning."
            ),
            "blocking_reason": "P90_SOURCE_MALFORMED_JSON",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status in {
        "NOT_COMPUTABLE",
        "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_DENIED",
    }:
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
            "required": False,
            "recommended_next_lane": _RECORD_PLAN_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P90 authorization record plan is denied or NOT_COMPUTABLE; P91 creation planning is denied until P90 is regenerated."
            ),
            "blocking_reason": "P90_RECORD_PLAN_DENIED_OR_NOT_COMPUTABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_REGENERATION_AUTHORIZATION_RECORD_NOT_REQUIRED":
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_NOT_REQUIRED",
            "required": False,
            "recommended_next_lane": _NOT_REQUIRED_NEXT_LANE,
            "recommended_next_lane_reason": (
                "P90 authorization record plan is not required; P91 creation planning is also not required."
            ),
            "blocking_reason": "P90_RECORD_NOT_REQUIRED",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY":
        conditions = (
            payload_dict.get("p83_regeneration_record_required") is True,
            payload_dict.get("p83_regeneration_record_creation_allowed") is False,
            payload_dict.get("authorization_record_created") is False,
            payload_dict.get("authorization_granted") is False,
            payload_dict.get("authorization_token_created") is False,
            source_recommended_lane == EXPECTED_P90_RECOMMENDED_NEXT_LANE,
        )
        if all(conditions):
            return {
                "status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY",
                "required": True,
                "recommended_next_lane": _READY_NEXT_LANE,
                "recommended_next_lane_reason": (
                    "P90 record plan is ready with creation/grant/token locks false; emit advisory-only P91 authorization record creation planning."
                ),
                "blocking_reason": "AUTHORIZATION_RECORD_CREATION_RESERVED_FOR_FUTURE_AUTHORIZED_GATE",
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
            "recommended_next_lane": _RECORD_PLAN_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P90 record plan signal is weak or inconsistent with creation/grant/token/lane invariants; regenerate P90 before deriving P91."
            ),
            "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "recommended_next_lane": _RECORD_PLAN_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P90 authorization record plan status is missing or unsupported; regenerate P90 before deriving P91 creation planning."
        ),
        "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
    }


def _creation_plan_items(
    *,
    source_record_plan_path: str,
    eligible_future_command: str,
    eligible_expected_output_path: str,
    blocking_reason: str,
) -> list[dict[str, Any]]:
    items = [
        {
            "creation_plan_item_id": "creation_plan_item_001",
            "lane": "P83",
            "source_record_plan_path": source_record_plan_path,
            "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "planned_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "eligible_future_command": eligible_future_command,
            "eligible_expected_output_path": eligible_expected_output_path,
            "authorization_record_creation_allowed": False,
            "authorization_record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_allowed": False,
            "blocking_reason": blocking_reason,
        }
    ]
    return sorted(
        items,
        key=lambda item: (
            str(item["creation_plan_item_id"]),
            str(item["lane"]),
            str(item["source_record_plan_path"]),
        ),
    )


def _pre_creation_checks(
    *,
    source_record_plan_path: str,
    source_record_plan_hash: str,
) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "pre_creation_check_001_source_record_plan_exists",
            "check_type": "source_exists",
            "path": source_record_plan_path,
            "required_status": "observed=true;readable=true",
            "satisfied": source_record_plan_hash != "NOT_COMPUTABLE",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "pre_creation_check_002_source_record_plan_hash_match",
            "check_type": "source_hash_exact_match",
            "path": source_record_plan_path,
            "required_status": source_record_plan_hash,
            "satisfied": source_record_plan_hash != "NOT_COMPUTABLE",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "pre_creation_check_003_source_record_plan_status",
            "check_type": "status_exact_match",
            "path": source_record_plan_path,
            "required_status": "p83_regeneration_record_plan_status=P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY",
            "satisfied": False,
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "pre_creation_check_004_authority_locks",
            "check_type": "authority_lock_check",
            "path": source_record_plan_path,
            "required_status": "authorization_record_created=false;authorization_granted=false;authorization_token_created=false;p83_regeneration_record_creation_allowed=false",
            "satisfied": False,
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "pre_creation_check_005_recommended_lane_exact_match",
            "check_type": "recommended_lane_exact_match",
            "path": source_record_plan_path,
            "required_status": f"recommended_next_lane={EXPECTED_P90_RECOMMENDED_NEXT_LANE}",
            "satisfied": False,
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
    ]
    return sorted(checks, key=lambda item: str(item["check_id"]))


def _planned_record_output() -> dict[str, Any]:
    return {
        "path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
        "overwrite_policy": "DENY_UNLESS_AUTHORIZED_BY_FUTURE_GATE",
        "creation_allowed": False,
        "creation_authority": False,
    }


def _rollback_policy() -> dict[str, Any]:
    return {
        "rollback_supported": True,
        "rollback_scope": "creation_plan_only",
        "rollback_trigger_conditions": [
            "source_record_plan_hash_mismatch",
            "source_record_plan_status_change",
            "operator_revocation",
            "drift_or_evidence_degradation_detected",
        ],
        "rollback_resulting_status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
    }


def _fail_closed_policy() -> dict[str, Any]:
    return {
        "fail_closed_required": True,
        "fail_closed_conditions": [
            "source_record_plan_missing_or_unreadable",
            "source_record_plan_hash_mismatch",
            "authority_lock_violation",
            "pre_creation_check_failure",
        ],
        "fail_closed_resulting_status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
        "downstream_progression_allowed": False,
    }


def _replay_validation_requirements(
    *,
    source_record_plan_path: str,
    source_record_plan_hash: str,
) -> list[dict[str, Any]]:
    requirements = [
        {
            "validation_id": "replay_validation_001_source_record_plan_exists",
            "validation_type": "source_exists",
            "path": source_record_plan_path,
            "required_status": "observed=true;readable=true",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_002_source_record_plan_hash_match",
            "validation_type": "source_hash_exact_match",
            "path": source_record_plan_path,
            "required_status": source_record_plan_hash,
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_003_source_record_plan_status",
            "validation_type": "status_exact_match",
            "path": source_record_plan_path,
            "required_status": "p83_regeneration_record_plan_status=P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_004_authority_locks",
            "validation_type": "authority_lock_check",
            "path": source_record_plan_path,
            "required_status": "authorization_record_created=false;authorization_granted=false;authorization_token_created=false;p83_regeneration_record_creation_allowed=false",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P90_RECORD_PLAN_REGENERATION",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["validation_id"]))


def _creation_denial_propagation_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "denial_id": "denial_rule_001_missing_or_unreadable_source",
            "source_condition": "source_p90_record_plan_observed=false OR source_p90_record_plan_readable=false",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _RECORD_PLAN_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_002_p90_denied_or_not_computable",
            "source_condition": "source_p90_record_plan_status in {NOT_COMPUTABLE,P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_DENIED}",
            "propagated_status": "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED",
            "recommended_lane": _RECORD_PLAN_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_003_invariant_violation",
            "source_condition": "eligible_invariants_violate_creation_grant_token_execution_or_lane",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _RECORD_PLAN_REGENERATION_LANE,
        },
    ]
    return sorted(rules, key=lambda item: str(item["denial_id"]))


def build_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
    *,
    repo_root: str | Path = ".",
    source_p90_record_plan_path: str = SOURCE_P90_RECORD_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p90 = _observe_source(
        root=root,
        rel_path=source_p90_record_plan_path,
        status_field="p83_regeneration_record_plan_status",
    )

    payload = p90.get("payload")
    inherited_payload: dict[str, Any] = payload if isinstance(payload, dict) else {}

    classification = _classify(p90)
    plan_status = str(classification["status"])
    required = bool(classification["required"])
    eligible_future_command = str(classification["eligible_future_command"])
    eligible_expected_output_path = str(classification["eligible_expected_output_path"])
    blocking_reason = str(classification["blocking_reason"])

    creation_plan_items = _creation_plan_items(
        source_record_plan_path=source_p90_record_plan_path,
        eligible_future_command=eligible_future_command,
        eligible_expected_output_path=eligible_expected_output_path,
        blocking_reason=blocking_reason,
    )

    pre_creation_checks = _pre_creation_checks(
        source_record_plan_path=source_p90_record_plan_path,
        source_record_plan_hash=str(p90["file_hash"]),
    )

    planned_record_output = _planned_record_output()
    rollback_policy = _rollback_policy()
    fail_closed_policy = _fail_closed_policy()

    replay_validation_requirements = _replay_validation_requirements(
        source_record_plan_path=source_p90_record_plan_path,
        source_record_plan_hash=str(p90["file_hash"]),
    )
    creation_denial_propagation_rules = _creation_denial_propagation_rules()

    degraded_evidence_inputs = _as_str_list(
        inherited_payload.get("degraded_evidence_inputs")
    )
    inherited_blockers = _as_str_list(inherited_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(inherited_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(inherited_payload.get("semantic_overlap_flags"))

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_creation_plan_only": True,
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
        "source_p90_record_plan_path": source_p90_record_plan_path,
        "source_p90_record_plan_observed": bool(p90["observed"]),
        "source_p90_record_plan_readable": bool(p90["readable"]),
        "source_p90_record_plan_hash": str(p90["file_hash"]),
        "source_p90_record_plan_status": str(p90["status"]),
        "source_p90_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p83_regeneration_record_creation_plan_status": (
            plan_status
            if plan_status in _ALLOWED_CREATION_PLAN_STATUSES
            else "NOT_COMPUTABLE"
        ),
        "p83_regeneration_record_creation_required": required,
        "p83_regeneration_record_creation_allowed": False,
        "creation_plan_items": creation_plan_items,
        "pre_creation_checks": pre_creation_checks,
        "planned_record_output": planned_record_output,
        "rollback_policy": rollback_policy,
        "fail_closed_policy": fail_closed_policy,
        "replay_validation_requirements": replay_validation_requirements,
        "creation_denial_propagation_rules": creation_denial_propagation_rules,
        "eligible_future_command": eligible_future_command,
        "eligible_expected_output_path": eligible_expected_output_path,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "creation_strategy_summary": {
            "creation_plan_items_count": len(creation_plan_items),
            "pre_creation_checks_count": len(pre_creation_checks),
            "replay_validation_requirements_count": len(replay_validation_requirements),
            "creation_denial_propagation_rules_count": len(
                creation_denial_propagation_rules
            ),
            "p83_regeneration_record_creation_plan_status": (
                plan_status
                if plan_status in _ALLOWED_CREATION_PLAN_STATUSES
                else "NOT_COMPUTABLE"
            ),
            "p83_regeneration_record_creation_required": required,
            "p83_regeneration_record_creation_allowed": False,
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


def write_temporal_continuity_p83_regeneration_authorization_record_creation_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
