from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "TemporalContinuityP83RegenerationAuthorizationRecordCreationSequenceRecordCreationRecordPlan.v1"
)
SOURCE_P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate/latest.json"
)
EXPECTED_P98_RECOMMENDED_NEXT_LANE = (
    "P99_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_PLAN"
)

_P98_REGENERATION_LANE = "P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"
_NOT_REQUIRED_NEXT_LANE = "P102_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
_READY_NEXT_LANE = (
    "P100_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN"
)

_ALLOWED_RECORD_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
    "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED",
    "P83_SEQUENCE_RECORD_CREATION_RECORD_NOT_REQUIRED",
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



def _classify(p98: dict[str, Any]) -> dict[str, Any]:
    payload = p98.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}

    source_status = str(p98["status"])
    source_recommended_lane = str(
        payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE")
    )
    eligible_future_command = str(
        payload_dict.get("eligible_future_command", "NOT_COMPUTABLE")
    )
    eligible_expected_output_path = str(
        payload_dict.get("eligible_expected_output_path", "NOT_COMPUTABLE")
    )

    if not p98["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P98_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P98 authorization gate source is missing; regenerate P98 before deriving P99 sequence record creation record planning."
            ),
            "blocking_reason": "P98_SOURCE_MISSING",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if not p98["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P98_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P98 authorization gate source is unreadable; regenerate P98 before deriving P99 sequence record creation record planning."
            ),
            "blocking_reason": "P98_SOURCE_UNREADABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if p98["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P98_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P98 authorization gate source is malformed JSON; regenerate P98 before deriving P99 sequence record creation record planning."
            ),
            "blocking_reason": "P98_SOURCE_MALFORMED_JSON",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status in {
        "NOT_COMPUTABLE",
        "P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_DENIED",
    }:
        return {
            "status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED",
            "required": False,
            "recommended_next_lane": _P98_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P98 authorization gate is denied or NOT_COMPUTABLE; P99 sequence record creation record planning is denied until P98 is regenerated."
            ),
            "blocking_reason": "P98_AUTHORIZATION_DENIED_OR_NOT_COMPUTABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED":
        return {
            "status": "P83_SEQUENCE_RECORD_CREATION_RECORD_NOT_REQUIRED",
            "required": False,
            "recommended_next_lane": _NOT_REQUIRED_NEXT_LANE,
            "recommended_next_lane_reason": (
                "P98 authorization gate is not required; P99 sequence record creation record planning is not required."
            ),
            "blocking_reason": "P98_AUTHORIZATION_NOT_REQUIRED",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_ELIGIBLE":
        conditions = (
            payload_dict.get("p83_sequence_record_creation_authorization_eligible") is True,
            payload_dict.get("p83_sequence_record_creation_authorization_granted") is False,
            payload_dict.get("p83_sequence_record_creation_allowed") is False,
            payload_dict.get("authorization_record_created") is False,
            payload_dict.get("authorization_granted") is False,
            payload_dict.get("authorization_token_created") is False,
            payload_dict.get("p83_record_created") is False,
            payload_dict.get("p83_regeneration_execution_allowed") is False,
            source_recommended_lane == EXPECTED_P98_RECOMMENDED_NEXT_LANE,
        )
        if all(conditions):
            return {
                "status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_READY",
                "required": True,
                "recommended_next_lane": _READY_NEXT_LANE,
                "recommended_next_lane_reason": (
                    "P98 authorization gate is eligible with required lock invariants false; emit advisory-only P99 sequence record creation record planning without creating records."
                ),
                "blocking_reason": "SEQUENCE_RECORD_CREATION_RECORD_RESERVED_FOR_FUTURE_AUTHORIZED_RECORD_CREATION_LANE",
                "eligible_future_command": eligible_future_command,
                "eligible_expected_output_path": eligible_expected_output_path,
            }

        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _P98_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P98 eligible signal is weak or inconsistent with record-creation lock/lane invariants; regenerate P98 before deriving P99."
            ),
            "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "recommended_next_lane": _P98_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P98 authorization gate status is missing or unsupported; regenerate P98 before deriving P99 sequence record creation record planning."
        ),
        "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
    }



def _planned_sequence_creation_record(
    *,
    source_sequence_record_creation_gate_path: str,
    source_sequence_record_creation_gate_hash: str,
    eligible_future_command: str,
    eligible_expected_output_path: str,
) -> dict[str, Any]:
    return {
        "planned_sequence_creation_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
        "planned_sequence_creation_record_output_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
        "source_sequence_record_creation_gate_path": source_sequence_record_creation_gate_path,
        "source_sequence_record_creation_gate_hash": source_sequence_record_creation_gate_hash,
        "authorized_future_command": eligible_future_command,
        "authorized_expected_output_path": eligible_expected_output_path,
        "record_creation_allowed": False,
        "record_created": False,
        "authorization_granted": False,
        "authorization_token_created": False,
        "execution_allowed": False,
    }



def _planned_sequence_creation_record_fields(planned_sequence_creation_record: dict[str, Any]) -> list[dict[str, Any]]:
    fields = [
        {
            "field": "planned_sequence_creation_record_artifact_type",
            "required": True,
            "expected_value": planned_sequence_creation_record["planned_sequence_creation_record_artifact_type"],
            "source": "P99_SCHEMA_DEFAULT",
        },
        {
            "field": "planned_sequence_creation_record_output_path",
            "required": True,
            "expected_value": planned_sequence_creation_record["planned_sequence_creation_record_output_path"],
            "source": "P99_SCHEMA_DEFAULT",
        },
        {
            "field": "source_sequence_record_creation_gate_path",
            "required": True,
            "expected_value": planned_sequence_creation_record["source_sequence_record_creation_gate_path"],
            "source": "P98_INPUT",
        },
        {
            "field": "source_sequence_record_creation_gate_hash",
            "required": True,
            "expected_value": planned_sequence_creation_record["source_sequence_record_creation_gate_hash"],
            "source": "P98_INPUT",
        },
        {
            "field": "authorized_future_command",
            "required": True,
            "expected_value": planned_sequence_creation_record["authorized_future_command"],
            "source": "P98_INPUT",
        },
        {
            "field": "authorized_expected_output_path",
            "required": True,
            "expected_value": planned_sequence_creation_record["authorized_expected_output_path"],
            "source": "P98_INPUT",
        },
        {
            "field": "record_creation_allowed",
            "required": True,
            "expected_value": False,
            "source": "P99_GOVERNANCE_LOCK",
        },
        {
            "field": "record_created",
            "required": True,
            "expected_value": False,
            "source": "P99_GOVERNANCE_LOCK",
        },
        {
            "field": "authorization_granted",
            "required": True,
            "expected_value": False,
            "source": "P99_GOVERNANCE_LOCK",
        },
        {
            "field": "authorization_token_created",
            "required": True,
            "expected_value": False,
            "source": "P99_GOVERNANCE_LOCK",
        },
        {
            "field": "execution_allowed",
            "required": True,
            "expected_value": False,
            "source": "P99_GOVERNANCE_LOCK",
        },
    ]
    return sorted(fields, key=lambda item: str(item["field"]))



def _provenance_links(
    *, source_sequence_record_creation_gate_path: str, source_sequence_record_creation_gate_hash: str
) -> list[dict[str, Any]]:
    links = [
        {
            "link_id": "provenance_001_source_p98_creation_gate",
            "source_artifact_path": source_sequence_record_creation_gate_path,
            "source_artifact_hash": source_sequence_record_creation_gate_hash,
            "relation": "DERIVED_FROM",
            "required": True,
        },
        {
            "link_id": "provenance_002_planned_sequence_creation_record_output",
            "source_artifact_path": "out/temporal_continuity_p83_regeneration_authorization_record/latest.json",
            "source_artifact_hash": "NOT_COMPUTABLE",
            "relation": "PLANS_HYPOTHETICAL_RECORD_OUTPUT",
            "required": True,
        },
    ]
    return sorted(links, key=lambda item: str(item["link_id"]))



def _replay_validation_requirements(
    *, source_sequence_record_creation_gate_path: str, source_sequence_record_creation_gate_hash: str
) -> list[dict[str, Any]]:
    requirements = [
        {
            "validation_id": "replay_validation_001_source_creation_gate_exists",
            "validation_type": "source_exists_readable",
            "path": source_sequence_record_creation_gate_path,
            "required_status": "observed=true;readable=true",
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION",
        },
        {
            "validation_id": "replay_validation_002_source_sequence_record_creation_gate_hash_match",
            "validation_type": "source_hash_exact_match",
            "path": source_sequence_record_creation_gate_path,
            "required_status": source_sequence_record_creation_gate_hash,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION",
        },
        {
            "validation_id": "replay_validation_003_source_creation_gate_status",
            "validation_type": "status_exact_match",
            "path": source_sequence_record_creation_gate_path,
            "required_status": "p83_sequence_record_creation_authorization_gate_status=P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_ELIGIBLE",
            "failure_action": "MARK_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED_AND_ROUTE_TO_P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION",
        },
        {
            "validation_id": "replay_validation_004_source_creation_gate_lane",
            "validation_type": "recommended_lane_exact_match",
            "path": "recommended_next_lane",
            "required_status": EXPECTED_P98_RECOMMENDED_NEXT_LANE,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["validation_id"]))



def _expiration_policy() -> dict[str, Any]:
    return {
        "expiration_required": True,
        "expiration_basis": "inherits_future_authorization_record_policy",
        "max_validity_scope": "sequence_record_creation_record_planning_only",
        "renewal_requires_new_gate": True,
    }



def _revocation_policy() -> dict[str, Any]:
    return {
        "revocation_supported": True,
        "revocation_triggers": [
            "source_creation_gate_status_change",
            "source_sequence_record_creation_gate_hash_mismatch",
            "operator_revocation",
            "governance_policy_change",
        ],
        "revocation_effect": "invalidate_planned_sequence_record_creation_record_and_require_new_gate",
        "revocation_requires_new_gate": True,
    }



def _rollback_policy() -> dict[str, Any]:
    return {
        "rollback_supported": True,
        "rollback_scope": "sequence_record_creation_record_plan_only",
        "rollback_trigger_conditions": [
            "source_creation_gate_missing_or_unreadable",
            "source_sequence_record_creation_gate_hash_mismatch",
            "source_creation_gate_status_or_lane_mismatch",
            "record_creation_lock_violation",
        ],
        "rollback_resulting_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED",
    }



def _denial_propagation_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "denial_id": "denial_rule_001_missing_or_unreadable_source",
            "source_condition": "source_p98_sequence_record_creation_authorization_gate_observed=false OR source_p98_sequence_record_creation_authorization_gate_readable=false",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _P98_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_002_p98_not_computable_or_denied",
            "source_condition": "source_p98_sequence_record_creation_authorization_gate_status in {NOT_COMPUTABLE,P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_DENIED}",
            "propagated_status": "P83_SEQUENCE_RECORD_CREATION_RECORD_PLAN_DENIED",
            "recommended_lane": _P98_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_003_weak_or_inconsistent_signal",
            "source_condition": "eligible_signal_violates_required_locks_or_lane",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _P98_REGENERATION_LANE,
        },
    ]
    return sorted(rules, key=lambda item: str(item["denial_id"]))



def _downstream_routing_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "route_id": "route_001_missing_unreadable_or_malformed",
            "source_condition": "source_p98_sequence_record_creation_authorization_gate_missing_or_unreadable_or_malformed",
            "next_lane": _P98_REGENERATION_LANE,
            "routing_reason": "Source gate unavailable; fail closed and regenerate P98.",
        },
        {
            "route_id": "route_002_p98_denied_or_not_computable",
            "source_condition": "source_p98_sequence_record_creation_authorization_gate_status in {NOT_COMPUTABLE,P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_DENIED}",
            "next_lane": _P98_REGENERATION_LANE,
            "routing_reason": "Authorization gate denied/not computable; re-run P98 before any sequence record creation record planning progression.",
        },
        {
            "route_id": "route_003_p98_not_required",
            "source_condition": "source_p98_sequence_record_creation_authorization_gate_status=P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED",
            "next_lane": _NOT_REQUIRED_NEXT_LANE,
            "routing_reason": "Sequence record creation authorization is not required; continue continuity chain to the non-record-creation branch.",
        },
        {
            "route_id": "route_004_p98_eligible_locks_false",
            "source_condition": "source_p98_sequence_record_creation_authorization_gate_status=P83_SEQUENCE_RECORD_CREATION_AUTHORIZATION_ELIGIBLE with lock invariants false",
            "next_lane": _READY_NEXT_LANE,
            "routing_reason": "Eligible signal verified; proceed to advisory-only sequence record creation record creation planning.",
        },
    ]
    return sorted(rules, key=lambda item: str(item["route_id"]))



def build_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan(
    *,
    repo_root: str | Path = ".",
    source_p98_creation_gate_path: str = SOURCE_P98_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p98 = _observe_source(
        root=root,
        rel_path=source_p98_creation_gate_path,
        status_field="p83_sequence_record_creation_authorization_gate_status",
    )

    payload = p98.get("payload")
    inherited_payload: dict[str, Any] = payload if isinstance(payload, dict) else {}

    classification = _classify(p98)
    plan_status = str(classification["status"])
    required = bool(classification["required"])
    eligible_future_command = str(classification["eligible_future_command"])
    eligible_expected_output_path = str(classification["eligible_expected_output_path"])

    planned_sequence_creation_record = _planned_sequence_creation_record(
        source_sequence_record_creation_gate_path=source_p98_creation_gate_path,
        source_sequence_record_creation_gate_hash=str(p98["file_hash"]),
        eligible_future_command=eligible_future_command,
        eligible_expected_output_path=eligible_expected_output_path,
    )
    planned_sequence_creation_record_fields = _planned_sequence_creation_record_fields(planned_sequence_creation_record)
    provenance_links = _provenance_links(
        source_sequence_record_creation_gate_path=source_p98_creation_gate_path,
        source_sequence_record_creation_gate_hash=str(p98["file_hash"]),
    )
    replay_validation_requirements = _replay_validation_requirements(
        source_sequence_record_creation_gate_path=source_p98_creation_gate_path,
        source_sequence_record_creation_gate_hash=str(p98["file_hash"]),
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
        "authorization_record_creation_sequence_record_creation_record_plan_only": True,
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
        "source_p98_creation_gate_path": source_p98_creation_gate_path,
        "source_p98_creation_gate_observed": bool(p98["observed"]),
        "source_p98_creation_gate_readable": bool(p98["readable"]),
        "source_p98_creation_gate_hash": str(p98["file_hash"]),
        "source_p98_sequence_record_creation_authorization_gate_status": str(p98["status"]),
        "source_p98_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p83_sequence_record_creation_record_plan_status": (
            plan_status if plan_status in _ALLOWED_RECORD_PLAN_STATUSES else "NOT_COMPUTABLE"
        ),
        "p83_sequence_record_creation_record_required": required,
        "p83_sequence_record_creation_record_allowed": False,
        "record_created": False,
        "execution_allowed": False,
        "planned_sequence_creation_record": planned_sequence_creation_record,
        "planned_sequence_creation_record_fields": planned_sequence_creation_record_fields,
        "provenance_links": provenance_links,
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
        "record_plan_strategy_summary": {
            "planned_sequence_creation_record_fields_count": len(planned_sequence_creation_record_fields),
            "provenance_links_count": len(provenance_links),
            "replay_validation_requirements_count": len(replay_validation_requirements),
            "denial_propagation_rules_count": len(denial_propagation_rules),
            "downstream_routing_rules_count": len(downstream_routing_rules),
            "p83_sequence_record_creation_record_plan_status": (
                plan_status
                if plan_status in _ALLOWED_RECORD_PLAN_STATUSES
                else "NOT_COMPUTABLE"
            ),
            "p83_sequence_record_creation_record_required": required,
            "p83_sequence_record_creation_record_allowed": False,
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



def write_temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
