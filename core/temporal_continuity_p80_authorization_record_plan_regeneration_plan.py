from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityP80AuthorizationRecordPlanRegenerationPlan.v1"
SOURCE_P83_STATUS_PLAN_PATH = (
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
)
SOURCE_P79_GATE_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
)
SOURCE_P80_RECORD_PLAN_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)
ALLOWED_FUTURE_RUNNER_COMMAND = (
    "python scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py"
)
EXPECTED_OUTPUT_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)

_ALLOWED_P79_GATE_STATUSES = (
    "AUTHORIZATION_ELIGIBLE",
    "AUTHORIZATION_BLOCKED",
    "AUTHORIZATION_NOT_REQUIRED",
)

_REASON_ORDER = (
    "P83_RECOMMENDS_P80_REGENERATION",
    "P80_STATUS_NOT_COMPUTABLE",
    "P80_SOURCE_STALE_AFTER_P79_READY",
    "P79_GATE_READY_FOR_P80",
    "P80_ALREADY_READY",
    "P79_GATE_NOT_COMPUTABLE",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_REASON_ORDER_INDEX = {reason: idx for idx, reason in enumerate(_REASON_ORDER)}

_BLOCKED_REASON_ORDER = (
    "P83_SOURCE_MISSING",
    "P83_SOURCE_UNREADABLE",
    "P83_SOURCE_MALFORMED_JSON",
    "P83_BLOCKED_OR_NOT_COMPUTABLE",
    "P79_SOURCE_MISSING",
    "P79_SOURCE_UNREADABLE",
    "P79_SOURCE_MALFORMED_JSON",
    "P79_GATE_NOT_COMPUTABLE",
    "P80_REGENERATION_NOT_REQUIRED",
    "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
)
_BLOCKED_REASON_ORDER_INDEX = {
    reason: idx for idx, reason in enumerate(_BLOCKED_REASON_ORDER)
}

_VALIDATION_ORDER = (
    "validation_001_p79_source_exists",
    "validation_002_p79_source_readable",
    "validation_003_p79_status_allowed",
    "validation_004_future_command_exact_match",
    "validation_005_expected_output_path_match",
    "validation_006_p80_exists_after_regeneration",
    "validation_007_p80_readable_after_regeneration",
    "validation_008_p80_status_computable_after_regeneration",
    "validation_009_authority_flags_false_after_regeneration",
)
_VALIDATION_ORDER_INDEX = {vid: idx for idx, vid in enumerate(_VALIDATION_ORDER)}

_DENIED_AUTHORITY: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "repair_execution_authority",
    "regeneration_authority",
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


def _build_validation_requirements_ready() -> list[dict[str, str]]:
    requirements = [
        {
            "validation_id": "validation_001_p79_source_exists",
            "validation_type": "source_exists",
            "path": SOURCE_P79_GATE_PATH,
            "required_status": "observed=true",
            "failure_action": "BLOCK_P80_REGENERATION_EXECUTION_PLANNING",
        },
        {
            "validation_id": "validation_002_p79_source_readable",
            "validation_type": "source_readable",
            "path": SOURCE_P79_GATE_PATH,
            "required_status": "readable=true",
            "failure_action": "BLOCK_P80_REGENERATION_EXECUTION_PLANNING",
        },
        {
            "validation_id": "validation_003_p79_status_allowed",
            "validation_type": "status_allowlist",
            "path": SOURCE_P79_GATE_PATH,
            "required_status": (
                "authorization_gate_status in "
                "{AUTHORIZATION_ELIGIBLE,AUTHORIZATION_BLOCKED,AUTHORIZATION_NOT_REQUIRED}"
            ),
            "failure_action": "BLOCK_P80_REGENERATION_EXECUTION_PLANNING",
        },
        {
            "validation_id": "validation_004_future_command_exact_match",
            "validation_type": "future_command_exact_match",
            "path": "scripts/temporal/run_temporal_continuity_upstream_input_regeneration_authorization_record_plan.py",
            "required_status": ALLOWED_FUTURE_RUNNER_COMMAND,
            "failure_action": "MARK_NOT_COMPUTABLE",
        },
        {
            "validation_id": "validation_005_expected_output_path_match",
            "validation_type": "expected_output_path_match",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": EXPECTED_OUTPUT_PATH,
            "failure_action": "MARK_NOT_COMPUTABLE",
        },
        {
            "validation_id": "validation_006_p80_exists_after_regeneration",
            "validation_type": "post_regeneration_source_exists",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "observed=true",
            "failure_action": "BLOCK_DOWNSTREAM_LANES",
        },
        {
            "validation_id": "validation_007_p80_readable_after_regeneration",
            "validation_type": "post_regeneration_source_readable",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "readable=true",
            "failure_action": "BLOCK_DOWNSTREAM_LANES",
        },
        {
            "validation_id": "validation_008_p80_status_computable_after_regeneration",
            "validation_type": "post_regeneration_status",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "authorization_record_plan_status!=NOT_COMPUTABLE",
            "failure_action": "REGENERATE_P80_OR_REPAIR_SOURCES",
        },
        {
            "validation_id": "validation_009_authority_flags_false_after_regeneration",
            "validation_type": "authority_lock_check",
            "path": EXPECTED_OUTPUT_PATH,
            "required_status": "all_authority_flags=false",
            "failure_action": "FAIL_CLOSED_REPORT_AND_BLOCK",
        },
    ]
    return sorted(
        requirements,
        key=lambda item: _VALIDATION_ORDER_INDEX.get(str(item["validation_id"]), 10_000),
    )


def _classify(
    *,
    p83: dict[str, Any],
    p79: dict[str, Any],
    p80: dict[str, Any],
) -> dict[str, Any]:
    p83_status = str(p83["status"])
    p83_lane = "NOT_COMPUTABLE"
    p83_payload = p83.get("payload")
    if isinstance(p83_payload, dict):
        p83_lane = str(p83_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))

    if not p83["observed"]:
        return {
            "p80_regeneration_plan_status": "NOT_COMPUTABLE",
            "p80_regeneration_required": False,
            "recommended_next_lane": "P83_STATUS_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P83 status repair plan source is missing; regenerate P83 before "
                "deriving a P80 regeneration plan."
            ),
            "regeneration_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
            "blocked_regeneration_reasons": ["P83_SOURCE_MISSING"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P83_SOURCE_MISSING",
            "prerequisite_sources": [],
        }

    if not p83["readable"]:
        return {
            "p80_regeneration_plan_status": "NOT_COMPUTABLE",
            "p80_regeneration_required": False,
            "recommended_next_lane": "P83_STATUS_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P83 status repair plan source is unreadable; regenerate P83 before "
                "deriving a P80 regeneration plan."
            ),
            "regeneration_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
            "blocked_regeneration_reasons": ["P83_SOURCE_UNREADABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P83_SOURCE_UNREADABLE",
            "prerequisite_sources": [],
        }

    if p83["malformed_json"]:
        return {
            "p80_regeneration_plan_status": "NOT_COMPUTABLE",
            "p80_regeneration_required": False,
            "recommended_next_lane": "P83_STATUS_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P83 status repair plan source is malformed JSON; regenerate P83 before "
                "deriving a P80 regeneration plan."
            ),
            "regeneration_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
            "blocked_regeneration_reasons": ["P83_SOURCE_MALFORMED_JSON"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P83_SOURCE_MALFORMED_JSON",
            "prerequisite_sources": [],
        }

    if p83_status in {"NOT_COMPUTABLE", "P79_STATUS_REPAIR_BLOCKED_BY_P82"}:
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_PLAN_BLOCKED",
            "p80_regeneration_required": False,
            "recommended_next_lane": "P83_STATUS_REPAIR_PLAN_REGENERATION",
            "recommended_next_lane_reason": (
                "P83 status repair lane is blocked or NOT_COMPUTABLE; regenerate P83 "
                "before attempting any P80 regeneration planning."
            ),
            "regeneration_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
            "blocked_regeneration_reasons": ["P83_BLOCKED_OR_NOT_COMPUTABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P83_BLOCKED_OR_NOT_COMPUTABLE",
            "prerequisite_sources": [],
        }

    if p83_lane != "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION":
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_NOT_REQUIRED",
            "p80_regeneration_required": False,
            "recommended_next_lane": "P83_RECOMMENDED_NEXT_LANE_PASSTHROUGH",
            "recommended_next_lane_reason": (
                "P83 routes to a different lane; preserving pass-through semantics and "
                "not introducing a new P80 regeneration requirement."
            ),
            "regeneration_reasons": ["WEAK_OR_INCONSISTENT_SOURCE_CHAIN"],
            "blocked_regeneration_reasons": ["P80_REGENERATION_NOT_REQUIRED"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P80_REGENERATION_NOT_REQUIRED",
            "prerequisite_sources": [str(p83["path"])],
        }

    if not p79["observed"]:
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_PLAN_BLOCKED",
            "p80_regeneration_required": False,
            "recommended_next_lane": (
                "P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate source is missing; repair/regenerate P79 before "
                "planning P80 regeneration execution."
            ),
            "regeneration_reasons": ["P79_GATE_NOT_COMPUTABLE"],
            "blocked_regeneration_reasons": ["P79_SOURCE_MISSING"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P79_SOURCE_MISSING",
            "prerequisite_sources": [str(p83["path"])],
        }

    if not p79["readable"]:
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_PLAN_BLOCKED",
            "p80_regeneration_required": False,
            "recommended_next_lane": (
                "P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate source is unreadable; repair/regenerate P79 before "
                "planning P80 regeneration execution."
            ),
            "regeneration_reasons": ["P79_GATE_NOT_COMPUTABLE"],
            "blocked_regeneration_reasons": ["P79_SOURCE_UNREADABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P79_SOURCE_UNREADABLE",
            "prerequisite_sources": [str(p83["path"])],
        }

    if p79["malformed_json"]:
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_PLAN_BLOCKED",
            "p80_regeneration_required": False,
            "recommended_next_lane": (
                "P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate source is malformed JSON; repair/regenerate P79 "
                "before planning P80 regeneration execution."
            ),
            "regeneration_reasons": ["P79_GATE_NOT_COMPUTABLE"],
            "blocked_regeneration_reasons": ["P79_SOURCE_MALFORMED_JSON"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P79_SOURCE_MALFORMED_JSON",
            "prerequisite_sources": [str(p83["path"])],
        }

    p79_status = str(p79["status"])
    if p79_status == "NOT_COMPUTABLE" or p79_status not in _ALLOWED_P79_GATE_STATUSES:
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_PLAN_BLOCKED",
            "p80_regeneration_required": False,
            "recommended_next_lane": (
                "P85_TEMPORAL_CONTINUITY_P79_AUTHORIZATION_GATE_REGENERATION_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P79 authorization gate status is NOT_COMPUTABLE or outside the allowed "
                "status set; P79 must be repaired before P80 regeneration planning."
            ),
            "regeneration_reasons": ["P79_GATE_NOT_COMPUTABLE"],
            "blocked_regeneration_reasons": ["P79_GATE_NOT_COMPUTABLE"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P79_GATE_NOT_COMPUTABLE",
            "prerequisite_sources": [str(p83["path"]), str(p79["path"])],
        }

    if (
        p80["observed"]
        and p80["readable"]
        and not p80["malformed_json"]
        and str(p80["status"]) == "AUTHORIZATION_RECORD_PLAN_READY"
    ):
        return {
            "p80_regeneration_plan_status": "P80_REGENERATION_NOT_REQUIRED",
            "p80_regeneration_required": False,
            "recommended_next_lane": (
                "P85_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_TEMPLATE_PLAN"
            ),
            "recommended_next_lane_reason": (
                "P80 source already reports AUTHORIZATION_RECORD_PLAN_READY; regeneration "
                "is not required."
            ),
            "regeneration_reasons": ["P80_ALREADY_READY"],
            "blocked_regeneration_reasons": ["P80_REGENERATION_NOT_REQUIRED"],
            "future_runner_command": "NOT_COMPUTABLE",
            "validation_requirements": [],
            "item_blocking_reason": "P80_REGENERATION_NOT_REQUIRED",
            "prerequisite_sources": [
                str(p83["path"]),
                str(p79["path"]),
                str(p80["path"]),
            ],
        }

    p80_status = str(p80["status"])
    reasons = [
        "P83_RECOMMENDS_P80_REGENERATION",
        "P79_GATE_READY_FOR_P80",
    ]
    if p80_status == "NOT_COMPUTABLE":
        reasons.append("P80_STATUS_NOT_COMPUTABLE")
    else:
        reasons.append("P80_SOURCE_STALE_AFTER_P79_READY")

    return {
        "p80_regeneration_plan_status": "P80_REGENERATION_PLAN_READY",
        "p80_regeneration_required": True,
        "recommended_next_lane": (
            "P85_TEMPORAL_CONTINUITY_P80_AUTHORIZATION_RECORD_PLAN_REGENERATION_EXECUTION_PLAN"
        ),
        "recommended_next_lane_reason": (
            "P83 recommends P80 regeneration and P79 source is computable; emit advisory "
            "execution planning handoff without executing regeneration."
        ),
        "regeneration_reasons": reasons,
        "blocked_regeneration_reasons": [],
        "future_runner_command": ALLOWED_FUTURE_RUNNER_COMMAND,
        "validation_requirements": _build_validation_requirements_ready(),
        "item_blocking_reason": "REGENERATION_PLAN_ONLY_EXECUTION_DENIED",
        "prerequisite_sources": [
            str(p83["path"]),
            str(p79["path"]),
            str(p80["path"]),
        ],
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
        "regeneration_item_id": "regeneration_item_p80_001",
        "lane": "P80",
        "target_artifact_path": SOURCE_P80_RECORD_PLAN_PATH,
        "current_status": current_status,
        "required_status_after_regeneration": "AUTHORIZATION_RECORD_PLAN_READY",
        "regeneration_reason": regeneration_reason,
        "prerequisite_paths": _sorted_paths(prerequisite_paths),
        "future_command": future_command,
        "expected_output_path": EXPECTED_OUTPUT_PATH,
        "regeneration_execution_allowed": False,
        "blocking_reason": blocking_reason,
    }


def build_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
    *,
    repo_root: str | Path = ".",
    source_p83_status_plan_path: str = SOURCE_P83_STATUS_PLAN_PATH,
    source_p79_gate_path: str = SOURCE_P79_GATE_PATH,
    source_p80_record_plan_path: str = SOURCE_P80_RECORD_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)

    p83 = _observe_source(
        root=root,
        rel_path=source_p83_status_plan_path,
        status_field="p79_status_repair_plan_status",
    )
    p79 = _observe_source(
        root=root,
        rel_path=source_p79_gate_path,
        status_field="authorization_gate_status",
    )
    p80 = _observe_source(
        root=root,
        rel_path=source_p80_record_plan_path,
        status_field="authorization_record_plan_status",
    )

    classification = _classify(p83=p83, p79=p79, p80=p80)

    p83_payload = p83.get("payload")
    inherited_payload: dict[str, Any] = (
        p83_payload if isinstance(p83_payload, dict) else {}
    )

    degraded_evidence_inputs = _as_str_list(
        inherited_payload.get("degraded_evidence_inputs")
    )
    inherited_blockers = _as_str_list(inherited_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(inherited_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(inherited_payload.get("semantic_overlap_flags"))

    regeneration_reasons = _ordered_unique(
        [str(reason) for reason in classification["regeneration_reasons"]],
        _REASON_ORDER_INDEX,
    )
    blocked_regeneration_reasons = _ordered_unique(
        [str(reason) for reason in classification["blocked_regeneration_reasons"]],
        _BLOCKED_REASON_ORDER_INDEX,
    )
    prerequisite_sources = _sorted_paths(
        [str(path) for path in classification["prerequisite_sources"]]
    )

    future_runner_command = str(classification["future_runner_command"])
    regeneration_item = _build_regeneration_item(
        current_status=str(p80["status"]),
        regeneration_reason=regeneration_reasons[0]
        if regeneration_reasons
        else "WEAK_OR_INCONSISTENT_SOURCE_CHAIN",
        prerequisite_paths=prerequisite_sources,
        future_command=future_runner_command,
        blocking_reason=str(classification["item_blocking_reason"]),
    )
    regeneration_items = [regeneration_item]
    regeneration_items = sorted(
        regeneration_items,
        key=lambda item: (
            str(item["regeneration_item_id"]),
            str(item["lane"]),
            str(item["target_artifact_path"]),
        ),
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

    p80_regeneration_plan_status = str(classification["p80_regeneration_plan_status"])
    p80_regeneration_required = bool(classification["p80_regeneration_required"])

    packet_base: dict[str, Any] = {
        "artifact_regeneration_authority": False,
        "artifact_type": ARTIFACT_TYPE,
        "audit_only": True,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "blocked_regeneration_reasons": blocked_regeneration_reasons,
        "canon_promotion": False,
        "canonical_status": "ADVISORY_ONLY",
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "denied_authority": sorted(_DENIED_AUTHORITY),
        "evidence_generation_authority": False,
        "execution_authority": False,
        "expected_output_path": EXPECTED_OUTPUT_PATH,
        "forecast_influence": False,
        "future_runner_command": future_runner_command,
        "generator_execution_authority": False,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "p80_regeneration_allowed": False,
        "p80_regeneration_plan_status": p80_regeneration_plan_status,
        "p80_regeneration_required": p80_regeneration_required,
        "packet_hash": "NOT_COMPUTABLE",
        "prerequisite_sources": prerequisite_sources,
        "production_activation": False,
        "projection_only": True,
        "recommended_next_lane": str(classification["recommended_next_lane"]),
        "recommended_next_lane_reason": str(classification["recommended_next_lane_reason"]),
        "regeneration_authority": False,
        "regeneration_items": regeneration_items,
        "regeneration_plan_only": True,
        "regeneration_reasons": regeneration_reasons,
        "regeneration_strategy_summary": {
            "blocked_regeneration_reasons_count": len(blocked_regeneration_reasons),
            "p80_regeneration_required": p80_regeneration_required,
            "p80_regeneration_status": p80_regeneration_plan_status,
            "prerequisite_sources_count": len(prerequisite_sources),
            "regeneration_items_count": len(regeneration_items),
            "regeneration_reasons_count": len(regeneration_reasons),
            "validation_requirements_count": len(validation_requirements),
        },
        "repair_authority": False,
        "repair_execution_authority": False,
        "restoration_execution_authority": False,
        "runtime_authority": False,
        "scheduler_mutation": False,
        "semantic_overlap_flags": semantic_overlap_flags,
        "source_p79_gate_hash": str(p79["file_hash"]),
        "source_p79_gate_observed": bool(p79["observed"]),
        "source_p79_gate_path": source_p79_gate_path,
        "source_p79_gate_readable": bool(p79["readable"]),
        "source_p79_gate_status": str(p79["status"]),
        "source_p80_record_plan_hash": str(p80["file_hash"]),
        "source_p80_record_plan_observed": bool(p80["observed"]),
        "source_p80_record_plan_path": source_p80_record_plan_path,
        "source_p80_record_plan_readable": bool(p80["readable"]),
        "source_p80_record_plan_status": str(p80["status"]),
        "source_p83_recommended_next_lane": str(
            inherited_payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "source_p83_status_plan_hash": str(p83["file_hash"]),
        "source_p83_status_plan_observed": bool(p83["observed"]),
        "source_p83_status_plan_path": source_p83_status_plan_path,
        "source_p83_status_plan_readable": bool(p83["readable"]),
        "source_p83_status_plan_status": str(p83["status"]),
        "spine_implementation_authority": False,
        "upstream_input_generation_authority": False,
        "validation_requirements": validation_requirements,
    }
    packet_no_hash = {k: v for k, v in packet_base.items() if k != "packet_hash"}
    packet = {**packet_no_hash, "packet_hash": canonical_hash(packet_no_hash)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_p80_authorization_record_plan_regeneration_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
