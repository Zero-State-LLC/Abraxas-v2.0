from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceRecordCreationPlan.v1"
SOURCE_P96_SEQUENCE_RECORD_PLAN_PATH = "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan/latest.json"
EXPECTED_P96_RECOMMENDED_NEXT_LANE = "P97_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_PLAN"

_P96_REGENERATION_LANE = "P96_SEQUENCE_RECORD_PLAN_REGENERATION"
_NOT_REQUIRED_NEXT_LANE = (
    "P98_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
)
_READY_NEXT_LANE = "P98_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE"

_ALLOWED_SEQUENCE_RECORD_CREATION_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_SEQUENCE_RECORD_CREATION_PLAN_READY",
    "P83_SEQUENCE_RECORD_CREATION_PLAN_DENIED",
    "P83_SEQUENCE_RECORD_CREATION_NOT_REQUIRED",
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


def _classify(p96: dict[str, Any]) -> dict[str, Any]:
    payload = p96.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}
    planned_sequence_record = payload_dict.get("planned_sequence_record")
    planned_sequence_record_dict = (
        planned_sequence_record if isinstance(planned_sequence_record, dict) else {}
    )

    source_status = str(p96["status"])
    source_recommended_lane = str(
        payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE")
    )

    eligible_future_command = str(
        payload_dict.get("eligible_future_command", "NOT_COMPUTABLE")
    )
    eligible_expected_output_path = str(
        payload_dict.get("eligible_expected_output_path", "NOT_COMPUTABLE")
    )

    if not p96["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P96_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P96 sequence record plan source is missing; regenerate P96 before deriving P97 sequence record creation planning."
            ),
            "blocking_reason": "P96_SOURCE_MISSING",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if not p96["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P96_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P96 sequence record plan source is unreadable; regenerate P96 before deriving P97 sequence record creation planning."
            ),
            "blocking_reason": "P96_SOURCE_UNREADABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if p96["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P96_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P96 sequence record plan source is malformed JSON; regenerate P96 before deriving P97 sequence record creation planning."
            ),
            "blocking_reason": "P96_SOURCE_MALFORMED_JSON",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status in {"NOT_COMPUTABLE", "P83_SEQUENCE_RECORD_PLAN_DENIED"}:
        return {
            "status": "P83_SEQUENCE_RECORD_CREATION_PLAN_DENIED",
            "required": False,
            "recommended_next_lane": _P96_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P96 sequence record plan is denied or NOT_COMPUTABLE; P97 sequence record creation planning is denied until P96 is regenerated."
            ),
            "blocking_reason": "P96_SEQUENCE_RECORD_PLAN_DENIED_OR_NOT_COMPUTABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_SEQUENCE_RECORD_NOT_REQUIRED":
        return {
            "status": "P83_SEQUENCE_RECORD_CREATION_NOT_REQUIRED",
            "required": False,
            "recommended_next_lane": _NOT_REQUIRED_NEXT_LANE,
            "recommended_next_lane_reason": (
                "P96 sequence record plan is not required; P97 sequence record creation planning is not required."
            ),
            "blocking_reason": "P96_SEQUENCE_RECORD_PLAN_NOT_REQUIRED",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_SEQUENCE_RECORD_PLAN_READY":
        conditions = (
            payload_dict.get("p83_sequence_record_required") is True,
            payload_dict.get("p83_sequence_record_allowed") is False,
            payload_dict.get("authorization_record_created") is False,
            payload_dict.get("authorization_granted") is False,
            payload_dict.get("authorization_token_created") is False,
            planned_sequence_record_dict.get("sequence_record_allowed") is False,
            planned_sequence_record_dict.get("record_created") is False,
            planned_sequence_record_dict.get("authorization_granted") is False,
            planned_sequence_record_dict.get("authorization_token_created") is False,
            planned_sequence_record_dict.get("execution_allowed") is False,
            source_recommended_lane == EXPECTED_P96_RECOMMENDED_NEXT_LANE,
        )
        if all(conditions):
            return {
                "status": "P83_SEQUENCE_RECORD_CREATION_PLAN_READY",
                "required": True,
                "recommended_next_lane": _READY_NEXT_LANE,
                "recommended_next_lane_reason": (
                    "P96 sequence record plan is ready with required lock invariants false; emit advisory-only P97 sequence record creation planning without creating authorization records."
                ),
                "blocking_reason": "SEQUENCE_RECORD_CREATION_RESERVED_FOR_FUTURE_AUTHORIZATION_GATE",
                "eligible_future_command": eligible_future_command,
                "eligible_expected_output_path": eligible_expected_output_path,
            }

        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P96_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P96 ready signal is weak or inconsistent with sequence record lock/lane invariants; regenerate P96 before deriving P97."
            ),
            "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "recommended_next_lane": _P96_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P96 sequence record plan status is missing or unsupported; regenerate P96 before deriving P97 sequence record creation planning."
        ),
        "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
    }


def _sequence_record_creation_steps(
    *, source_sequence_record_plan_path: str
) -> list[dict[str, Any]]:
    steps = [
        {
            "step_id": "step_001_plan_authorization_record_creation_sequence_record",
            "lane": "P97_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_PLAN",
            "source_sequence_record_plan_path": source_sequence_record_plan_path,
            "planned_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "action_type": "ADVISORY_SEQUENCE_RECORD_CREATION_PLANNING",
            "action_description": "Define governed sequence-record creation steps without creating any authorization record or granting authority.",
            "creation_allowed": False,
            "record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_allowed": False,
            "blocking_reason": "AUTHORIZATION_RECORD_CREATION_RESERVED_FOR_FUTURE_GATE",
        }
    ]
    return sorted(steps, key=lambda item: str(item["step_id"]))


def _pre_creation_checks(
    *,
    source_sequence_record_plan_path: str,
    source_status: str,
    source_recommended_next_lane: str,
) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "precheck_001_source_observed_readable",
            "check_type": "source_exists_readable",
            "path": source_sequence_record_plan_path,
            "required_status": "observed=true;readable=true",
            "satisfied": source_status != "NOT_COMPUTABLE",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "precheck_002_source_status_ready",
            "check_type": "status_exact_match",
            "path": source_sequence_record_plan_path,
            "required_status": "p83_sequence_record_plan_status=P83_SEQUENCE_RECORD_PLAN_READY",
            "satisfied": source_status == "P83_SEQUENCE_RECORD_PLAN_READY",
            "failure_action": "MARK_SEQUENCE_RECORD_CREATION_PLAN_DENIED_OR_NOT_COMPUTABLE",
        },
        {
            "check_id": "precheck_003_source_lane_match",
            "check_type": "recommended_lane_exact_match",
            "path": "recommended_next_lane",
            "required_status": EXPECTED_P96_RECOMMENDED_NEXT_LANE,
            "satisfied": source_recommended_next_lane
            == EXPECTED_P96_RECOMMENDED_NEXT_LANE,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
        {
            "check_id": "precheck_004_creation_governance_locks",
            "check_type": "governance_locks_false",
            "path": "planned_sequence_record.*",
            "required_status": "sequence_record_allowed=false;record_created=false;authorization_granted=false;authorization_token_created=false;execution_allowed=false",
            "satisfied": source_status == "P83_SEQUENCE_RECORD_PLAN_READY",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
    ]
    return sorted(checks, key=lambda item: str(item["check_id"]))


def _planned_record_output() -> dict[str, Any]:
    return {
        "path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
        "artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
        "overwrite_policy": "NO_WRITE_ADVISORY_PLAN_ONLY",
        "creation_allowed": False,
        "creation_authority": False,
        "record_created": False,
        "authorization_granted": False,
        "authorization_token_created": False,
        "execution_allowed": False,
    }


def _replay_validation_requirements(
    *, source_sequence_record_plan_path: str, source_sequence_record_plan_hash: str
) -> list[dict[str, Any]]:
    requirements = [
        {
            "validation_id": "replay_validation_001_source_sequence_record_plan_exists",
            "validation_type": "source_exists_readable",
            "path": source_sequence_record_plan_path,
            "required_status": "observed=true;readable=true",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_002_source_sequence_record_plan_hash_match",
            "validation_type": "source_hash_exact_match",
            "path": source_sequence_record_plan_path,
            "required_status": source_sequence_record_plan_hash,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_003_source_sequence_record_plan_status",
            "validation_type": "status_exact_match",
            "path": source_sequence_record_plan_path,
            "required_status": "p83_sequence_record_plan_status=P83_SEQUENCE_RECORD_PLAN_READY",
            "failure_action": "MARK_SEQUENCE_RECORD_CREATION_PLAN_DENIED_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
        {
            "validation_id": "replay_validation_004_source_sequence_record_plan_lane",
            "validation_type": "recommended_lane_exact_match",
            "path": "recommended_next_lane",
            "required_status": EXPECTED_P96_RECOMMENDED_NEXT_LANE,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P96_SEQUENCE_RECORD_PLAN_REGENERATION",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["validation_id"]))


def _expiration_policy() -> dict[str, Any]:
    return {
        "expiration_required": True,
        "expiration_basis": "inherits_from_future_sequence_record_creation_authorization_gate",
        "max_validity_scope": "sequence_record_creation_planning_only",
        "renewal_requires_new_gate": True,
    }


def _revocation_policy() -> dict[str, Any]:
    return {
        "revocation_supported": True,
        "revocation_triggers": [
            "source_sequence_record_plan_status_change",
            "source_sequence_record_plan_hash_mismatch",
            "operator_revocation",
            "governance_policy_change",
        ],
        "revocation_effect": "invalidate_sequence_record_creation_plan_and_require_new_gate",
        "revocation_requires_new_gate": True,
    }


def _rollback_policy() -> dict[str, Any]:
    return {
        "rollback_supported": True,
        "rollback_scope": "sequence_record_creation_plan_only",
        "rollback_trigger_conditions": [
            "source_sequence_record_plan_missing_or_unreadable",
            "source_sequence_record_plan_hash_mismatch",
            "source_sequence_record_plan_status_or_lane_mismatch",
            "sequence_record_creation_lock_violation",
        ],
        "rollback_resulting_status": "P83_SEQUENCE_RECORD_CREATION_PLAN_DENIED",
    }


def _denial_propagation_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "denial_id": "denial_rule_001_missing_or_unreadable_source",
            "source_condition": "source_p96_sequence_record_plan_observed=false OR source_p96_sequence_record_plan_readable=false",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _P96_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_002_source_denied_or_not_computable",
            "source_condition": "source_p96_sequence_record_plan_status in {NOT_COMPUTABLE,P83_SEQUENCE_RECORD_PLAN_DENIED}",
            "propagated_status": "P83_SEQUENCE_RECORD_CREATION_PLAN_DENIED",
            "recommended_lane": _P96_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_003_weak_or_inconsistent_signal",
            "source_condition": "ready_signal_violates_required_locks_or_lane",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _P96_REGENERATION_LANE,
        },
    ]
    return sorted(rules, key=lambda item: str(item["denial_id"]))


def _downstream_routing_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "route_id": "route_001_missing_unreadable_or_malformed",
            "source_condition": "source_p96_sequence_record_plan_missing_or_unreadable_or_malformed",
            "next_lane": _P96_REGENERATION_LANE,
            "routing_reason": "Source sequence record plan unavailable; fail closed and regenerate P96.",
        },
        {
            "route_id": "route_002_source_denied_or_not_computable",
            "source_condition": "source_p96_sequence_record_plan_status in {NOT_COMPUTABLE,P83_SEQUENCE_RECORD_PLAN_DENIED}",
            "next_lane": _P96_REGENERATION_LANE,
            "routing_reason": "Source sequence record plan denied/not computable; re-run P96 before P97 progression.",
        },
        {
            "route_id": "route_003_source_not_required",
            "source_condition": "source_p96_sequence_record_plan_status=P83_SEQUENCE_RECORD_NOT_REQUIRED",
            "next_lane": _NOT_REQUIRED_NEXT_LANE,
            "routing_reason": "Sequence record plan is not required; continue continuity chain to P84 regeneration-plan branch.",
        },
        {
            "route_id": "route_004_source_ready_locks_false",
            "source_condition": "source_p96_sequence_record_plan_status=P83_SEQUENCE_RECORD_PLAN_READY with lock invariants false",
            "next_lane": _READY_NEXT_LANE,
            "routing_reason": "Ready source signal verified; proceed to advisory-only sequence record creation authorization gate planning handoff.",
        },
    ]
    return sorted(rules, key=lambda item: str(item["route_id"]))


def build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_plan(
    *,
    repo_root: str | Path = ".",
    source_p96_sequence_record_plan_path: str = SOURCE_P96_SEQUENCE_RECORD_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p96 = _observe_source(
        root=root,
        rel_path=source_p96_sequence_record_plan_path,
        status_field="p83_sequence_record_plan_status",
    )

    payload = p96.get("payload")
    inherited_payload: dict[str, Any] = payload if isinstance(payload, dict) else {}

    classification = _classify(p96)
    plan_status = str(classification["status"])
    required = bool(classification["required"])
    eligible_future_command = str(classification["eligible_future_command"])
    eligible_expected_output_path = str(classification["eligible_expected_output_path"])

    sequence_record_creation_steps = _sequence_record_creation_steps(
        source_sequence_record_plan_path=source_p96_sequence_record_plan_path
    )
    pre_creation_checks = _pre_creation_checks(
        source_sequence_record_plan_path=source_p96_sequence_record_plan_path,
        source_status=str(p96["status"]),
        source_recommended_next_lane=str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
    )
    planned_record_output = _planned_record_output()
    replay_validation_requirements = _replay_validation_requirements(
        source_sequence_record_plan_path=source_p96_sequence_record_plan_path,
        source_sequence_record_plan_hash=str(p96["file_hash"]),
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
    inherited_drift_flags = _preserve_list(
        inherited_payload.get("inherited_drift_flags")
    )
    semantic_overlap_flags = _preserve_list(
        inherited_payload.get("semantic_overlap_flags")
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_record_creation_sequence_record_creation_plan_only": True,
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
        "source_p96_sequence_record_plan_path": source_p96_sequence_record_plan_path,
        "source_p96_sequence_record_plan_observed": bool(p96["observed"]),
        "source_p96_sequence_record_plan_readable": bool(p96["readable"]),
        "source_p96_sequence_record_plan_hash": str(p96["file_hash"]),
        "source_p96_sequence_record_plan_status": str(p96["status"]),
        "source_p96_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p83_sequence_record_creation_plan_status": (
            plan_status
            if plan_status in _ALLOWED_SEQUENCE_RECORD_CREATION_PLAN_STATUSES
            else "NOT_COMPUTABLE"
        ),
        "p83_sequence_record_creation_required": required,
        "p83_sequence_record_creation_allowed": False,
        "sequence_record_creation_steps": sequence_record_creation_steps,
        "pre_creation_checks": pre_creation_checks,
        "planned_record_output": planned_record_output,
        "replay_validation_requirements": replay_validation_requirements,
        "expiration_policy": expiration_policy,
        "revocation_policy": revocation_policy,
        "rollback_policy": rollback_policy,
        "denial_propagation_rules": denial_propagation_rules,
        "downstream_routing_rules": downstream_routing_rules,
        "eligible_future_command": eligible_future_command,
        "eligible_expected_output_path": eligible_expected_output_path,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "sequence_record_creation_strategy_summary": {
            "sequence_record_creation_steps_count": len(sequence_record_creation_steps),
            "pre_creation_checks_count": len(pre_creation_checks),
            "replay_validation_requirements_count": len(replay_validation_requirements),
            "denial_propagation_rules_count": len(denial_propagation_rules),
            "downstream_routing_rules_count": len(downstream_routing_rules),
            "p83_sequence_record_creation_plan_status": (
                plan_status
                if plan_status in _ALLOWED_SEQUENCE_RECORD_CREATION_PLAN_STATUSES
                else "NOT_COMPUTABLE"
            ),
            "p83_sequence_record_creation_required": required,
            "p83_sequence_record_creation_allowed": False,
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


def write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
