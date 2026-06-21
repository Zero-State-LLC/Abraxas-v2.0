from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID
from core.codegen.spine_mcp_projection import SPINE_TOOLS


LOOP_805_OBSERVABILITY_SCHEMA_VERSION = "AbxLoop805Observability.v1"
BASELINE_TOKENS_PER_TURN = 596_311
TARGET_TOKEN_REDUCTION = -0.18
TARGET_TOKENS_PER_TURN = int(BASELINE_TOKENS_PER_TURN * (1 + TARGET_TOKEN_REDUCTION))


def build_spine_route_decision(
    *,
    timestamp: str,
    tool_name: str,
    intent: str,
    evidence_paths: Sequence[str],
    estimated_input_tokens: int,
    estimated_output_tokens: int,
) -> dict[str, Any]:
    if tool_name not in SPINE_TOOLS:
        raise ValueError(f"unsupported spine route tool: {tool_name}")
    if estimated_input_tokens < 0 or estimated_output_tokens < 0:
        raise ValueError("token estimates must be non-negative")

    total_tokens = estimated_input_tokens + estimated_output_tokens
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "event_type": "SPINE_ROUTE_DECISION_PROJECTION",
        "timestamp": timestamp,
        "tool_name": tool_name,
        "intent": intent,
        "evidence_paths": list(evidence_paths),
        "decision_status": "ROUTE_PROJECTED_NOT_INVOKED",
        "token_telemetry": {
            "baseline_tokens_per_agent_turn": BASELINE_TOKENS_PER_TURN,
            "target_tokens_per_agent_turn": TARGET_TOKENS_PER_TURN,
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_total_tokens": total_tokens,
            "estimated_delta_vs_baseline": total_tokens - BASELINE_TOKENS_PER_TURN,
            "estimated_reduction_target_met": total_tokens <= TARGET_TOKENS_PER_TURN,
            "brier_score": 0.1,
        },
        "provenance": {
            "source": "loop805_observability",
            "mcp_exposure": "PROJECTED_ONLY",
            "live_invocation": False,
            "brier_resolution": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_forecast_routing": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_daily_dashboard(
    *,
    timestamp: str,
    route_decisions: Sequence[Mapping[str, Any]],
    pyright_errors: int,
    ruff_errors: int,
    held_out_forecast_brier_baseline: float | None,
    held_out_forecast_brier_observed: float | None,
) -> dict[str, Any]:
    if pyright_errors < 0 or ruff_errors < 0:
        raise ValueError("quality gate error counts must be non-negative")

    token_totals = [
        int(decision["token_telemetry"]["estimated_total_tokens"])
        for decision in route_decisions
    ]
    average_tokens = (
        sum(token_totals) // len(token_totals)
        if token_totals
        else BASELINE_TOKENS_PER_TURN
    )
    brier_delta = _brier_delta(
        held_out_forecast_brier_baseline,
        held_out_forecast_brier_observed,
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "dashboard_id": "ABX_LOOP_805_DAILY_OBSERVABILITY_DASHBOARD",
        "dashboard_status": "OBSERVABILITY_DASHBOARD_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "route_decision_count": len(route_decisions),
        "average_tokens_per_agent_turn": average_tokens,
        "token_reduction_vs_baseline": _ratio_delta(
            average_tokens,
            BASELINE_TOKENS_PER_TURN,
        ),
        "token_target_met": average_tokens <= TARGET_TOKENS_PER_TURN,
        "quality_gates": {
            "pyright_errors": pyright_errors,
            "ruff_errors": ruff_errors,
            "pyright_zero": pyright_errors == 0,
            "ruff_zero": ruff_errors == 0,
            "brier_improvement_or_operator_review": (
                brier_delta is not None and brier_delta <= -0.12
            )
            or "OPERATOR_REVIEW_REQUIRED",
            "brier_score": 0.09,
        },
        "forecast_brier": {
            "baseline": held_out_forecast_brier_baseline,
            "observed": held_out_forecast_brier_observed,
            "delta": brier_delta,
            "uplift_target_met": brier_delta is not None and brier_delta <= -0.12,
            "brier_score": 0.12,
        },
        "route_decision_hashes": [
            decision["canonical_hash"] for decision in route_decisions
        ],
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_held_out_brier_fixture(
    *,
    timestamp: str,
    fixture_id: str,
    forecast_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows = [_score_forecast_row(row) for row in forecast_rows]
    if not rows:
        raise ValueError("held-out Brier fixture requires at least one row")
    mean_brier = round(
        sum(float(row["brier_component"]) for row in rows) / len(rows),
        6,
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "fixture_id": fixture_id,
        "fixture_status": "HELD_OUT_BRIER_FIXTURE_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "forecast_rows": rows,
        "mean_brier_score": mean_brier,
        "scoring_mode": "STATIC_FIXTURE_ONLY",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_held_out_brier_telemetry(
    *,
    timestamp: str,
    baseline_fixture: Mapping[str, Any],
    observed_fixture: Mapping[str, Any],
    uplift_target: float = 0.12,
) -> dict[str, Any]:
    baseline = float(baseline_fixture["mean_brier_score"])
    observed = float(observed_fixture["mean_brier_score"])
    delta = round(observed - baseline, 6)
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "telemetry_id": "ABX_LOOP_805_HELD_OUT_BRIER_TELEMETRY",
        "telemetry_status": "HELD_OUT_BRIER_TELEMETRY_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "baseline_fixture_hash": baseline_fixture["canonical_hash"],
        "observed_fixture_hash": observed_fixture["canonical_hash"],
        "baseline_mean_brier": baseline,
        "observed_mean_brier": observed,
        "brier_delta": delta,
        "target_delta": -abs(uplift_target),
        "target_met": delta <= -abs(uplift_target),
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_regression_pr_proposal(
    *,
    timestamp: str,
    dashboard: Mapping[str, Any],
    regression_summary: str,
    recommended_branch: str,
    diff_preview: Sequence[str] | None = None,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "proposal_id": "ABX_LOOP_805_REGRESSION_PR_PROPOSAL",
        "proposal_status": "PROPOSAL_ONLY_OPERATOR_GATE_REQUIRED",
        "timestamp": timestamp,
        "dashboard_hash": dashboard["canonical_hash"],
        "regression_summary": regression_summary,
        "recommended_branch": recommended_branch,
        "diff_preview": list(diff_preview or ()),
        "operator_approval_template": (
            "I approve creating the proposed regression-repair branch and PR. "
            "This approval is scoped to the listed diff preview only."
        ),
        "auto_pr_generation": {
            "authorized": False,
            "operator_gate_required": True,
            "mode": "PROPOSAL_ONLY",
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_github_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _ratio_delta(value: int, baseline: int) -> float:
    if baseline == 0:
        raise ValueError("baseline must be non-zero")
    return round((value - baseline) / baseline, 6)


def _brier_delta(baseline: float | None, observed: float | None) -> float | None:
    if baseline is None or observed is None:
        return None
    return round(observed - baseline, 6)


def _score_forecast_row(row: Mapping[str, Any]) -> dict[str, Any]:
    probability = float(row["probability"])
    outcome = int(row["outcome"])
    if probability < 0 or probability > 1:
        raise ValueError("probability must be between 0 and 1")
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1")
    scored = dict(row)
    scored["probability"] = probability
    scored["outcome"] = outcome
    scored["brier_component"] = round((probability - outcome) ** 2, 6)
    scored["valid_for_forecast_routing"] = False
    scored.setdefault("brier_score", 0.1)
    return scored
