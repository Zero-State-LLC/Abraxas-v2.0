from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityAuthorizationRecordPlanSourceStatusAudit.v1"
SOURCE_P80_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)
SOURCE_P79_PATH = "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
SOURCE_P78_PATH = "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json"

_REASON_ORDER = (
    "P80_SOURCE_MISSING",
    "P80_SOURCE_UNREADABLE",
    "P80_SOURCE_MALFORMED_JSON",
    "P80_STATUS_NOT_COMPUTABLE",
    "P79_SOURCE_MISSING",
    "P79_SOURCE_UNREADABLE",
    "P79_SOURCE_MALFORMED_JSON",
    "P79_STATUS_NOT_COMPUTABLE",
    "P79_NOT_AUTHORIZATION_ELIGIBLE",
    "P78_SOURCE_MISSING",
    "P78_STATUS_NOT_COMPUTABLE",
    "STATUS_FIELD_MISSING",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_REASON_ORDER_INDEX = {reason: index for index, reason in enumerate(_REASON_ORDER)}

_DENIED_AUTHORITY = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
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

_SOURCE_STATUS_FIELDS = {
    "P78": "execution_plan_status",
    "P79": "authorization_gate_status",
    "P80": "authorization_record_plan_status",
}


def _observe_source(*, lane: str, root: Path, rel_path: str) -> dict[str, Any]:
    status_field = _SOURCE_STATUS_FIELDS[lane]
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    packet_hash = "NOT_COMPUTABLE"
    status_value = "NOT_COMPUTABLE"
    recommended_next_lane = "NOT_COMPUTABLE"
    payload: dict[str, Any] | None = None
    status_field_missing = False

    if observed:
        try:
            source_bytes = source_path.read_bytes()
            readable = True
            file_hash = hashlib.sha256(source_bytes).hexdigest()
        except OSError:
            readable = False
        if readable:
            try:
                parsed = json.loads(source_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                malformed_json = True
                parsed = None
            if isinstance(parsed, dict):
                payload = parsed
                packet_hash = str(parsed.get("packet_hash", "NOT_COMPUTABLE"))
                if status_field in parsed:
                    status_value = str(parsed.get(status_field, "NOT_COMPUTABLE"))
                else:
                    status_field_missing = True
                    status_value = "NOT_COMPUTABLE"
                recommended_next_lane = str(
                    parsed.get("recommended_next_lane", "NOT_COMPUTABLE")
                )
            else:
                malformed_json = True

    if not observed:
        blocking_reason = f"{lane}_SOURCE_MISSING"
    elif not readable:
        blocking_reason = f"{lane}_SOURCE_UNREADABLE"
    elif malformed_json:
        blocking_reason = f"{lane}_SOURCE_MALFORMED_JSON"
    elif status_field_missing:
        blocking_reason = "STATUS_FIELD_MISSING"
    elif status_value == "NOT_COMPUTABLE":
        blocking_reason = f"{lane}_STATUS_NOT_COMPUTABLE"
    else:
        blocking_reason = ""

    return {
        "lane": lane,
        "path": rel_path,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "packet_hash": packet_hash,
        "status_field": status_field,
        "status_value": status_value,
        "recommended_next_lane": recommended_next_lane,
        "blocking_reason": blocking_reason,
        "status_field_missing": status_field_missing,
        "payload": payload,
    }


def _reason_list(reasons: list[str]) -> list[str]:
    unique = list(dict.fromkeys(reasons))
    return sorted(unique, key=lambda reason: _REASON_ORDER_INDEX.get(reason, 10_000))


def _classify(
    *,
    p78: dict[str, Any],
    p79: dict[str, Any],
    p80: dict[str, Any],
    reasons: list[str],
) -> tuple[str, str, str]:
    if not p80["observed"]:
        reasons.append("P80_SOURCE_MISSING")
        return (
            "NOT_COMPUTABLE",
            "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "P80 authorization record plan source is missing; regenerate P80 before source-chain auditing.",
        )
    if not p80["readable"]:
        reasons.append("P80_SOURCE_UNREADABLE")
        return (
            "NOT_COMPUTABLE",
            "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "P80 authorization record plan source is unreadable; regenerate P80 before source-chain auditing.",
        )
    if p80["malformed_json"]:
        reasons.append("P80_SOURCE_MALFORMED_JSON")
        return (
            "NOT_COMPUTABLE",
            "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "P80 authorization record plan source is malformed JSON; regenerate P80 before source-chain auditing.",
        )

    if p80["status_field_missing"]:
        reasons.append("STATUS_FIELD_MISSING")
    p80_status = str(p80["status_value"])

    if p80_status == "NOT_COMPUTABLE":
        reasons.append("P80_STATUS_NOT_COMPUTABLE")

        if not p79["observed"]:
            reasons.append("P79_SOURCE_MISSING")
            return (
                "SOURCE_CHAIN_BLOCKED",
                "P79_AUTHORIZATION_GATE_REGENERATION",
                "P80 is NOT_COMPUTABLE because P79 authorization gate source is missing.",
            )
        if not p79["readable"]:
            reasons.append("P79_SOURCE_UNREADABLE")
            return (
                "SOURCE_CHAIN_BLOCKED",
                "P79_AUTHORIZATION_GATE_REGENERATION",
                "P80 is NOT_COMPUTABLE because P79 authorization gate source is unreadable.",
            )
        if p79["malformed_json"]:
            reasons.append("P79_SOURCE_MALFORMED_JSON")
            return (
                "SOURCE_CHAIN_BLOCKED",
                "P79_AUTHORIZATION_GATE_REGENERATION",
                "P80 is NOT_COMPUTABLE because P79 authorization gate source is malformed JSON.",
            )

        if p79["status_field_missing"]:
            reasons.append("STATUS_FIELD_MISSING")
        p79_status = str(p79["status_value"])

        if p79_status == "NOT_COMPUTABLE":
            reasons.append("P79_STATUS_NOT_COMPUTABLE")
            return (
                "SOURCE_CHAIN_BLOCKED",
                "P79_AUTHORIZATION_GATE_SOURCE_REPAIR_PLAN",
                "P79 authorization gate status is NOT_COMPUTABLE; source repair planning is required before P80 regeneration.",
            )

        if p79_status == "AUTHORIZATION_ELIGIBLE":
            return (
                "SOURCE_CHAIN_READY_FOR_P80_REGENERATION",
                "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
                "P79 authorization gate is AUTHORIZATION_ELIGIBLE while P80 remains NOT_COMPUTABLE; regenerate P80 authorization record plan.",
            )

        reasons.append("P79_NOT_AUTHORIZATION_ELIGIBLE")
        reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")
        return (
            "NOT_COMPUTABLE",
            "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
            "P80 is NOT_COMPUTABLE and P79 is not AUTHORIZATION_ELIGIBLE; regenerate P80 after resolving source-chain inconsistency.",
        )

    if p80_status == "AUTHORIZATION_RECORD_PLAN_READY":
        return (
            "SOURCE_CHAIN_READY_FOR_P81_TEMPLATE",
            "P81_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE",
            "P80 authorization record plan is ready; safe to proceed to P81 operator authorization record template work.",
        )

    if p80_status == "AUTHORIZATION_RECORD_PLAN_BLOCKED":
        return (
            "SOURCE_CHAIN_BLOCKED",
            "P81_TEMPORAL_CONTINUITY_AUTHORIZATION_BLOCKER_REPAIR_PLAN",
            "P80 authorization record plan is blocked; repair blockers before any template work.",
        )

    if p80_status == "AUTHORIZATION_RECORD_NOT_REQUIRED":
        return (
            "SOURCE_CHAIN_READY_FOR_P81_TEMPLATE",
            "P81_TEMPORAL_CONTINUITY_AUTHORIZATION_NOT_REQUIRED_ROUTING_AUDIT",
            "P80 indicates authorization record not required; proceed with authorization-not-required routing audit.",
        )

    if p80["status_field_missing"]:
        reasons.append("STATUS_FIELD_MISSING")
    reasons.append("WEAK_OR_INCONSISTENT_SOURCE_CHAIN")
    return (
        "NOT_COMPUTABLE",
        "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION",
        "P80 status is missing or inconsistent; regenerate P80 authorization record plan.",
    )


def _first_available_string_list(
    sources: tuple[dict[str, Any], ...], field: str
) -> list[str]:
    for source in sources:
        payload = source.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get(field), list):
            value = payload[field]
            if all(isinstance(item, str) for item in value):
                return list(value)
            return [str(item) for item in value]
    return []


def build_temporal_continuity_authorization_record_plan_source_status_audit(
    *,
    repo_root: str | Path = ".",
    source_p80_path: str = SOURCE_P80_PATH,
    source_p79_path: str = SOURCE_P79_PATH,
    source_p78_path: str = SOURCE_P78_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p78 = _observe_source(lane="P78", root=root, rel_path=source_p78_path)
    p79 = _observe_source(lane="P79", root=root, rel_path=source_p79_path)
    p80 = _observe_source(lane="P80", root=root, rel_path=source_p80_path)

    reasons: list[str] = []
    source_chain_status, recommended_next_lane, recommended_next_lane_reason = _classify(
        p78=p78,
        p79=p79,
        p80=p80,
        reasons=reasons,
    )

    if source_chain_status != "SOURCE_CHAIN_READY_FOR_P81_TEMPLATE":
        if not p78["observed"]:
            reasons.append("P78_SOURCE_MISSING")
        elif p78["status_value"] == "NOT_COMPUTABLE":
            reasons.append("P78_STATUS_NOT_COMPUTABLE")

    not_computable_reasons = _reason_list(reasons)

    chain_items = [
        {
            "lane": item["lane"],
            "path": item["path"],
            "observed": item["observed"],
            "readable": item["readable"],
            "malformed_json": item["malformed_json"],
            "packet_hash": item["packet_hash"],
            "status_field": item["status_field"],
            "status_value": item["status_value"],
            "recommended_next_lane": item["recommended_next_lane"],
            "blocking_reason": item["blocking_reason"],
        }
        for item in (p78, p79, p80)
    ]

    degraded_evidence_inputs = _first_available_string_list(
        (p80, p79, p78), "degraded_evidence_inputs"
    )
    inherited_blockers = _first_available_string_list(
        (p80, p79, p78), "inherited_blockers"
    )
    inherited_drift_flags = _first_available_string_list(
        (p80, p79, p78), "inherited_drift_flags"
    )
    semantic_overlap_flags = _first_available_string_list(
        (p80, p79, p78), "semantic_overlap_flags"
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "source_status_audit_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "spine_implementation_authority": False,
        "source_p80_path": source_p80_path,
        "source_p80_observed": p80["observed"],
        "source_p80_readable": p80["readable"],
        "source_p80_hash": p80["file_hash"],
        "source_p80_status": p80["status_value"],
        "source_p79_path": source_p79_path,
        "source_p79_observed": p79["observed"],
        "source_p79_readable": p79["readable"],
        "source_p79_hash": p79["file_hash"],
        "source_p79_status": p79["status_value"],
        "source_p78_path": source_p78_path,
        "source_p78_observed": p78["observed"],
        "source_p78_readable": p78["readable"],
        "source_p78_hash": p78["file_hash"],
        "source_p78_status": p78["status_value"],
        "source_chain_status": source_chain_status,
        "not_computable_reasons": not_computable_reasons,
        "source_chain_items": chain_items,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "source_status_summary": {
            "source_chain_status": source_chain_status,
            "source_p78_status": p78["status_value"],
            "source_p79_status": p79["status_value"],
            "source_p80_status": p80["status_value"],
            "not_computable_reasons_count": len(not_computable_reasons),
        },
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_authorization_record_plan_source_status_audit(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
