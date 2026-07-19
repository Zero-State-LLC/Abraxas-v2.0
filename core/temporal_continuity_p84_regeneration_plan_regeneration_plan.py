from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP84RegenerationPlanRegenerationPlan.v1"
SOURCE_P85_EXECUTION_PLAN_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
)
SOURCE_P84_REGENERATION_PLAN_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
)
SOURCE_P83_STATUS_PLAN_PATH = (
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
)
ALLOWED_FUTURE_RUNNER_COMMAND = (
    "python scripts/temporal/run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
)

_PLAN_STATUSES = (
    "NOT_COMPUTABLE",
    "P84_REGENERATION_PLAN_READY",
    "P84_REGENERATION_PLAN_BLOCKED",
    "P84_REGENERATION_NOT_REQUIRED",
)

_REASON_ORDER = (
    "P85_SOURCE_WEAK_OR_INCONSISTENT",
    "P85_ROUTE_DOES_NOT_REQUIRE_P84_REGENERATION",
    "P84_ALREADY_READY",
    "P83_SOURCE_WEAK_OR_INCONSISTENT",
    "P83_NOT_COMPUTABLE",
    "P85_ROUTES_TO_P84_REGENERATION",
    "P83_COMPUTABLE_AND_READY_FOR_P84_REGENERATION",
)
_REASON_ORDER_INDEX = {reason: idx for idx, reason in enumerate(_REASON_ORDER)}

_BLOCKED_REASON_ORDER = (
    "P85_SOURCE_MISSING",
    "P85_SOURCE_UNREADABLE",
    "P85_SOURCE_MALFORMED_JSON",
    "P85_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
    "P84_ALREADY_READY",
    "P83_SOURCE_MISSING",
    "P83_SOURCE_UNREADABLE",
    "P83_SOURCE_MALFORMED_JSON",
    "P83_STATUS_NOT_COMPUTABLE",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_BLOCKED_REASON_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_BLOCKED_REASON_ORDER)
}

_VALIDATION_ORDER = (
    "validation_001_p83_source_exists",
    "validation_002_p83_source_readable",
    "validation_003_p83_status_not_not_computable",
    "validation_004_future_command_exact_match",
    "validation_005_expected_output_path_exact_match",
    "validation_006_p84_exists_after_regeneration",
    "validation_007_p84_readable_after_regeneration",
    "validation_008_p84_status_not_not_computable_after_regeneration",
    "validation_009_all_authority_fields_false",
)
_VALIDATION_ORDER_INDEX = {value: idx for idx, value in enumerate(_VALIDATION_ORDER)}

_DENIED_AUTHORITY: tuple[str, ...] = (
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


def _sorted_paths(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(value for value in values if value))


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


def _validation_requirements_ready() -> list[dict[str, str]]:
    requirements = [
        {
            "validation_id": "validation_001_p83_source_exists",
            "validation_type": "source_exists",
            "path": SOURCE_P83_STATUS_PLAN_PATH,
            "required_status": "observed=true",
            "failure_action": "BLOCK_P84_REGENERATION_EXECUTION_PLANNING",
        },
        {
            "validation_id": "validation_002_p83_source_readable",
            "validation_type": "source_readable",
            "path": SOURCE_P83_STATUS_PLAN_PATH,
            "required_status": "readable=true",
            "failure_action": "BLOCK_P84_REGENERATION_EXECUTION_PLANNING",
        },
        {
            "validation_id": "validation_003_p83_status_not_not_computable",
            "validation_type": "status_not_not_computable",
            "path": SOURCE_P83_STATUS_PLAN_PATH,
            "required_status": "p79_status_repair_plan_status!=NOT_COMPUTABLE",
            "failure_action": "ROUTE_TO_P87_P83_STATUS_PLAN_REGENERATION_PLAN",
        },
        {
            "validation_id": "validation_004_future_command_exact_match",
            "validation_type": "future_command_exact_match",
            "path": "scripts/temporal/run_temporal_continuity_p80_authorization_record_plan_regeneration_plan.py",
            "required_status": ALLOWED_FUTURE_RUNNER_COMMAND,
            "failure_action": "MARK_NOT_COMPUTABLE",
        },
        {
            "validation_id": "validation_005_expected_output_path_exact_match",
            "validation_type": "expected_output_path_exact_match",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": EXPECTED_OUTPUT_PATH,
            "failure_action": "MARK_NOT_COMPUTABLE",
        },
        {
            "validation_id": "validation_006_p84_exists_after_regeneration",
            "validation_type": "post_regeneration_exists",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "observed=true",
            "failure_action": "BLOCK_DOWNSTREAM_LANES",
        },
        {
            "validation_id": "validation_007_p84_readable_after_regeneration",
            "validation_type": "post_regeneration_readable",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "readable=true",
            "failure_action": "BLOCK_DOWNSTREAM_LANES",
        },
        {
            "validation_id": "validation_008_p84_status_not_not_computable_after_regeneration",
            "validation_type": "post_regeneration_status",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "p80_regeneration_plan_status!=NOT_COMPUTABLE",
            "failure_action": "ROUTE_TO_P85_EXECUTION_PLAN_REGENERATION",
        },
        {
            "validation_id": "validation_009_all_authority_fields_false",
            "validation_type": "authority_lock_check",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "all_authority_fields=false",
            "failure_action": "FAIL_CLOSED_REPORT_AND_BLOCK",
        },
    ]
    return sorted(
        requirements,
        key=lambda item: _VALIDATION_ORDER_INDEX.get(str(item["validation_id"]), 10_000),
    )


def _classify(*, p85: dict[str, Any], p84: dict[str, Any], p83: dict[str, Any]) -> dict[str, Any]:
    p85_payload = p85.get("payload")
    p85_payload_dict = p85_payload if isinstance(p85_payload, dict) else {}
    p85_recommended_next_lane = str(
        p85_payload_dict.get("recommended_next_lane", "NOT_COMPUTABLE")
    )

    if not p85["observed"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "allowed": False,
            "reasons": ["P85_SOURCE_WEAK_OR_INCONSISTENT"],
            "blocked_reasons": ["P85_SOURCE_MISSING"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": "P85_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P85 execution plan source is missing; regenerate P85 before deriving "
                "P84 regeneration-plan regeneration planning."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [],
            "item_blocking_reason": "P85_SOURCE_MISSING",
        }

    if not p85["readable"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "allowed": False,
            "reasons": ["P85_SOURCE_WEAK_OR_INCONSISTENT"],
            "blocked_reasons": ["P85_SOURCE_UNREADABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": "P85_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P85 execution plan source is unreadable; regenerate P85 before deriving "
                "P84 regeneration-plan regeneration planning."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [],
            "item_blocking_reason": "P85_SOURCE_UNREADABLE",
        }

    if p85["malformed_json"]:
        return {
            "status": "NOT_COMPUTABLE",
            "required": False,
            "allowed": False,
            "reasons": ["P85_SOURCE_WEAK_OR_INCONSISTENT"],
            "blocked_reasons": ["P85_SOURCE_MALFORMED_JSON"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": "P85_EXECUTION_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P85 execution plan source is malformed JSON; regenerate P85 before "
                "deriving P84 regeneration-plan regeneration planning."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [],
            "item_blocking_reason": "P85_SOURCE_MALFORMED_JSON",
        }

    if p85_recommended_next_lane != "P84_REGENERATION_PLAN_REGENERATION":
        return {
            "status": "P84_REGENERATION_NOT_REQUIRED",
            "required": False,
            "allowed": False,
            "reasons": ["P85_ROUTE_DOES_NOT_REQUIRE_P84_REGENERATION"],
            "blocked_reasons": ["P85_RECOMMENDED_NEXT_LANE_PASSTHROUGH"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": "P85_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
            "recommended_next_lane_reason": (
                "P85 recommended next lane does not route to P84 regeneration-plan "
                "regeneration; preserve pass-through routing."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [str(p85["path"])],
            "item_blocking_reason": "P85_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
        }

    if str(p84["status"]) == "P80_REGENERATION_PLAN_READY":
        return {
            "status": "P84_REGENERATION_NOT_REQUIRED",
            "required": False,
            "allowed": False,
            "reasons": ["P84_ALREADY_READY"],
            "blocked_reasons": ["P84_ALREADY_READY"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": (
                "P87_TEMPORAL_CONTINUITY_P85_REGENERATION_EXECUTION_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P84 source already reports P80_REGENERATION_PLAN_READY; additional "
                "regeneration planning is not required."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [str(p85["path"]), str(p84["path"])],
            "item_blocking_reason": "P84_ALREADY_READY",
        }

    if not p83["observed"]:
        return {
            "status": "P84_REGENERATION_PLAN_BLOCKED",
            "required": False,
            "allowed": False,
            "reasons": ["P83_SOURCE_WEAK_OR_INCONSISTENT"],
            "blocked_reasons": ["P83_SOURCE_MISSING"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": (
                "P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P83 prerequisite source is missing; regenerate P83 status planning before "
                "P84 regeneration-plan regeneration can be prepared."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [str(p85["path"]), str(p84["path"])],
            "item_blocking_reason": "P83_SOURCE_MISSING",
        }

    if not p83["readable"]:
        return {
            "status": "P84_REGENERATION_PLAN_BLOCKED",
            "required": False,
            "allowed": False,
            "reasons": ["P83_SOURCE_WEAK_OR_INCONSISTENT"],
            "blocked_reasons": ["P83_SOURCE_UNREADABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": (
                "P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P83 prerequisite source is unreadable; regenerate P83 status planning "
                "before P84 regeneration-plan regeneration can be prepared."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [str(p85["path"]), str(p84["path"])],
            "item_blocking_reason": "P83_SOURCE_UNREADABLE",
        }

    if p83["malformed_json"]:
        return {
            "status": "P84_REGENERATION_PLAN_BLOCKED",
            "required": False,
            "allowed": False,
            "reasons": ["P83_SOURCE_WEAK_OR_INCONSISTENT"],
            "blocked_reasons": ["P83_SOURCE_MALFORMED_JSON"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": (
                "P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P83 prerequisite source is malformed JSON; regenerate P83 status planning "
                "before P84 regeneration-plan regeneration can be prepared."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [str(p85["path"]), str(p84["path"])],
            "item_blocking_reason": "P83_SOURCE_MALFORMED_JSON",
        }

    if str(p83["status"]) == "NOT_COMPUTABLE":
        return {
            "status": "P84_REGENERATION_PLAN_BLOCKED",
            "required": False,
            "allowed": False,
            "reasons": ["P83_NOT_COMPUTABLE"],
            "blocked_reasons": ["P83_STATUS_NOT_COMPUTABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "recommended_next_lane": (
                "P87_TEMPORAL_CONTINUITY_P83_STATUS_PLAN_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P83 status is NOT_COMPUTABLE; regenerate P83 status planning before "
                "preparing P84 regeneration-plan regeneration."
            ),
            "validation_requirements": [],
            "prerequisite_sources": [str(p85["path"]), str(p84["path"]), str(p83["path"])],
            "item_blocking_reason": "P83_STATUS_NOT_COMPUTABLE",
        }

    if p85_recommended_next_lane == "P84_REGENERATION_PLAN_REGENERATION":
        return {
            "status": "P84_REGENERATION_PLAN_READY",
            "required": True,
            "allowed": False,
            "reasons": [
                "P85_ROUTES_TO_P84_REGENERATION",
                "P83_COMPUTABLE_AND_READY_FOR_P84_REGENERATION",
            ],
            "blocked_reasons": [],
            "future_runner_command": ALLOWED_FUTURE_RUNNER_COMMAND,
            "recommended_next_lane": (
                "P87_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_EXECUTION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P85 routes to P84 regeneration and P83 is computable; emit advisory "
                "P84 regeneration execution planning handoff without executing regeneration."
            ),
            "validation_requirements": _validation_requirements_ready(),
            "prerequisite_sources": [str(p85["path"]), str(p84["path"]), str(p83["path"])],
            "item_blocking_reason": "REGENERATION_PLAN_ONLY_EXECUTION_DENIED",
        }

    return {
        "status": "NOT_COMPUTABLE",
        "required": False,
        "allowed": False,
        "reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
        "blocked_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
        "future_runner_command": "NOT_COMPUTABLE",
        "recommended_next_lane": "P85_EXECUTION_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "Source chain is weak or inconsistent; regenerate P85 execution planning "
            "before deriving P84 regeneration-plan regeneration planning."
        ),
        "validation_requirements": [],
        "prerequisite_sources": _sorted_paths(
            [str(p85["path"]), str(p84["path"]), str(p83["path"])]
        ),
        "item_blocking_reason": "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
    }


def _build_regeneration_item(
    *,
    current_status: str,
    regeneration_reason: str,
    prerequisite_paths: list[str],
    future_command: str,
    blocking_reason: str,
) -> dict[str, Any]:
    return {
        "regeneration_item_id": "regeneration_item_p84_001",
        "target_artifact_path": SOURCE_P84_REGENERATION_PLAN_PATH,
        "current_status": current_status,
        "required_status_after_regeneration": "P80_REGENERATION_PLAN_READY",
        "regeneration_reason": regeneration_reason,
        "prerequisite_paths": _sorted_paths(prerequisite_paths),
        "future_command": future_command,
        "expected_output_path": EXPECTED_OUTPUT_PATH,
        "regeneration_execution_allowed": False,
        "blocking_reason": blocking_reason,
    }


def build_temporal_continuity_p84_regeneration_plan_regeneration_plan(
    *,
    repo_root: str | Path = ".",
    source_p85_execution_plan_path: str = SOURCE_P85_EXECUTION_PLAN_PATH,
    source_p84_regeneration_plan_path: str = SOURCE_P84_REGENERATION_PLAN_PATH,
    source_p83_status_plan_path: str = SOURCE_P83_STATUS_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)

    p85 = _observe_source(
        root=root,
        rel_path=source_p85_execution_plan_path,
        status_field="p80_regeneration_execution_plan_status",
    )
    p84 = _observe_source(
        root=root,
        rel_path=source_p84_regeneration_plan_path,
        status_field="p80_regeneration_plan_status",
    )
    p83 = _observe_source(
        root=root,
        rel_path=source_p83_status_plan_path,
        status_field="p79_status_repair_plan_status",
    )

    classification = _classify(p85=p85, p84=p84, p83=p83)

    p85_payload = p85.get("payload")
    p84_payload = p84.get("payload")
    inherited_payload: dict[str, Any] = (
        p85_payload
        if isinstance(p85_payload, dict)
        else (p84_payload if isinstance(p84_payload, dict) else {})
    )

    degraded_evidence_inputs = _as_str_list(
        inherited_payload.get("degraded_evidence_inputs")
    )
    inherited_blockers = _as_str_list(inherited_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(inherited_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(inherited_payload.get("semantic_overlap_flags"))

    regeneration_reasons = _ordered_unique(
        [str(reason) for reason in classification["reasons"]],
        _REASON_ORDER_INDEX,
    )
    blocked_regeneration_reasons = _ordered_unique(
        [str(reason) for reason in classification["blocked_reasons"]],
        _BLOCKED_REASON_ORDER_INDEX,
    )

    prerequisite_sources = _sorted_paths(
        [str(path) for path in classification["prerequisite_sources"]]
    )

    validation_requirements = sorted(
        [
            {
                "validation_id": str(item["validation_id"]),
                "validation_type": str(item["validation_type"]),
                "path": str(item["path"]),
                "required_status": str(item["required_status"]),
                "failure_action": str(item["failure_action"]),
            }
            for item in classification["validation_requirements"]
        ],
        key=lambda item: _VALIDATION_ORDER_INDEX.get(str(item["validation_id"]), 10_000),
    )

    status = str(classification["status"])
    p84_regeneration_plan_regeneration_status = (
        status if status in _PLAN_STATUSES else "NOT_COMPUTABLE"
    )
    p84_regeneration_required = bool(classification["required"])

    future_runner_command = str(classification["future_runner_command"])
    regeneration_item = _build_regeneration_item(
        current_status=str(p84["status"]),
        regeneration_reason=regeneration_reasons[0]
        if regeneration_reasons
        else "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        prerequisite_paths=prerequisite_sources,
        future_command=future_runner_command,
        blocking_reason=str(classification["item_blocking_reason"]),
    )
    regeneration_items = sorted(
        [regeneration_item],
        key=lambda item: (
            str(item["regeneration_item_id"]),
            str(item["target_artifact_path"]),
        ),
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "regeneration_plan_only": True,
        "meta_regeneration_plan_only": True,
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
        "authorization_record_creation_authority": False,
        "spine_implementation_authority": False,
        "source_p85_execution_plan_path": source_p85_execution_plan_path,
        "source_p85_execution_plan_observed": bool(p85["observed"]),
        "source_p85_execution_plan_readable": bool(p85["readable"]),
        "source_p85_execution_plan_hash": str(p85["file_hash"]),
        "source_p85_execution_plan_status": str(p85["status"]),
        "source_p85_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "source_p84_regeneration_plan_path": source_p84_regeneration_plan_path,
        "source_p84_regeneration_plan_observed": bool(p84["observed"]),
        "source_p84_regeneration_plan_readable": bool(p84["readable"]),
        "source_p84_regeneration_plan_hash": str(p84["file_hash"]),
        "source_p84_regeneration_plan_status": str(p84["status"]),
        "source_p83_status_plan_path": source_p83_status_plan_path,
        "source_p83_status_plan_observed": bool(p83["observed"]),
        "source_p83_status_plan_readable": bool(p83["readable"]),
        "source_p83_status_plan_hash": str(p83["file_hash"]),
        "source_p83_status_plan_status": str(p83["status"]),
        "p84_regeneration_plan_regeneration_status": p84_regeneration_plan_regeneration_status,
        "p84_regeneration_required": p84_regeneration_required,
        "p84_regeneration_allowed": False,
        "regeneration_reasons": regeneration_reasons,
        "regeneration_items": regeneration_items,
        "future_runner_command": future_runner_command,
        "expected_output_path": EXPECTED_OUTPUT_PATH,
        "prerequisite_sources": prerequisite_sources,
        "validation_requirements": validation_requirements,
        "blocked_regeneration_reasons": blocked_regeneration_reasons,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "regeneration_strategy_summary": {
            "p84_regeneration_plan_regeneration_status": (
                p84_regeneration_plan_regeneration_status
            ),
            "p84_regeneration_required": p84_regeneration_required,
            "p84_regeneration_allowed": False,
            "regeneration_reasons_count": len(regeneration_reasons),
            "regeneration_items_count": len(regeneration_items),
            "prerequisite_sources_count": len(prerequisite_sources),
            "validation_requirements_count": len(validation_requirements),
            "blocked_regeneration_reasons_count": len(blocked_regeneration_reasons),
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


def write_temporal_continuity_p84_regeneration_plan_regeneration_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
