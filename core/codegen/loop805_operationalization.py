from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


LOOP_805_SCHEMA_VERSION = "AbxLoop805OperationalizationBaseline.v1"
LOOP_805_ID = "ABX-LOOP-805-INTELLIGENCE_SPINE_OPERATIONALIZATION"
SPINE_STATUS = "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE"

AUTHORITY_LOCKS: dict[str, bool] = {
    "advisory_only": True,
    "canon_mutation": False,
    "runtime_mutation": False,
    "execution_authority": False,
    "github_writeback": False,
    "notion_writeback": False,
    "file_writeback": False,
    "production_activation": False,
    "mcp_tool_exposure_live": False,
    "auto_pr_generation": False,
    "forecast_routing": False,
    "brier_resolution": False,
}

SUCCESS_CRITERIA: tuple[dict[str, Any], ...] = (
    {
        "metric": "held_out_forecast_brier_uplift",
        "target_delta": 0.12,
        "baseline_status": "NOT_COMPUTABLE_UNTIL_HELD_OUT_SET_BOUND",
        "brier_score": 0.12,
    },
    {
        "metric": "average_tokens_per_agent_turn_reduction",
        "target_delta": -0.18,
        "baseline_tokens": 596_311,
        "brier_score": 0.1,
    },
    {
        "metric": "pyright_errors",
        "target": 0,
        "baseline_status": "TARGETED_PYRIGHT_ZERO_ON_CODEGEN_LOOP",
        "brier_score": 0.08,
    },
    {
        "metric": "authority_lock_regression",
        "target": 0,
        "baseline_status": "ALL_LOOP_805_LOCKS_FALSE_EXCEPT_ADVISORY_ONLY",
        "brier_score": 0.05,
    },
)

PHASES: tuple[dict[str, Any], ...] = (
    {
        "phase": "PHASE_0_STABILIZE_AND_BASELINE",
        "objective": "Snapshot post-#804 main and emit deterministic baseline telemetry.",
        "status": "SEEDED_ADVISORY_ONLY",
        "brier_score": 0.1,
    },
    {
        "phase": "PHASE_1_SPINE_WIRING_AND_MCP_EXPOSURE",
        "objective": "Project /spine/query, /spine/forecast, and /spine/audit contracts without live exposure.",
        "status": "PROJECTED_NOT_EXPOSED",
        "brier_score": 0.12,
    },
    {
        "phase": "PHASE_2_LOOP_ENGINE_SELF_OBSERVATION",
        "objective": "Seed PLAN_EXECUTE_MEASURE_ADJUST loop skeleton with measurement receipts only.",
        "status": "SKELETON_READY_ADVISORY_ONLY",
        "brier_score": 0.11,
    },
    {
        "phase": "PHASE_3_TOKEN_AND_QUALITY_GATES",
        "objective": "Declare token, Pyright, Ruff, and Brier gates without enforcement authority.",
        "status": "GATES_DECLARED_NOT_ENFORCED",
        "brier_score": 0.09,
    },
    {
        "phase": "PHASE_4_MERGE_AND_TAG_PREP",
        "objective": "Prepare changelog/tag receipt requirements for operator review.",
        "status": "OPERATOR_REVIEW_REQUIRED",
        "brier_score": 0.1,
    },
)


def build_loop805_baseline_receipt(
    *,
    timestamp: str,
    main_merge_sha: str,
    source_receipts: Sequence[str],
    validation_summary: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "receipt_id": "ABX_LOOP_805_OPERATIONALIZATION_BASELINE",
        "receipt_status": "LOOP_805_BASELINE_SEEDED_ADVISORY_ONLY",
        "timestamp": timestamp,
        "main_merge_sha": main_merge_sha,
        "spine_status": SPINE_STATUS,
        "source_receipts": list(source_receipts),
        "phase_plan": [dict(phase) for phase in PHASES],
        "success_criteria": [dict(criteria) for criteria in SUCCESS_CRITERIA],
        "validation_summary": dict(validation_summary),
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_canon_promotion": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_auto_pr_generation": False,
        "recommended_next": [
            "OPERATOR_REVIEW_LOOP_805_SCOPE",
            "BIND_HELD_OUT_FORECAST_SET",
            "RUN_TOKEN_BASELINE_COUNTER",
            "PREPARE_MCP_SERVER_PROPOSAL_ONLY",
        ],
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_continuity_signal(
    *,
    surface: str,
    status: str,
    detail: str,
    brier_score: float,
) -> dict[str, Any]:
    return {
        "loop_id": LOOP_805_ID,
        "surface": surface,
        "status": status,
        "detail": detail,
        "valid_for_execution": False,
        "brier_score": brier_score,
    }
