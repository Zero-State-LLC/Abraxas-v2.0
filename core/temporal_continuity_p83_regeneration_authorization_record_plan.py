from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP83RegenerationAuthorizationRecordPlan.v1"
SOURCE_P89_GATE_PATH = "out/temporal_continuity_p83_regeneration_authorization_gate/latest.json"
EXPECTED_P89_RECOMMENDED_NEXT_LANE = (
    "P90_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_PLAN"
)

_GATE_REGENERATION_LANE = "P89_AUTHORIZATION_GATE_REGENERATION"
_NOT_REQUIRED_NEXT_LANE = (
    "P91_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
)
_READY_NEXT_LANE = (
    "P91_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN"
)

_ALLOWED_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY",
    "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_DENIED",
    "P83_REGENERATION_AUTHORIZATION_RECORD_NOT_REQUIRED",
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


def _classify(p89: dict[str, Any]) -> dict[str, Any]:
    payload = p89.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}

    source_status = str(p89["status"])
    source_recommended_lane = str(
        payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE")
    )

    if not p89["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _GATE_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P89 authorization gate source is missing; regenerate P89 before deriving P90 authorization record planning."
            ),
            "blocking_reason": "P89_SOURCE_MISSING",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if not p89["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _GATE_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P89 authorization gate source is unreadable; regenerate P89 before deriving P90 authorization record planning."
            ),
            "blocking_reason": "P89_SOURCE_UNREADABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if p89["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "recommended_next_lane": _GATE_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P89 authorization gate source is malformed JSON; regenerate P89 before deriving P90 authorization record planning."
            ),
            "blocking_reason": "P89_SOURCE_MALFORMED_JSON",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status in {
        "NOT_COMPUTABLE",
        "P83_REGENERATION_AUTHORIZATION_DENIED",
    }:
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_DENIED",
            "required": False,
            "recommended_next_lane": _GATE_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P89 authorization gate is denied or NOT_COMPUTABLE; P90 authorization record planning is denied until P89 is regenerated."
            ),
            "blocking_reason": "P89_AUTHORIZATION_DENIED_OR_NOT_COMPUTABLE",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_REGENERATION_AUTHORIZATION_NOT_REQUIRED":
        return {
            "status": "P83_REGENERATION_AUTHORIZATION_RECORD_NOT_REQUIRED",
            "required": False,
            "recommended_next_lane": _NOT_REQUIRED_NEXT_LANE,
            "recommended_next_lane_reason": (
                "P89 authorization is not required; P90 authorization record planning is also not required."
            ),
            "blocking_reason": "P89_AUTHORIZATION_NOT_REQUIRED",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    if source_status == "P83_REGENERATION_AUTHORIZATION_ELIGIBLE":
        conditions = (
            payload_dict.get("p83_regeneration_authorization_eligible") is True,
            payload_dict.get("p83_regeneration_authorization_granted") is False,
            payload_dict.get("authorization_granted") is False,
            payload_dict.get("authorization_token_created") is False,
            payload_dict.get("p83_regeneration_execution_allowed") is False,
            source_recommended_lane == EXPECTED_P89_RECOMMENDED_NEXT_LANE,
        )
        if all(conditions):
            return {
                "status": "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY",
                "required": True,
                "recommended_next_lane": _READY_NEXT_LANE,
                "recommended_next_lane_reason": (
                    "P89 is authorization-eligible with grant/token/execution locks false; emit advisory-only P90 authorization record planning."
                ),
                "blocking_reason": "AUTHORIZATION_RECORD_CREATION_RESERVED_FOR_P91",
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
            "recommended_next_lane": _GATE_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P89 eligible signal is weak or inconsistent with grant/token/execution/lane invariants; regenerate P89 before deriving P90."
            ),
            "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
            "eligible_future_command": "NOT_COMPUTABLE",
            "eligible_expected_output_path": "NOT_COMPUTABLE",
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "recommended_next_lane": _GATE_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P89 authorization gate status is missing or unsupported; regenerate P89 before deriving P90 authorization record planning."
        ),
        "blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
    }


def _required_record_fields(
    *,
    source_gate_path: str,
    source_gate_hash: str,
    future_command: str,
    expected_output_path: str,
) -> list[dict[str, Any]]:
    fields = [
        {
            "field": "artifact_type",
            "required": True,
            "expected_value": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "source": "P90_REQUIRED_RECORD_SCHEMA",
        },
        {
            "field": "source_p90_record_plan_hash",
            "required": True,
            "expected_value": "MUST_EQUAL_P90_PACKET_HASH",
            "source": "packet_hash",
        },
        {
            "field": "source_p89_gate_path",
            "required": True,
            "expected_value": source_gate_path,
            "source": "source_p89_gate_path",
        },
        {
            "field": "source_p89_gate_hash",
            "required": True,
            "expected_value": source_gate_hash,
            "source": "source_p89_gate_hash",
        },
        {
            "field": "authorized_command",
            "required": True,
            "expected_value": future_command,
            "source": "eligible_future_command",
        },
        {
            "field": "authorized_expected_output_path",
            "required": True,
            "expected_value": expected_output_path,
            "source": "eligible_expected_output_path",
        },
        {
            "field": "authorization_granted",
            "required": True,
            "expected_value": False,
            "source": "P90_GOVERNANCE_LOCK",
        },
        {
            "field": "authorization_token_created",
            "required": True,
            "expected_value": False,
            "source": "P90_GOVERNANCE_LOCK",
        },
        {
            "field": "execution_authority",
            "required": True,
            "expected_value": False,
            "source": "P90_GOVERNANCE_LOCK",
        },
    ]
    return sorted(fields, key=lambda item: str(item["field"]))


def _provenance_links(
    *,
    source_gate_path: str,
    source_gate_hash: str,
    source_p88_path: str,
    source_p88_hash: str,
) -> list[dict[str, Any]]:
    links = [
        {
            "link_id": "provenance_001_p89_gate",
            "source_artifact_path": source_gate_path,
            "source_artifact_hash": source_gate_hash,
            "relation": "AUTHORIZATION_GATE_INPUT",
            "required": True,
        },
        {
            "link_id": "provenance_002_p88_execution_plan",
            "source_artifact_path": source_p88_path,
            "source_artifact_hash": source_p88_hash,
            "relation": "UPSTREAM_EXECUTION_PLAN_CONTEXT",
            "required": source_p88_hash != "NOT_COMPUTABLE",
        },
    ]
    return sorted(links, key=lambda item: str(item["link_id"]))


def _replay_validation_requirements(
    *, source_gate_path: str, source_gate_hash: str
) -> list[dict[str, Any]]:
    requirements = [
        {
            "validation_id": "replay_validation_001_source_gate_exists",
            "validation_type": "source_exists",
            "path": source_gate_path,
            "required_status": "observed=true;readable=true",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P89_AUTHORIZATION_GATE_REGENERATION",
        },
        {
            "validation_id": "replay_validation_002_source_gate_hash_match",
            "validation_type": "source_hash_exact_match",
            "path": source_gate_path,
            "required_status": source_gate_hash,
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P89_AUTHORIZATION_GATE_REGENERATION",
        },
        {
            "validation_id": "replay_validation_003_source_gate_status",
            "validation_type": "status_exact_match",
            "path": source_gate_path,
            "required_status": "p83_regeneration_authorization_gate_status=P83_REGENERATION_AUTHORIZATION_ELIGIBLE",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P89_AUTHORIZATION_GATE_REGENERATION",
        },
        {
            "validation_id": "replay_validation_004_authority_locks",
            "validation_type": "authority_lock_check",
            "path": source_gate_path,
            "required_status": "authorization_granted=false;authorization_token_created=false;p83_regeneration_execution_allowed=false",
            "failure_action": "DENY_RECORD_CREATION_AND_ROUTE_TO_P89_AUTHORIZATION_GATE_REGENERATION",
        },
    ]
    return sorted(requirements, key=lambda item: str(item["validation_id"]))


def _denial_propagation_rules() -> list[dict[str, Any]]:
    rules = [
        {
            "denial_id": "denial_rule_001_missing_or_unreadable_source",
            "source_condition": "source_p89_gate_observed=false OR source_p89_gate_readable=false",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _GATE_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_002_p89_denied_or_not_computable",
            "source_condition": "source_p89_gate_status in {NOT_COMPUTABLE,P83_REGENERATION_AUTHORIZATION_DENIED}",
            "propagated_status": "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_DENIED",
            "recommended_lane": _GATE_REGENERATION_LANE,
        },
        {
            "denial_id": "denial_rule_003_invariant_violation",
            "source_condition": "eligible_invariants_violate_grant_token_execution_or_lane",
            "propagated_status": "NOT_COMPUTABLE",
            "recommended_lane": _GATE_REGENERATION_LANE,
        },
    ]
    return sorted(rules, key=lambda item: str(item["denial_id"]))


def build_temporal_continuity_p83_regeneration_authorization_record_plan(
    *,
    repo_root: str | Path = ".",
    source_p89_gate_path: str = SOURCE_P89_GATE_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p89 = _observe_source(
        root=root,
        rel_path=source_p89_gate_path,
        status_field="p83_regeneration_authorization_gate_status",
    )

    payload = p89.get("payload")
    inherited_payload: dict[str, Any] = payload if isinstance(payload, dict) else {}

    classification = _classify(p89)
    plan_status = str(classification["status"])
    required = bool(classification["required"])
    eligible_future_command = str(classification["eligible_future_command"])
    eligible_expected_output_path = str(classification["eligible_expected_output_path"])

    record_plan_items = [
        {
            "record_plan_item_id": "record_plan_item_001",
            "lane": "P83",
            "source_gate_path": source_p89_gate_path,
            "planned_record_artifact_type": "TemporalContinuityP83RegenerationAuthorizationRecord.v1",
            "future_command": eligible_future_command,
            "expected_output_path": eligible_expected_output_path,
            "authorization_record_creation_allowed": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_allowed": False,
            "blocking_reason": str(classification["blocking_reason"]),
        }
    ]
    record_plan_items = sorted(
        record_plan_items,
        key=lambda item: (
            str(item["record_plan_item_id"]),
            str(item["lane"]),
            str(item["source_gate_path"]),
        ),
    )

    required_record_fields = _required_record_fields(
        source_gate_path=source_p89_gate_path,
        source_gate_hash=str(p89["file_hash"]),
        future_command=eligible_future_command,
        expected_output_path=eligible_expected_output_path,
    )

    provenance_links = _provenance_links(
        source_gate_path=source_p89_gate_path,
        source_gate_hash=str(p89["file_hash"]),
        source_p88_path=str(
            inherited_payload.get("source_p88_execution_plan_path", "NOT_COMPUTABLE")
        ),
        source_p88_hash=str(
            inherited_payload.get("source_p88_execution_plan_hash", "NOT_COMPUTABLE")
        ),
    )

    expiration_policy = {
        "expiration_required": True,
        "expiration_basis": "operator_defined_expiration_timestamp",
        "max_validity_scope": "single_p83_regeneration_authorization_record",
        "renewal_requires_new_gate": True,
    }

    revocation_policy = {
        "revocation_supported": True,
        "revocation_triggers": [
            "source_gate_hash_mismatch",
            "source_gate_status_change",
            "operator_revocation",
            "drift_or_evidence_degradation_detected",
        ],
        "revocation_effect": "authorization_record_invalidated_and_execution_denied",
        "revocation_requires_new_record_plan": True,
    }

    replay_validation_requirements = _replay_validation_requirements(
        source_gate_path=source_p89_gate_path,
        source_gate_hash=str(p89["file_hash"]),
    )
    denial_propagation_rules = _denial_propagation_rules()

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
        "authorization_record_plan_only": True,
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
        "source_p89_gate_path": source_p89_gate_path,
        "source_p89_gate_observed": bool(p89["observed"]),
        "source_p89_gate_readable": bool(p89["readable"]),
        "source_p89_gate_hash": str(p89["file_hash"]),
        "source_p89_gate_status": str(p89["status"]),
        "source_p89_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p83_regeneration_record_plan_status": (
            plan_status if plan_status in _ALLOWED_PLAN_STATUSES else "NOT_COMPUTABLE"
        ),
        "p83_regeneration_record_required": required,
        "p83_regeneration_record_creation_allowed": False,
        "record_plan_items": record_plan_items,
        "required_record_fields": required_record_fields,
        "provenance_links": provenance_links,
        "expiration_policy": expiration_policy,
        "revocation_policy": revocation_policy,
        "replay_validation_requirements": replay_validation_requirements,
        "denial_propagation_rules": denial_propagation_rules,
        "eligible_future_command": eligible_future_command,
        "eligible_expected_output_path": eligible_expected_output_path,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "record_strategy_summary": {
            "record_plan_items_count": len(record_plan_items),
            "required_record_fields_count": len(required_record_fields),
            "provenance_links_count": len(provenance_links),
            "replay_validation_requirements_count": len(replay_validation_requirements),
            "denial_propagation_rules_count": len(denial_propagation_rules),
            "p83_regeneration_record_plan_status": (
                plan_status if plan_status in _ALLOWED_PLAN_STATUSES else "NOT_COMPUTABLE"
            ),
            "p83_regeneration_record_required": required,
            "p83_regeneration_record_creation_allowed": False,
            "authorization_record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_authority": False,
            "regeneration_execution_authority": False,
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


def write_temporal_continuity_p83_regeneration_authorization_record_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
