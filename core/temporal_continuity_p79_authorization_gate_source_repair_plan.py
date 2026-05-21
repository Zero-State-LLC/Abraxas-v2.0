from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP79AuthorizationGateSourceRepairPlan.v1"
SOURCE_P81_AUDIT_PATH = (
    "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json"
)

_DENIED_AUTHORITY = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "repair_execution_authority",
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

_REASON_ORDER = (
    "P79_SOURCE_MISSING",
    "P79_SOURCE_UNREADABLE",
    "P79_SOURCE_MALFORMED_JSON",
    "P79_STATUS_NOT_COMPUTABLE",
    "P79_NOT_AUTHORIZATION_ELIGIBLE",
    "P78_SOURCE_MISSING",
    "P78_STATUS_NOT_COMPUTABLE",
    "STATUS_FIELD_MISSING",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
    "NOT_COMPUTABLE",
)
_REASON_ORDER_INDEX = {reason: index for index, reason in enumerate(_REASON_ORDER)}

_FAILURE_MODE_ORDER = (
    "P79_SOURCE_MISSING",
    "P79_SOURCE_UNREADABLE",
    "P79_SOURCE_MALFORMED_JSON",
    "P79_STATUS_NOT_COMPUTABLE",
    "P79_NOT_AUTHORIZATION_ELIGIBLE",
    "P78_SOURCE_BLOCKING_P79",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
    "NOT_COMPUTABLE",
)
_FAILURE_MODE_ORDER_INDEX = {
    mode: index for index, mode in enumerate(_FAILURE_MODE_ORDER)
}

_REPAIR_STRATEGY_ORDER = (
    "REGENERATE_P79_AUTHORIZATION_GATE",
    "REPAIR_P79_SOURCE_SCHEMA_OR_STATUS",
    "REGENERATE_P78_EXECUTION_PLAN_FIRST",
    "REPAIR_P78_SOURCE_FIRST",
    "RERUN_P80_AFTER_P79_REPAIR",
    "NO_REPAIR_REQUIRED",
    "NOT_COMPUTABLE",
)
_REPAIR_STRATEGY_ORDER_INDEX = {
    strategy: index for index, strategy in enumerate(_REPAIR_STRATEGY_ORDER)
}


def _ordered_unique(
    values: list[str], order_index: dict[str, int], *, fallback: int = 10_000
) -> list[str]:
    unique = list(dict.fromkeys(values))
    return sorted(unique, key=lambda value: order_index.get(value, fallback))


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    if all(isinstance(item, str) for item in value):
        return list(value)
    return [str(item) for item in value]


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _observe_p81(*, root: Path, rel_path: str) -> dict[str, Any]:
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    source_chain_status = "NOT_COMPUTABLE"
    recommended_next_lane = "NOT_COMPUTABLE"
    payload: dict[str, Any] | None = None

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
                source_chain_status = str(
                    parsed.get("source_chain_status", "NOT_COMPUTABLE")
                )
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
        "source_chain_status": source_chain_status,
        "recommended_next_lane": recommended_next_lane,
        "payload": payload,
    }


def _find_source_chain_item(payload: dict[str, Any] | None, lane: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    for item in _as_dict_list(payload.get("source_chain_items")):
        if str(item.get("lane", "")) == lane:
            return item
    return {}


def _source_item_path(item: dict[str, Any], fallback: str) -> str:
    return str(item.get("path", fallback))


def _source_item_bool(item: dict[str, Any], field: str, fallback: bool) -> bool:
    value = item.get(field)
    return value if isinstance(value, bool) else fallback


def _source_item_str(item: dict[str, Any], field: str, fallback: str) -> str:
    value = item.get(field)
    return str(value) if value is not None else fallback


def _source_payload_list(payload: dict[str, Any] | None, field: str) -> list[str]:
    if not isinstance(payload, dict):
        return []
    return _as_str_list(payload.get(field))


def _failure_mode_from_reason(reason: str) -> str | None:
    if reason in {
        "P79_SOURCE_MISSING",
        "P79_SOURCE_UNREADABLE",
        "P79_SOURCE_MALFORMED_JSON",
        "P79_STATUS_NOT_COMPUTABLE",
        "P79_NOT_AUTHORIZATION_ELIGIBLE",
    }:
        return reason
    if reason in {"P78_SOURCE_MISSING", "P78_STATUS_NOT_COMPUTABLE"}:
        return "P78_SOURCE_BLOCKING_P79"
    if reason in {"STATUS_FIELD_MISSING", "WEAK_OR_INCONSISTENT_SOURCE_CHAIN"}:
        return "WEAK_OR_INCONSISTENT_SOURCE_CHAIN"
    if reason == "NOT_COMPUTABLE":
        return "NOT_COMPUTABLE"
    return None


def _p79_failure_modes(reasons: list[str], *, fallback_not_computable: bool) -> list[str]:
    failure_modes = [
        failure_mode
        for reason in reasons
        if (failure_mode := _failure_mode_from_reason(reason)) is not None
    ]
    if fallback_not_computable and not failure_modes:
        failure_modes.append("NOT_COMPUTABLE")
    return _ordered_unique(failure_modes, _FAILURE_MODE_ORDER_INDEX)


def _sorted_paths(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(value for value in values if value))


def _build_repair_item(
    *,
    repair_item_id: str,
    lane: str,
    path: str,
    observed: bool,
    readable: bool,
    malformed_json: bool,
    status_field: str,
    status_value: str,
    failure_mode: str,
    repair_strategy: str,
    prerequisite_paths: list[str],
    blocking_reason: str,
) -> dict[str, Any]:
    return {
        "repair_item_id": repair_item_id,
        "lane": lane,
        "path": path,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "status_field": status_field,
        "status_value": status_value,
        "failure_mode": failure_mode,
        "repair_strategy": repair_strategy,
        "prerequisite_paths": _sorted_paths(prerequisite_paths),
        "repair_execution_allowed": False,
        "blocking_reason": blocking_reason,
    }


def _build_status_not_computable_packet(
    *,
    p81: dict[str, Any],
    p79_source_path: str,
    p79_source_status: str,
    failure_mode: str,
    blocking_reason: str,
    recommended_next_lane_reason: str,
) -> dict[str, Any]:
    return {
        "p79_source_repair_plan_status": "NOT_COMPUTABLE",
        "recommended_next_lane": "P81_SOURCE_STATUS_AUDIT_REGENERATION",
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "p79_source_status": p79_source_status,
        "p79_source_path": p79_source_path,
        "p79_failure_modes": [failure_mode],
        "repair_items": [
            _build_repair_item(
                repair_item_id="repair_item_p81_001",
                lane="P81",
                path=str(p81["path"]),
                observed=bool(p81["observed"]),
                readable=bool(p81["readable"]),
                malformed_json=bool(p81["malformed_json"]),
                status_field="source_chain_status",
                status_value=str(p81["source_chain_status"]),
                failure_mode=failure_mode,
                repair_strategy="NOT_COMPUTABLE",
                prerequisite_paths=[],
                blocking_reason=blocking_reason,
            )
        ],
        "blocked_repair_reasons": [blocking_reason],
        "prerequisite_sources": [],
    }


def _classify_packet(
    *,
    p81: dict[str, Any],
    p81_payload: dict[str, Any],
    p78_item: dict[str, Any],
    p79_item: dict[str, Any],
    p81_reasons: list[str],
) -> dict[str, Any]:
    p78_path = str(p81_payload.get("source_p78_path", "NOT_COMPUTABLE"))
    p78_status = str(p81_payload.get("source_p78_status", "NOT_COMPUTABLE"))
    p79_path = str(p81_payload.get("source_p79_path", "NOT_COMPUTABLE"))
    p79_status = str(p81_payload.get("source_p79_status", "NOT_COMPUTABLE"))

    if str(p81["source_chain_status"]) != "SOURCE_CHAIN_BLOCKED":
        next_lane = (
            "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION"
            if str(p81["recommended_next_lane"])
            == "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION"
            else "P81_RECOMMENDED_NEXT_LANE_PASSTHROUGH"
        )
        return {
            "p79_source_repair_plan_status": "P79_REPAIR_NOT_REQUIRED",
            "recommended_next_lane": next_lane,
            "recommended_next_lane_reason": (
                "P81 source chain is not blocked; no P79 source repair plan is required."
                if next_lane == "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION"
                else (
                    "P81 source chain is not blocked; preserve the P81 recommended next "
                    f"lane ({p81['recommended_next_lane']}) instead of introducing P79 repair."
                )
            ),
            "p79_source_status": p79_status,
            "p79_source_path": p79_path,
            "p79_failure_modes": [],
            "repair_items": [],
            "blocked_repair_reasons": [],
            "prerequisite_sources": [],
        }

    p79_prerequisites = _sorted_paths([str(p81["path"]), p78_path])

    if any(
        reason in {"P78_SOURCE_MISSING", "P78_STATUS_NOT_COMPUTABLE"}
        for reason in p81_reasons
    ):
        strategy = (
            "REGENERATE_P78_EXECUTION_PLAN_FIRST"
            if "P78_SOURCE_MISSING" in p81_reasons
            else "REPAIR_P78_SOURCE_FIRST"
        )
        return {
            "p79_source_repair_plan_status": "P79_REPAIR_PLAN_BLOCKED_BY_P78",
            "recommended_next_lane": (
                "P83_TEMPORAL_CONTINUITY_P78_EXECUTION_PLAN_SOURCE_REPAIR_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P78 remains the upstream blocker for P79; repair or regenerate P78 "
                "before planning any P79 repair."
            ),
            "p79_source_status": p79_status,
            "p79_source_path": p79_path,
            "p79_failure_modes": ["P78_SOURCE_BLOCKING_P79"],
            "repair_items": [
                _build_repair_item(
                    repair_item_id="repair_item_p78_001",
                    lane="P78",
                    path=_source_item_path(p78_item, p78_path),
                    observed=_source_item_bool(
                        p78_item, "observed", p78_path != "NOT_COMPUTABLE"
                    ),
                    readable=_source_item_bool(p78_item, "readable", True),
                    malformed_json=_source_item_bool(p78_item, "malformed_json", False),
                    status_field=_source_item_str(
                        p78_item, "status_field", "execution_plan_status"
                    ),
                    status_value=_source_item_str(p78_item, "status_value", p78_status),
                    failure_mode="P78_SOURCE_BLOCKING_P79",
                    repair_strategy=strategy,
                    prerequisite_paths=[str(p81["path"])],
                    blocking_reason=(
                        "P78_SOURCE_MISSING"
                        if "P78_SOURCE_MISSING" in p81_reasons
                        else "P78_STATUS_NOT_COMPUTABLE"
                    ),
                )
            ],
            "blocked_repair_reasons": _ordered_unique(p81_reasons, _REASON_ORDER_INDEX),
            "prerequisite_sources": _sorted_paths([str(p81["path"])]),
        }

    if "P79_SOURCE_MISSING" in p81_reasons:
        return {
            "p79_source_repair_plan_status": "P79_REPAIR_PLAN_READY",
            "recommended_next_lane": (
                "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate source is missing; create a deterministic "
                "regeneration plan before attempting P80 or P81 follow-on work."
            ),
            "p79_source_status": p79_status,
            "p79_source_path": p79_path,
            "p79_failure_modes": ["P79_SOURCE_MISSING"],
            "repair_items": [
                _build_repair_item(
                    repair_item_id="repair_item_p79_001",
                    lane="P79",
                    path=_source_item_path(p79_item, p79_path),
                    observed=_source_item_bool(p79_item, "observed", False),
                    readable=_source_item_bool(p79_item, "readable", False),
                    malformed_json=_source_item_bool(p79_item, "malformed_json", False),
                    status_field=_source_item_str(
                        p79_item, "status_field", "authorization_gate_status"
                    ),
                    status_value=_source_item_str(p79_item, "status_value", p79_status),
                    failure_mode="P79_SOURCE_MISSING",
                    repair_strategy="REGENERATE_P79_AUTHORIZATION_GATE",
                    prerequisite_paths=p79_prerequisites,
                    blocking_reason="P79_SOURCE_MISSING",
                )
            ],
            "blocked_repair_reasons": ["P79_SOURCE_MISSING"],
            "prerequisite_sources": p79_prerequisites,
        }

    if any(
        reason in {"P79_SOURCE_UNREADABLE", "P79_SOURCE_MALFORMED_JSON"}
        for reason in p81_reasons
    ):
        blocking_reason = (
            "P79_SOURCE_UNREADABLE"
            if "P79_SOURCE_UNREADABLE" in p81_reasons
            else "P79_SOURCE_MALFORMED_JSON"
        )
        failure_mode = (
            "P79_SOURCE_UNREADABLE"
            if "P79_SOURCE_UNREADABLE" in p81_reasons
            else "P79_SOURCE_MALFORMED_JSON"
        )
        return {
            "p79_source_repair_plan_status": "P79_REPAIR_PLAN_READY",
            "recommended_next_lane": (
                "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 source is present but unreadable or malformed; define a governed "
                "source repair execution plan before any regeneration work."
            ),
            "p79_source_status": p79_status,
            "p79_source_path": p79_path,
            "p79_failure_modes": [failure_mode],
            "repair_items": [
                _build_repair_item(
                    repair_item_id="repair_item_p79_001",
                    lane="P79",
                    path=_source_item_path(p79_item, p79_path),
                    observed=_source_item_bool(p79_item, "observed", True),
                    readable=_source_item_bool(
                        p79_item, "readable", blocking_reason != "P79_SOURCE_UNREADABLE"
                    ),
                    malformed_json=_source_item_bool(
                        p79_item,
                        "malformed_json",
                        blocking_reason == "P79_SOURCE_MALFORMED_JSON",
                    ),
                    status_field=_source_item_str(
                        p79_item, "status_field", "authorization_gate_status"
                    ),
                    status_value=_source_item_str(p79_item, "status_value", p79_status),
                    failure_mode=failure_mode,
                    repair_strategy="REPAIR_P79_SOURCE_SCHEMA_OR_STATUS",
                    prerequisite_paths=p79_prerequisites,
                    blocking_reason=blocking_reason,
                )
            ],
            "blocked_repair_reasons": [blocking_reason],
            "prerequisite_sources": p79_prerequisites,
        }

    if "P79_STATUS_NOT_COMPUTABLE" in p81_reasons:
        return {
            "p79_source_repair_plan_status": "P79_REPAIR_PLAN_READY",
            "recommended_next_lane": (
                "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_STATUS_REPAIR_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 source is readable but its authorization gate status is "
                "NOT_COMPUTABLE; a status repair plan is required before P80 reruns."
            ),
            "p79_source_status": p79_status,
            "p79_source_path": p79_path,
            "p79_failure_modes": ["P79_STATUS_NOT_COMPUTABLE"],
            "repair_items": [
                _build_repair_item(
                    repair_item_id="repair_item_p79_001",
                    lane="P79",
                    path=_source_item_path(p79_item, p79_path),
                    observed=_source_item_bool(p79_item, "observed", True),
                    readable=_source_item_bool(p79_item, "readable", True),
                    malformed_json=_source_item_bool(p79_item, "malformed_json", False),
                    status_field=_source_item_str(
                        p79_item, "status_field", "authorization_gate_status"
                    ),
                    status_value=_source_item_str(p79_item, "status_value", p79_status),
                    failure_mode="P79_STATUS_NOT_COMPUTABLE",
                    repair_strategy="REPAIR_P79_SOURCE_SCHEMA_OR_STATUS",
                    prerequisite_paths=p79_prerequisites,
                    blocking_reason="P79_STATUS_NOT_COMPUTABLE",
                )
            ],
            "blocked_repair_reasons": ["P79_STATUS_NOT_COMPUTABLE"],
            "prerequisite_sources": p79_prerequisites,
        }

    if "P79_NOT_AUTHORIZATION_ELIGIBLE" in p81_reasons:
        failure_modes = _p79_failure_modes(p81_reasons, fallback_not_computable=False)
        return {
            "p79_source_repair_plan_status": "P79_REPAIR_PLAN_READY",
            "recommended_next_lane": (
                "P83_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_ELIGIBILITY_REPAIR_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 is present but not authorization-eligible; an eligibility repair "
                "plan is required before any downstream regeneration."
            ),
            "p79_source_status": p79_status,
            "p79_source_path": p79_path,
            "p79_failure_modes": failure_modes,
            "repair_items": [
                _build_repair_item(
                    repair_item_id="repair_item_p79_001",
                    lane="P79",
                    path=_source_item_path(p79_item, p79_path),
                    observed=_source_item_bool(p79_item, "observed", True),
                    readable=_source_item_bool(p79_item, "readable", True),
                    malformed_json=_source_item_bool(p79_item, "malformed_json", False),
                    status_field=_source_item_str(
                        p79_item, "status_field", "authorization_gate_status"
                    ),
                    status_value=_source_item_str(p79_item, "status_value", p79_status),
                    failure_mode="P79_NOT_AUTHORIZATION_ELIGIBLE",
                    repair_strategy="REPAIR_P79_SOURCE_SCHEMA_OR_STATUS",
                    prerequisite_paths=p79_prerequisites,
                    blocking_reason="P79_NOT_AUTHORIZATION_ELIGIBLE",
                )
            ],
            "blocked_repair_reasons": _ordered_unique(p81_reasons, _REASON_ORDER_INDEX),
            "prerequisite_sources": p79_prerequisites,
        }

    failure_modes = _p79_failure_modes(p81_reasons, fallback_not_computable=True)
    return {
        "p79_source_repair_plan_status": "NOT_COMPUTABLE",
        "recommended_next_lane": "P81_SOURCE_STATUS_AUDIT_REGENERATION",
        "recommended_next_lane_reason": (
            "P81 indicates a weak or inconsistent source chain without a stable P79 "
            "repair route; regenerate the P81 audit first."
        ),
        "p79_source_status": p79_status,
        "p79_source_path": p79_path,
        "p79_failure_modes": failure_modes,
        "repair_items": [
            _build_repair_item(
                repair_item_id="repair_item_p79_001",
                lane="P79",
                path=_source_item_path(p79_item, p79_path),
                observed=_source_item_bool(p79_item, "observed", p79_path != "NOT_COMPUTABLE"),
                readable=_source_item_bool(p79_item, "readable", True),
                malformed_json=_source_item_bool(p79_item, "malformed_json", False),
                status_field=_source_item_str(
                    p79_item, "status_field", "authorization_gate_status"
                ),
                status_value=_source_item_str(p79_item, "status_value", p79_status),
                failure_mode=failure_modes[0],
                repair_strategy="NOT_COMPUTABLE",
                prerequisite_paths=_sorted_paths([str(p81["path"])]),
                blocking_reason=(
                    _ordered_unique(p81_reasons or ["NOT_COMPUTABLE"], _REASON_ORDER_INDEX)[0]
                ),
            )
        ],
        "blocked_repair_reasons": _ordered_unique(
            p81_reasons or ["NOT_COMPUTABLE"], _REASON_ORDER_INDEX
        ),
        "prerequisite_sources": _sorted_paths([str(p81["path"])]),
    }


def build_temporal_continuity_p79_authorization_gate_source_repair_plan(
    *,
    repo_root: str | Path = ".",
    source_p81_audit_path: str = SOURCE_P81_AUDIT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p81 = _observe_p81(root=root, rel_path=source_p81_audit_path)

    p81_payload = p81.get("payload")
    if not isinstance(p81_payload, dict):
        p81_payload = {}

    p79_source_path = str(p81_payload.get("source_p79_path", "NOT_COMPUTABLE"))
    p79_source_status = str(p81_payload.get("source_p79_status", "NOT_COMPUTABLE"))

    if not p81["observed"]:
        classification = _build_status_not_computable_packet(
            p81=p81,
            p79_source_path=p79_source_path,
            p79_source_status=p79_source_status,
            failure_mode="NOT_COMPUTABLE",
            blocking_reason="P81_SOURCE_MISSING",
            recommended_next_lane_reason=(
                "P81 source-status audit artifact is missing; regenerate P81 before "
                "deriving any P79 source repair plan."
            ),
        )
    elif not p81["readable"]:
        classification = _build_status_not_computable_packet(
            p81=p81,
            p79_source_path=p79_source_path,
            p79_source_status=p79_source_status,
            failure_mode="NOT_COMPUTABLE",
            blocking_reason="P81_SOURCE_UNREADABLE",
            recommended_next_lane_reason=(
                "P81 source-status audit artifact is unreadable; regenerate P81 before "
                "deriving any P79 source repair plan."
            ),
        )
    elif p81["malformed_json"]:
        classification = _build_status_not_computable_packet(
            p81=p81,
            p79_source_path=p79_source_path,
            p79_source_status=p79_source_status,
            failure_mode="NOT_COMPUTABLE",
            blocking_reason="P81_SOURCE_MALFORMED_JSON",
            recommended_next_lane_reason=(
                "P81 source-status audit artifact is malformed JSON; regenerate P81 "
                "before deriving any P79 source repair plan."
            ),
        )
    else:
        p81_reasons = _ordered_unique(
            _source_payload_list(p81_payload, "not_computable_reasons"),
            _REASON_ORDER_INDEX,
        )
        classification = _classify_packet(
            p81=p81,
            p81_payload=p81_payload,
            p78_item=_find_source_chain_item(p81_payload, "P78"),
            p79_item=_find_source_chain_item(p81_payload, "P79"),
            p81_reasons=p81_reasons,
        )

    repair_items = sorted(
        classification["repair_items"],
        key=lambda item: (
            str(item["repair_item_id"]),
            str(item["lane"]),
            str(item["path"]),
        ),
    )
    p79_failure_modes = _ordered_unique(
        [str(item) for item in classification["p79_failure_modes"]],
        _FAILURE_MODE_ORDER_INDEX,
    )
    blocked_repair_reasons = _ordered_unique(
        [str(item) for item in classification["blocked_repair_reasons"]],
        _REASON_ORDER_INDEX,
    )
    prerequisite_sources = _sorted_paths(
        [str(item) for item in classification["prerequisite_sources"]]
        + [
            prerequisite
            for item in repair_items
            for prerequisite in _as_str_list(item.get("prerequisite_paths"))
        ]
    )

    p81_payload_dict = p81_payload if isinstance(p81_payload, dict) else {}
    degraded_evidence_inputs = _source_payload_list(
        p81_payload_dict, "degraded_evidence_inputs"
    )
    inherited_blockers = _source_payload_list(p81_payload_dict, "inherited_blockers")
    inherited_drift_flags = _source_payload_list(
        p81_payload_dict, "inherited_drift_flags"
    )
    semantic_overlap_flags = _source_payload_list(
        p81_payload_dict, "semantic_overlap_flags"
    )
    repair_strategies = _ordered_unique(
        [str(item["repair_strategy"]) for item in repair_items],
        _REPAIR_STRATEGY_ORDER_INDEX,
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "source_repair_plan_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "repair_execution_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "spine_implementation_authority": False,
        "source_p81_audit_path": source_p81_audit_path,
        "source_p81_audit_observed": p81["observed"],
        "source_p81_audit_readable": p81["readable"],
        "source_p81_audit_hash": p81["file_hash"],
        "source_p81_chain_status": p81["source_chain_status"],
        "source_p81_recommended_next_lane": p81["recommended_next_lane"],
        "p79_source_repair_plan_status": classification["p79_source_repair_plan_status"],
        "p79_source_status": classification["p79_source_status"],
        "p79_source_path": classification["p79_source_path"],
        "p79_failure_modes": p79_failure_modes,
        "repair_items": repair_items,
        "blocked_repair_reasons": blocked_repair_reasons,
        "prerequisite_sources": prerequisite_sources,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "repair_strategy_summary": {
            "source_chain_status": p81["source_chain_status"],
            "repair_items_count": len(repair_items),
            "repair_strategies": repair_strategies,
            "blocked_repair_reasons_count": len(blocked_repair_reasons),
            "prerequisite_sources_count": len(prerequisite_sources),
        },
        "recommended_next_lane": classification["recommended_next_lane"],
        "recommended_next_lane_reason": classification["recommended_next_lane_reason"],
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_p79_authorization_gate_source_repair_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
