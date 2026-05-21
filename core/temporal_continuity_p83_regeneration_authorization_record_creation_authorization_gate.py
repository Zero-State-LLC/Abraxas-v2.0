from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "TemporalContinuityP83RegenerationAuthorizationRecordCreationAuthorizationGate.v1"
)
SOURCE_P91_CREATION_PLAN_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json"
)
EXPECTED_P91_RECOMMENDED_NEXT_LANE = (
    "P92_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
)

_P91_REGENERATION_LANE = "P91_AUTHORIZATION_RECORD_CREATION_PLAN_REGENERATION"
_NOT_REQUIRED_NEXT_LANE = (
    "P93_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
)
_ELIGIBLE_NEXT_LANE = (
    "P93_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN"
)

_GATE_STATUSES = (
    "NOT_COMPUTABLE",
    "P83_RECORD_CREATION_AUTHORIZATION_ELIGIBLE",
    "P83_RECORD_CREATION_AUTHORIZATION_DENIED",
    "P83_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED",
)

_ELIGIBILITY_REASON_ORDER = (
    "P91_CREATION_PLAN_READY",
    "P91_RECOMMENDS_P92_GATE",
    "P91_RECORD_OUTPUT_DEFINED",
    "P91_CREATION_LOCKS_FALSE",
    "P91_AUTHORITY_LOCKS_FALSE",
    "RECORD_CREATION_ELIGIBLE_BUT_NOT_GRANTED",
)
_ELIGIBILITY_REASON_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_ELIGIBILITY_REASON_ORDER)
}

_DENIAL_REASON_ORDER = (
    "P91_SOURCE_MISSING",
    "P91_SOURCE_UNREADABLE",
    "P91_SOURCE_MALFORMED_JSON",
    "P91_NOT_COMPUTABLE",
    "P91_CREATION_PLAN_DENIED",
    "P91_CREATION_NOT_REQUIRED",
    "P91_RECOMMENDED_LANE_MISMATCH",
    "P91_RECORD_OUTPUT_MISSING",
    "P91_CREATION_LOCK_VIOLATION",
    "P91_AUTHORITY_LOCK_VIOLATION",
    "CREATION_AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P92",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_DENIAL_REASON_ORDER_INDEX = {reason: idx for idx, reason in enumerate(_DENIAL_REASON_ORDER)}

_PREREQUISITE_CHECK_ORDER = (
    "prerequisite_001_source_exists_readable",
    "prerequisite_002_source_status_ready",
    "prerequisite_003_source_lane_exact_match",
    "prerequisite_004_record_output_defined",
    "prerequisite_005_creation_locks_false",
    "prerequisite_006_authority_locks_false",
)
_PREREQUISITE_CHECK_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_PREREQUISITE_CHECK_ORDER)
}

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

_P91_AUTHORITY_FIELDS = (
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


def _all_p91_authority_fields_false(payload: dict[str, Any]) -> bool:
    return all(payload.get(field) is False for field in _P91_AUTHORITY_FIELDS)


def _prerequisite_checks(
    *,
    source_observed: bool,
    source_readable: bool,
    source_status: str,
    source_recommended_lane: str,
    has_planned_record_output: bool,
    creation_locks_false: bool,
    authority_locks_false: bool,
) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "prerequisite_001_source_exists_readable",
            "check_type": "source_exists_readable",
            "path": SOURCE_P91_CREATION_PLAN_PATH,
            "required_status": "observed=true;readable=true",
            "satisfied": source_observed and source_readable,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P91_AUTHORIZATION_RECORD_CREATION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_002_source_status_ready",
            "check_type": "status_exact_match",
            "path": SOURCE_P91_CREATION_PLAN_PATH,
            "required_status": "p83_regeneration_record_creation_plan_status=P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY",
            "satisfied": (
                source_status
                == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY"
            ),
            "failure_action": "DENY_AUTHORIZATION_ELIGIBILITY_AND_ROUTE_TO_P91_AUTHORIZATION_RECORD_CREATION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_003_source_lane_exact_match",
            "check_type": "recommended_lane_exact_match",
            "path": "recommended_next_lane",
            "required_status": EXPECTED_P91_RECOMMENDED_NEXT_LANE,
            "satisfied": source_recommended_lane == EXPECTED_P91_RECOMMENDED_NEXT_LANE,
            "failure_action": "MARK_NOT_COMPUTABLE_AND_ROUTE_TO_P91_AUTHORIZATION_RECORD_CREATION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_004_record_output_defined",
            "check_type": "record_output_defined",
            "path": "planned_record_output",
            "required_status": "planned_record_output.path/artifact_type present",
            "satisfied": has_planned_record_output,
            "failure_action": "DENY_AUTHORIZATION_ELIGIBILITY_AND_ROUTE_TO_P91_AUTHORIZATION_RECORD_CREATION_PLAN_REGENERATION",
        },
        {
            "check_id": "prerequisite_005_creation_locks_false",
            "check_type": "creation_lock_check",
            "path": SOURCE_P91_CREATION_PLAN_PATH,
            "required_status": "record_creation_required=true;record_creation_allowed=false;authorization_record_created=false;authorization_granted=false;authorization_token_created=false;planned_record_output.creation_allowed=false;planned_record_output.creation_authority=false",
            "satisfied": creation_locks_false,
            "failure_action": "DENY_AUTHORIZATION_ELIGIBILITY_AND_FAIL_CLOSED_ON_CREATION_LOCK_VIOLATION",
        },
        {
            "check_id": "prerequisite_006_authority_locks_false",
            "check_type": "source_authority_lock_check",
            "path": SOURCE_P91_CREATION_PLAN_PATH,
            "required_status": "all_authority_fields=false",
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


def _classify(p91: dict[str, Any]) -> dict[str, Any]:
    p91_status = str(p91["status"])
    payload = p91.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}

    source_recommended_lane = str(payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE"))
    planned_record_output = payload_dict.get("planned_record_output")
    output_dict = planned_record_output if isinstance(planned_record_output, dict) else {}
    has_planned_record_output = isinstance(planned_record_output, dict)
    planned_record_output_path = str(output_dict.get("path", "NOT_COMPUTABLE"))
    planned_record_artifact_type = str(output_dict.get("artifact_type", "NOT_COMPUTABLE"))

    creation_locks_false = (
        payload_dict.get("p83_regeneration_record_creation_required") is True
        and payload_dict.get("p83_regeneration_record_creation_allowed") is False
        and payload_dict.get("authorization_record_created") is False
        and payload_dict.get("authorization_granted") is False
        and payload_dict.get("authorization_token_created") is False
        and output_dict.get("creation_allowed") is False
        and output_dict.get("creation_authority") is False
    )
    authority_locks_false = _all_p91_authority_fields_false(payload_dict)

    if not p91["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": _P91_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P91 authorization record creation plan source is missing; regenerate P91 before deriving P92 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P91_SOURCE_MISSING"],
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": "NOT_COMPUTABLE",
            "planned_record_artifact_type": "NOT_COMPUTABLE",
            "has_planned_record_output": False,
            "creation_locks_false": False,
            "authority_locks_false": False,
        }

    if not p91["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": _P91_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P91 authorization record creation plan source is unreadable; regenerate P91 before deriving P92 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P91_SOURCE_UNREADABLE"],
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": "NOT_COMPUTABLE",
            "planned_record_artifact_type": "NOT_COMPUTABLE",
            "has_planned_record_output": False,
            "creation_locks_false": False,
            "authority_locks_false": False,
        }

    if p91["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": _P91_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P91 authorization record creation plan source is malformed JSON; regenerate P91 before deriving P92 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P91_SOURCE_MALFORMED_JSON"],
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": "NOT_COMPUTABLE",
            "planned_record_artifact_type": "NOT_COMPUTABLE",
            "has_planned_record_output": False,
            "creation_locks_false": False,
            "authority_locks_false": False,
        }

    if p91_status == "NOT_COMPUTABLE":
        return {
            "status": "P83_RECORD_CREATION_AUTHORIZATION_DENIED",
            "eligible": False,
            "recommended_next_lane": _P91_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P91 reports NOT_COMPUTABLE; record-creation authorization eligibility is denied until P91 is regenerated."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P91_NOT_COMPUTABLE"],
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "has_planned_record_output": has_planned_record_output,
            "creation_locks_false": creation_locks_false,
            "authority_locks_false": authority_locks_false,
        }

    if p91_status == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_DENIED":
        return {
            "status": "P83_RECORD_CREATION_AUTHORIZATION_DENIED",
            "eligible": False,
            "recommended_next_lane": _P91_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P91 reports creation-plan denied; record-creation authorization eligibility is denied until P91 is regenerated."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P91_CREATION_PLAN_DENIED"],
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "has_planned_record_output": has_planned_record_output,
            "creation_locks_false": creation_locks_false,
            "authority_locks_false": authority_locks_false,
        }

    if p91_status == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_NOT_REQUIRED":
        return {
            "status": "P83_RECORD_CREATION_AUTHORIZATION_NOT_REQUIRED",
            "eligible": False,
            "recommended_next_lane": _NOT_REQUIRED_NEXT_LANE,
            "recommended_next_lane_reason": (
                "P91 reports authorization record creation not required; P92 authorization gate remains not required."
            ),
            "eligibility_reasons": [],
            "denial_reasons": ["P91_CREATION_NOT_REQUIRED"],
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "has_planned_record_output": has_planned_record_output,
            "creation_locks_false": creation_locks_false,
            "authority_locks_false": authority_locks_false,
        }

    if p91_status == "P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY":
        lane_match = source_recommended_lane == EXPECTED_P91_RECOMMENDED_NEXT_LANE

        if (
            lane_match
            and has_planned_record_output
            and creation_locks_false
            and authority_locks_false
        ):
            return {
                "status": "P83_RECORD_CREATION_AUTHORIZATION_ELIGIBLE",
                "eligible": True,
                "recommended_next_lane": _ELIGIBLE_NEXT_LANE,
                "recommended_next_lane_reason": (
                    "P91 is ready with expected lane and creation/authority locks false; P83 authorization record creation is eligible but not granted in P92."
                ),
                "eligibility_reasons": [
                    "P91_CREATION_PLAN_READY",
                    "P91_RECOMMENDS_P92_GATE",
                    "P91_RECORD_OUTPUT_DEFINED",
                    "P91_CREATION_LOCKS_FALSE",
                    "P91_AUTHORITY_LOCKS_FALSE",
                    "RECORD_CREATION_ELIGIBLE_BUT_NOT_GRANTED",
                ],
                "denial_reasons": ["CREATION_AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P92"],
                "source_recommended_lane": source_recommended_lane,
                "planned_record_output_path": planned_record_output_path,
                "planned_record_artifact_type": planned_record_artifact_type,
                "has_planned_record_output": has_planned_record_output,
                "creation_locks_false": creation_locks_false,
                "authority_locks_false": authority_locks_false,
            }

        denial_reasons: list[str] = []
        if not lane_match:
            denial_reasons.append("P91_RECOMMENDED_LANE_MISMATCH")
        if not has_planned_record_output:
            denial_reasons.append("P91_RECORD_OUTPUT_MISSING")
        if not creation_locks_false:
            denial_reasons.append("P91_CREATION_LOCK_VIOLATION")
        if not authority_locks_false:
            denial_reasons.append("P91_AUTHORITY_LOCK_VIOLATION")
        if not denial_reasons:
            denial_reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")

        return {
            "status": "NOT_COMPUTABLE",
            "eligible": False,
            "recommended_next_lane": _P91_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P91 ready signal is weak or inconsistent with lane/output/lock invariants; regenerate P91 before deriving P92 authorization gating."
            ),
            "eligibility_reasons": [],
            "denial_reasons": denial_reasons,
            "source_recommended_lane": source_recommended_lane,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "has_planned_record_output": has_planned_record_output,
            "creation_locks_false": creation_locks_false,
            "authority_locks_false": authority_locks_false,
        }

    return {
        "status": "NOT_COMPUTABLE",
        "eligible": False,
        "recommended_next_lane": _P91_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P91 creation plan status is missing or unsupported; regenerate P91 before deriving P92 authorization gating."
        ),
        "eligibility_reasons": [],
        "denial_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
        "source_recommended_lane": source_recommended_lane,
        "planned_record_output_path": planned_record_output_path,
        "planned_record_artifact_type": planned_record_artifact_type,
        "has_planned_record_output": has_planned_record_output,
        "creation_locks_false": creation_locks_false,
        "authority_locks_false": authority_locks_false,
    }


def build_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
    *,
    repo_root: str | Path = ".",
    source_p91_creation_plan_path: str = SOURCE_P91_CREATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p91 = _observe_source(
        root=root,
        rel_path=source_p91_creation_plan_path,
        status_field="p83_regeneration_record_creation_plan_status",
    )
    p91_payload = p91.get("payload")
    inherited_payload: dict[str, Any] = p91_payload if isinstance(p91_payload, dict) else {}

    classification = _classify(p91)
    status = str(classification["status"])
    eligible = bool(classification["eligible"])
    source_recommended_lane = str(classification["source_recommended_lane"])
    planned_record_output_path = str(classification["planned_record_output_path"])
    planned_record_artifact_type = str(classification["planned_record_artifact_type"])
    has_planned_record_output = bool(classification["has_planned_record_output"])
    creation_locks_false = bool(classification["creation_locks_false"])
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
        source_observed=bool(p91["observed"]),
        source_readable=bool(p91["readable"]),
        source_status=str(p91["status"]),
        source_recommended_lane=source_recommended_lane,
        has_planned_record_output=has_planned_record_output,
        creation_locks_false=creation_locks_false,
        authority_locks_false=authority_locks_false,
    )

    gate_items: list[dict[str, Any]] = [
        {
            "gate_item_id": "gate_item_001",
            "lane": "P83",
            "source_creation_plan_path": source_p91_creation_plan_path,
            "planned_record_output_path": planned_record_output_path,
            "planned_record_artifact_type": planned_record_artifact_type,
            "authorization_eligible": eligible,
            "authorization_granted": False,
            "record_creation_allowed": False,
            "record_created": False,
            "token_created": False,
            "execution_allowed": False,
            "blocking_reason": (
                str(denial_reasons[0])
                if denial_reasons
                else "CREATION_AUTHORIZATION_GRANT_NOT_PERMITTED_IN_P92"
            ),
        }
    ]
    gate_items = sorted(
        gate_items,
        key=lambda item: (
            str(item["gate_item_id"]),
            str(item["lane"]),
            str(item["source_creation_plan_path"]),
        ),
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "authorization_gate_only": True,
        "authorization_record_creation_gate_only": True,
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
        "source_p91_creation_plan_path": source_p91_creation_plan_path,
        "source_p91_creation_plan_observed": bool(p91["observed"]),
        "source_p91_creation_plan_readable": bool(p91["readable"]),
        "source_p91_creation_plan_hash": str(p91["file_hash"]),
        "source_p91_creation_plan_status": str(p91["status"]),
        "source_p91_recommended_next_lane": source_recommended_lane,
        "p83_record_creation_authorization_gate_status": (
            status if status in _GATE_STATUSES else "NOT_COMPUTABLE"
        ),
        "p83_record_creation_authorization_eligible": eligible,
        "p83_record_creation_authorization_granted": False,
        "p83_record_creation_allowed": False,
        "p83_regeneration_execution_allowed": False,
        "eligibility_reasons": eligibility_reasons,
        "denial_reasons": denial_reasons,
        "prerequisite_checks": prerequisite_checks,
        "gate_items": gate_items,
        "planned_record_output_path": planned_record_output_path,
        "planned_record_artifact_type": planned_record_artifact_type,
        "eligible_future_command": "NOT_COMPUTABLE",
        "eligible_expected_output_path": "NOT_COMPUTABLE",
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "gate_strategy_summary": {
            "prerequisite_checks_count": len(prerequisite_checks),
            "gate_items_count": len(gate_items),
            "eligibility_reasons_count": len(eligibility_reasons),
            "denial_reasons_count": len(denial_reasons),
            "p83_record_creation_authorization_gate_status": (
                status if status in _GATE_STATUSES else "NOT_COMPUTABLE"
            ),
            "p83_record_creation_authorization_eligible": eligible,
            "authorization_record_creation_authority": False,
            "authorization_record_created": False,
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


def write_temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
