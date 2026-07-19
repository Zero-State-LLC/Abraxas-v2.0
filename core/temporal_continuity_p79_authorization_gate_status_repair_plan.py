from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP79AuthorizationGateStatusRepairPlan.v1"
SOURCE_P82_REPAIR_PLAN_PATH = (
    "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json"
)

_DENIED_AUTHORITY: tuple[str, ...] = (
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
_FAILURE_MODE_ORDER_INDEX = {mode: i for i, mode in enumerate(_FAILURE_MODE_ORDER)}

_STATUS_REPAIR_STRATEGY_ORDER = (
    "NORMALIZE_P79_STATUS_FIELD",
    "RECOMPUTE_P79_FROM_P78_PLAN",
    "REPAIR_AUTHORIZATION_ELIGIBILITY_DERIVATION",
    "REGENERATE_P79_FIRST",
    "REPAIR_P79_SOURCE_FIRST",
    "NO_STATUS_REPAIR_REQUIRED",
    "NOT_COMPUTABLE",
)
_STATUS_REPAIR_STRATEGY_ORDER_INDEX = {
    s: i for i, s in enumerate(_STATUS_REPAIR_STRATEGY_ORDER)
}

# Expected P79 authorization_gate_status given P78 execution_plan_status
# when P79 is in a "ready" state (all source inputs present and computable)
_P78_TO_P79_EXPECTED_IF_READY: dict[str, str] = {
    "EXECUTION_PLAN_READY": "AUTHORIZATION_ELIGIBLE",
    "EXECUTION_PLAN_BLOCKED": "AUTHORIZATION_BLOCKED",
    "EXECUTION_PLAN_NOT_REQUIRED": "AUTHORIZATION_NOT_REQUIRED",
    "NOT_COMPUTABLE": "NOT_COMPUTABLE",
}

# Expected P79 authorization_gate_status when P79 source is present but blocked
_P78_TO_P79_EXPECTED_IF_BLOCKED: dict[str, str] = {
    "EXECUTION_PLAN_READY": "NOT_COMPUTABLE",
    "EXECUTION_PLAN_BLOCKED": "AUTHORIZATION_BLOCKED",
    "EXECUTION_PLAN_NOT_REQUIRED": "AUTHORIZATION_NOT_REQUIRED",
    "NOT_COMPUTABLE": "NOT_COMPUTABLE",
}

_RERUN_SEQUENCE = [
    "Run python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_execution_plan.py",
    "Run python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_gate.py",
    "Run python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py",
    "Run python scripts/temporal/run_temporal_continuity_authorization_record_plan_source_status_audit.py",
]


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float, bool))]


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _ordered_unique(
    values: list[str], order_index: dict[str, int], *, fallback: int = 10_000
) -> list[str]:
    unique = list(dict.fromkeys(values))
    return sorted(unique, key=lambda v: order_index.get(v, fallback))


def _sorted_paths(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(v for v in values if v))


def _observe_p82(*, root: Path, rel_path: str) -> dict[str, Any]:
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    source_repair_plan_status = "NOT_COMPUTABLE"
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
                source_repair_plan_status = str(
                    parsed.get("p79_source_repair_plan_status", "NOT_COMPUTABLE")
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
        "source_repair_plan_status": source_repair_plan_status,
        "recommended_next_lane": recommended_next_lane,
        "payload": payload,
    }


def _p78_status_from_p82(p82_payload: dict[str, Any] | None) -> str:
    """Return the P78 execution_plan_status observed in P82's repair_items, if any."""
    if not isinstance(p82_payload, dict):
        return "NOT_COMPUTABLE"
    for item in _as_dict_list(p82_payload.get("repair_items")):
        if str(item.get("lane", "")) == "P78":
            return str(item.get("status_value", "NOT_COMPUTABLE"))
    return "NOT_COMPUTABLE"


def _build_corrected_status_relationship(
    *,
    source_p78_status: str,
    repair_plan_ready: bool,
) -> dict[str, Any]:
    expected_if_ready = _P78_TO_P79_EXPECTED_IF_READY.get(
        source_p78_status, "NOT_COMPUTABLE"
    )
    expected_if_blocked = _P78_TO_P79_EXPECTED_IF_BLOCKED.get(
        source_p78_status, "NOT_COMPUTABLE"
    )
    expected_p80_after_repair = (
        "AUTHORIZATION_RECORD_PLAN_READY"
        if expected_if_ready == "AUTHORIZATION_ELIGIBLE"
        else "NOT_COMPUTABLE"
    )
    return {
        "source_p78_status": source_p78_status,
        "expected_p79_status_if_ready": expected_if_ready,
        "expected_p79_status_if_blocked": expected_if_blocked,
        "expected_p80_status_after_p79_repair": expected_p80_after_repair,
        "rerun_sequence": _RERUN_SEQUENCE if repair_plan_ready else [],
    }


def _build_status_field_expectations(
    *,
    p79_source_status: str,
) -> list[dict[str, Any]]:
    satisfied = p79_source_status in {
        "AUTHORIZATION_ELIGIBLE",
        "AUTHORIZATION_BLOCKED",
        "AUTHORIZATION_NOT_REQUIRED",
    }
    return [
        {
            "allowed_values": [
                "AUTHORIZATION_ELIGIBLE",
                "AUTHORIZATION_BLOCKED",
                "AUTHORIZATION_NOT_REQUIRED",
                "NOT_COMPUTABLE",
            ],
            "current_value": p79_source_status,
            "expected_relationship": (
                "P79 authorization_gate_status must derive from P78 execution_plan_status "
                "and the allowlist of future execution commands"
            ),
            "field": "authorization_gate_status",
            "satisfied": satisfied,
        }
    ]


def _build_status_repair_item(
    *,
    status_repair_item_id: str,
    lane: str,
    path: str,
    status_field: str,
    observed_status_value: str,
    expected_status_values: list[str],
    failure_mode: str,
    repair_strategy: str,
    prerequisite_paths: list[str],
    blocking_reason: str,
) -> dict[str, Any]:
    return {
        "blocking_reason": blocking_reason,
        "expected_status_values": expected_status_values,
        "failure_mode": failure_mode,
        "lane": lane,
        "observed_status_value": observed_status_value,
        "path": path,
        "prerequisite_paths": _sorted_paths(prerequisite_paths),
        "repair_execution_allowed": False,
        "repair_strategy": repair_strategy,
        "status_field": status_field,
        "status_repair_item_id": status_repair_item_id,
    }


def _p82_blocked_item(*, p82_path: str, p82_status: str, blocking_reason: str) -> dict[str, Any]:
    return _build_status_repair_item(
        status_repair_item_id="status_repair_item_p82_001",
        lane="P82",
        path=p82_path,
        status_field="p79_source_repair_plan_status",
        observed_status_value=p82_status,
        expected_status_values=["P79_REPAIR_PLAN_READY", "P79_REPAIR_NOT_REQUIRED"],
        failure_mode="NOT_COMPUTABLE",
        repair_strategy="NOT_COMPUTABLE",
        prerequisite_paths=[],
        blocking_reason=blocking_reason,
    )


def _classify_packet(
    *,
    p82: dict[str, Any],
    p82_payload: dict[str, Any],
) -> dict[str, Any]:
    p82_status = str(p82["source_repair_plan_status"])
    p79_source_path = str(p82_payload.get("p79_source_path", "NOT_COMPUTABLE"))
    p79_source_status = str(p82_payload.get("p79_source_status", "NOT_COMPUTABLE"))
    p79_failure_modes = [
        str(fm) for fm in _as_str_list(p82_payload.get("p79_failure_modes", []))
    ]
    p82_prereqs = _as_str_list(p82_payload.get("prerequisite_sources", []))
    p82_path = str(p82["path"])

    # Rule 2: P82 status is NOT_COMPUTABLE
    if p82_status == "NOT_COMPUTABLE":
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_BLOCKED_BY_P82",
            "recommended_next_lane": "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P82 source repair plan status is NOT_COMPUTABLE; "
                "regenerate P82 before deriving any P79 status repair plan."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": [],
            "status_repair_items": [
                _p82_blocked_item(
                    p82_path=p82_path,
                    p82_status=p82_status,
                    blocking_reason="P82_NOT_COMPUTABLE",
                )
            ],
            "blocked_status_repair_reasons": ["P82_NOT_COMPUTABLE"],
            "prerequisite_sources": [],
        }

    # Rule 3: P82 status is P79_REPAIR_PLAN_BLOCKED_BY_P78
    if p82_status == "P79_REPAIR_PLAN_BLOCKED_BY_P78":
        p78_path = str(
            next(
                (
                    item.get("path", "NOT_COMPUTABLE")
                    for item in _as_dict_list(p82_payload.get("repair_items"))
                    if str(item.get("lane", "")) == "P78"
                ),
                "NOT_COMPUTABLE",
            )
        )
        p78_status = _p78_status_from_p82(p82_payload)
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_BLOCKED_BY_P82",
            "recommended_next_lane": (
                "P84_TEMPORAL_CONTINUITY_P78_EXECUTION_PLAN_SOURCE_REPAIR_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P82 indicates P79 repair is blocked by P78; "
                "repair P78 execution plan source before addressing P79 status."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": ["P78_SOURCE_BLOCKING_P79"],
            "status_repair_items": [
                _build_status_repair_item(
                    status_repair_item_id="status_repair_item_p78_001",
                    lane="P78",
                    path=p78_path,
                    status_field="execution_plan_status",
                    observed_status_value=p78_status,
                    expected_status_values=["EXECUTION_PLAN_READY"],
                    failure_mode="P78_SOURCE_BLOCKING_P79",
                    repair_strategy="REPAIR_P79_SOURCE_FIRST",
                    prerequisite_paths=[p82_path],
                    blocking_reason="P82_BLOCKED_BY_P78",
                )
            ],
            "blocked_status_repair_reasons": ["P82_BLOCKED_BY_P78"],
            "prerequisite_sources": _sorted_paths([p82_path] + p82_prereqs),
        }

    # Rules 4-7: failure mode checks (highest priority when failure modes are present)
    prerequisites = _sorted_paths([p82_path] + p82_prereqs)

    # Rule 4: P79_STATUS_NOT_COMPUTABLE
    if "P79_STATUS_NOT_COMPUTABLE" in p79_failure_modes:
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_PLAN_READY",
            "recommended_next_lane": (
                "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_STATUS_REPAIR_EXECUTION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate status is NOT_COMPUTABLE; "
                "a status repair execution plan is required before P80 reruns."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": _ordered_unique(
                [fm for fm in p79_failure_modes if fm], _FAILURE_MODE_ORDER_INDEX
            ),
            "status_repair_items": [
                _build_status_repair_item(
                    status_repair_item_id="status_repair_item_p79_001",
                    lane="P79",
                    path=p79_source_path,
                    status_field="authorization_gate_status",
                    observed_status_value=p79_source_status,
                    expected_status_values=[
                        "AUTHORIZATION_ELIGIBLE",
                        "AUTHORIZATION_BLOCKED",
                        "AUTHORIZATION_NOT_REQUIRED",
                    ],
                    failure_mode="P79_STATUS_NOT_COMPUTABLE",
                    repair_strategy="NORMALIZE_P79_STATUS_FIELD",
                    prerequisite_paths=prerequisites,
                    blocking_reason="P79_STATUS_NOT_COMPUTABLE",
                )
            ],
            "blocked_status_repair_reasons": ["P79_STATUS_NOT_COMPUTABLE"],
            "prerequisite_sources": prerequisites,
        }

    # Rule 5: P79_NOT_AUTHORIZATION_ELIGIBLE
    if "P79_NOT_AUTHORIZATION_ELIGIBLE" in p79_failure_modes:
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_PLAN_READY",
            "recommended_next_lane": (
                "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_ELIGIBILITY_REPAIR_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 is present but not authorization-eligible; "
                "an eligibility repair plan is required before any downstream reruns."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": _ordered_unique(
                [fm for fm in p79_failure_modes if fm], _FAILURE_MODE_ORDER_INDEX
            ),
            "status_repair_items": [
                _build_status_repair_item(
                    status_repair_item_id="status_repair_item_p79_001",
                    lane="P79",
                    path=p79_source_path,
                    status_field="authorization_gate_status",
                    observed_status_value=p79_source_status,
                    expected_status_values=["AUTHORIZATION_ELIGIBLE"],
                    failure_mode="P79_NOT_AUTHORIZATION_ELIGIBLE",
                    repair_strategy="REPAIR_AUTHORIZATION_ELIGIBILITY_DERIVATION",
                    prerequisite_paths=prerequisites,
                    blocking_reason="P79_NOT_AUTHORIZATION_ELIGIBLE",
                )
            ],
            "blocked_status_repair_reasons": ["P79_NOT_AUTHORIZATION_ELIGIBLE"],
            "prerequisite_sources": prerequisites,
        }

    # Rule 6: P79_SOURCE_MISSING
    if "P79_SOURCE_MISSING" in p79_failure_modes:
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_BLOCKED_BY_P82",
            "recommended_next_lane": (
                "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate source is missing; "
                "regenerate P79 before any status repair work."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": ["P79_SOURCE_MISSING"],
            "status_repair_items": [
                _build_status_repair_item(
                    status_repair_item_id="status_repair_item_p79_001",
                    lane="P79",
                    path=p79_source_path,
                    status_field="authorization_gate_status",
                    observed_status_value=p79_source_status,
                    expected_status_values=["AUTHORIZATION_ELIGIBLE"],
                    failure_mode="P79_SOURCE_MISSING",
                    repair_strategy="REGENERATE_P79_FIRST",
                    prerequisite_paths=prerequisites,
                    blocking_reason="P79_SOURCE_MISSING",
                )
            ],
            "blocked_status_repair_reasons": ["P79_SOURCE_MISSING"],
            "prerequisite_sources": prerequisites,
        }

    # Rule 7: P79_SOURCE_UNREADABLE or P79_SOURCE_MALFORMED_JSON
    if (
        "P79_SOURCE_UNREADABLE" in p79_failure_modes
        or "P79_SOURCE_MALFORMED_JSON" in p79_failure_modes
    ):
        blocking_reason = (
            "P79_SOURCE_UNREADABLE"
            if "P79_SOURCE_UNREADABLE" in p79_failure_modes
            else "P79_SOURCE_MALFORMED_JSON"
        )
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_BLOCKED_BY_P82",
            "recommended_next_lane": (
                "P84_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_SOURCE_REPAIR_EXECUTION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 source is present but unreadable or malformed; "
                "a source repair execution plan is required before any status repair."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": _ordered_unique(
                [fm for fm in p79_failure_modes if fm], _FAILURE_MODE_ORDER_INDEX
            ),
            "status_repair_items": [
                _build_status_repair_item(
                    status_repair_item_id="status_repair_item_p79_001",
                    lane="P79",
                    path=p79_source_path,
                    status_field="authorization_gate_status",
                    observed_status_value=p79_source_status,
                    expected_status_values=["AUTHORIZATION_ELIGIBLE"],
                    failure_mode=blocking_reason,
                    repair_strategy="REPAIR_P79_SOURCE_FIRST",
                    prerequisite_paths=prerequisites,
                    blocking_reason=blocking_reason,
                )
            ],
            "blocked_status_repair_reasons": [blocking_reason],
            "prerequisite_sources": prerequisites,
        }

    # Rule 8: P79_REPAIR_NOT_REQUIRED
    if p82_status == "P79_REPAIR_NOT_REQUIRED":
        return {
            "p79_status_repair_plan_status": "P79_STATUS_REPAIR_NOT_REQUIRED",
            "recommended_next_lane": str(p82["recommended_next_lane"]),
            "recommended_next_lane_reason": (
                "P82 indicates no P79 source repair is required; "
                f"preserving P82 recommended lane ({p82['recommended_next_lane']})."
            ),
            "p79_source_path": p79_source_path,
            "p79_source_status": p79_source_status,
            "p79_failure_modes": [],
            "status_repair_items": [],
            "blocked_status_repair_reasons": [],
            "prerequisite_sources": [],
        }

    # Rule 9: Otherwise NOT_COMPUTABLE
    fallback_failure_modes = _ordered_unique(
        [fm for fm in p79_failure_modes if fm], _FAILURE_MODE_ORDER_INDEX
    ) or ["NOT_COMPUTABLE"]
    return {
        "p79_status_repair_plan_status": "NOT_COMPUTABLE",
        "recommended_next_lane": "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P82 source repair plan has an unrecognized status or failure modes; "
            "regenerate P82 before deriving any P79 status repair plan."
        ),
        "p79_source_path": p79_source_path,
        "p79_source_status": p79_source_status,
        "p79_failure_modes": fallback_failure_modes,
        "status_repair_items": [
            _p82_blocked_item(
                p82_path=p82_path,
                p82_status=p82_status,
                blocking_reason="P82_STATUS_UNRECOGNIZED",
            )
        ],
        "blocked_status_repair_reasons": ["P82_STATUS_UNRECOGNIZED"],
        "prerequisite_sources": [],
    }


def build_temporal_continuity_p79_authorization_gate_status_repair_plan(
    *,
    repo_root: str | Path = ".",
    source_p82_repair_plan_path: str = SOURCE_P82_REPAIR_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p82 = _observe_p82(root=root, rel_path=source_p82_repair_plan_path)

    p82_payload: dict[str, Any] = {}
    raw_payload = p82.get("payload")
    if isinstance(raw_payload, dict):
        p82_payload = raw_payload

    # Rule 1: P82 missing/unreadable/malformed
    if not p82["observed"]:
        blocking_reason = "P82_SOURCE_MISSING"
        reason_text = (
            "P82 source repair plan artifact is missing; "
            "regenerate P82 before deriving any P79 status repair plan."
        )
        classification: dict[str, Any] = {
            "p79_status_repair_plan_status": "NOT_COMPUTABLE",
            "recommended_next_lane": "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": reason_text,
            "p79_source_path": "NOT_COMPUTABLE",
            "p79_source_status": "NOT_COMPUTABLE",
            "p79_failure_modes": [],
            "status_repair_items": [
                _p82_blocked_item(
                    p82_path=str(p82["path"]),
                    p82_status="NOT_COMPUTABLE",
                    blocking_reason=blocking_reason,
                )
            ],
            "blocked_status_repair_reasons": [blocking_reason],
            "prerequisite_sources": [],
        }
    elif not p82["readable"]:
        blocking_reason = "P82_SOURCE_UNREADABLE"
        reason_text = (
            "P82 source repair plan artifact is unreadable; "
            "regenerate P82 before deriving any P79 status repair plan."
        )
        classification = {
            "p79_status_repair_plan_status": "NOT_COMPUTABLE",
            "recommended_next_lane": "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": reason_text,
            "p79_source_path": "NOT_COMPUTABLE",
            "p79_source_status": "NOT_COMPUTABLE",
            "p79_failure_modes": [],
            "status_repair_items": [
                _p82_blocked_item(
                    p82_path=str(p82["path"]),
                    p82_status="NOT_COMPUTABLE",
                    blocking_reason=blocking_reason,
                )
            ],
            "blocked_status_repair_reasons": [blocking_reason],
            "prerequisite_sources": [],
        }
    elif p82["malformed_json"]:
        blocking_reason = "P82_SOURCE_MALFORMED_JSON"
        reason_text = (
            "P82 source repair plan artifact is malformed JSON; "
            "regenerate P82 before deriving any P79 status repair plan."
        )
        classification = {
            "p79_status_repair_plan_status": "NOT_COMPUTABLE",
            "recommended_next_lane": "P82_P79_SOURCE_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": reason_text,
            "p79_source_path": "NOT_COMPUTABLE",
            "p79_source_status": "NOT_COMPUTABLE",
            "p79_failure_modes": [],
            "status_repair_items": [
                _p82_blocked_item(
                    p82_path=str(p82["path"]),
                    p82_status="NOT_COMPUTABLE",
                    blocking_reason=blocking_reason,
                )
            ],
            "blocked_status_repair_reasons": [blocking_reason],
            "prerequisite_sources": [],
        }
    else:
        classification = _classify_packet(p82=p82, p82_payload=p82_payload)

    p79_source_path = str(classification["p79_source_path"])
    p79_source_status = str(classification["p79_source_status"])
    p79_failure_modes = _ordered_unique(
        [str(fm) for fm in classification["p79_failure_modes"]],
        _FAILURE_MODE_ORDER_INDEX,
    )
    status_repair_items = sorted(
        classification["status_repair_items"],
        key=lambda item: (
            str(item["status_repair_item_id"]),
            str(item["lane"]),
            str(item["path"]),
            str(item["status_field"]),
        ),
    )
    blocked_status_repair_reasons = list(
        dict.fromkeys(str(r) for r in classification["blocked_status_repair_reasons"])
    )
    prerequisite_sources = _sorted_paths(
        [str(s) for s in classification["prerequisite_sources"]]
        + [
            p
            for item in status_repair_items
            for p in _as_str_list(item.get("prerequisite_paths", []))
        ]
    )

    # Inherit from P82 payload
    degraded_evidence_inputs = _as_str_list(p82_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(p82_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(p82_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(p82_payload.get("semantic_overlap_flags"))

    status_repair_strategies = _ordered_unique(
        [str(item["repair_strategy"]) for item in status_repair_items],
        _STATUS_REPAIR_STRATEGY_ORDER_INDEX,
    )

    p79_status_repair_plan_status = str(classification["p79_status_repair_plan_status"])
    repair_plan_ready = p79_status_repair_plan_status == "P79_STATUS_REPAIR_PLAN_READY"

    source_p78_status = _p78_status_from_p82(p82_payload)
    corrected_status_relationship = _build_corrected_status_relationship(
        source_p78_status=source_p78_status,
        repair_plan_ready=repair_plan_ready,
    )
    status_field_expectations = _build_status_field_expectations(
        p79_source_status=p79_source_status,
    )

    packet_base: dict[str, Any] = {
        "artifact_regeneration_authority": False,
        "artifact_type": ARTIFACT_TYPE,
        "audit_only": True,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "blocked_status_repair_reasons": blocked_status_repair_reasons,
        "canon_promotion": False,
        "canonical_status": "ADVISORY_ONLY",
        "corrected_status_relationship": corrected_status_relationship,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "denied_authority": sorted(_DENIED_AUTHORITY),
        "evidence_generation_authority": False,
        "execution_authority": False,
        "forecast_influence": False,
        "generator_execution_authority": False,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "p79_failure_modes": p79_failure_modes,
        "p79_source_path": p79_source_path,
        "p79_source_status": p79_source_status,
        "p79_status_repair_plan_status": p79_status_repair_plan_status,
        "prerequisite_sources": prerequisite_sources,
        "production_activation": False,
        "projection_only": True,
        "recommended_next_lane": classification["recommended_next_lane"],
        "recommended_next_lane_reason": classification["recommended_next_lane_reason"],
        "repair_authority": False,
        "repair_execution_authority": False,
        "restoration_execution_authority": False,
        "runtime_authority": False,
        "scheduler_mutation": False,
        "semantic_overlap_flags": semantic_overlap_flags,
        "source_p82_recommended_next_lane": p82["recommended_next_lane"],
        "source_p82_repair_plan_hash": p82["file_hash"],
        "source_p82_repair_plan_observed": p82["observed"],
        "source_p82_repair_plan_path": source_p82_repair_plan_path,
        "source_p82_repair_plan_readable": p82["readable"],
        "source_p82_repair_plan_status": p82["source_repair_plan_status"],
        "spine_implementation_authority": False,
        "status_field_expectations": status_field_expectations,
        "status_repair_items": status_repair_items,
        "status_repair_plan_only": True,
        "status_repair_strategy_summary": {
            "blocked_status_repair_reasons_count": len(blocked_status_repair_reasons),
            "p82_repair_plan_status": p82["source_repair_plan_status"],
            "prerequisite_sources_count": len(prerequisite_sources),
            "status_repair_items_count": len(status_repair_items),
            "status_repair_strategies": status_repair_strategies,
        },
        "upstream_input_generation_authority": False,
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_p79_authorization_gate_status_repair_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
