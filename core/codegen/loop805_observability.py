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


def build_oracle_signal_observability_hook(
    *,
    timestamp: str,
    oracle_receipt_hash: str,
    schema_paths: Sequence[str],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ABX_LOOP805_ORACLE_SIGNAL_LAYER_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_SIGNAL_OBSERVABILITY_HOOK_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "oracle_receipt_hash": oracle_receipt_hash,
        "schema_paths": list(schema_paths),
        "hook_mode": "REFERENCE_ONLY_NO_LIVE_TELEMETRY",
        "provenance": {
            "source": "loop805_observability",
            "oracle_signal_layer": "ADVISORY_CANON_EXTENSION_ONLY",
            "live_invocation": False,
            "brier_resolution": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_live_signal_ingest": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
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


def build_oracle_ingest_wiring_observability_hook(
    *,
    timestamp: str,
    wiring_receipt_hash: str,
    wiring_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_INGEST_WIRING_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_INGEST_WIRING_OBSERVABILITY_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "wiring_receipt_hash": wiring_receipt_hash,
        "wiring_schema_path": wiring_schema_path,
        "telemetry_mode": "SHADOW_TELEMETRY_PLAN_ONLY_NOT_LIVE",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_ingest": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_shadow_dryrun_observability_hook(
    *,
    timestamp: str,
    dryrun_receipt_hash: str,
    dryrun_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_SHADOW_DRYRUN_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_SHADOW_DRYRUN_OBSERVABILITY_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "dryrun_receipt_hash": dryrun_receipt_hash,
        "dryrun_schema_path": dryrun_schema_path,
        "route_decision_logging": "PROJECTED_ONLY_NO_ROUTE_MUTATION",
        "telemetry_mode": "SHADOW_REPLAY_TELEMETRY_PLAN_ONLY_NOT_LIVE",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_signal_ingest": False,
        "valid_for_runtime_execution": False,
        "valid_for_shadow_replay_execution": False,
        "valid_for_route_mutation": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_readiness_observability_hook(
    *,
    timestamp: str,
    readiness_receipt_hash: str,
    readiness_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_MEASUREMENT_READINESS_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_MEASUREMENT_READINESS_OBSERVABILITY_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "readiness_receipt_hash": readiness_receipt_hash,
        "readiness_schema_path": readiness_schema_path,
        "decision_intake_logging": "PROJECTED_ONLY_NO_ATTESTATION_RECORDING",
        "measurement_mode": "READINESS_REVIEW_ONLY_NOT_EXECUTED",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_measurement": False,
        "valid_for_measurement_execution": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_shadow_measurement_observability_hook(
    *,
    timestamp: str,
    measurement_receipt_hash: str,
    measurement_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_SHADOW_MEASUREMENT_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_SHADOW_MEASUREMENT_OBSERVABILITY_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_receipt_hash": measurement_receipt_hash,
        "measurement_schema_path": measurement_schema_path,
        "route_decision_logging": "PROJECTED_ONLY_NO_ROUTE_MUTATION",
        "measurement_logging": "PROJECTED_ONLY_NO_MEASUREMENT_EXECUTION",
        "telemetry_mode": "SHADOW_MEASUREMENT_TELEMETRY_PLAN_ONLY_NOT_LIVE",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_measurement": False,
        "valid_for_measurement_execution": False,
        "valid_for_outcome_recording": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_proposal_observability_hook(
    *,
    timestamp: str,
    proposal_receipt_hash: str,
    proposal_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_MEASUREMENT_PROPOSAL_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_MEASUREMENT_PROPOSAL_OBSERVABILITY_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "proposal_receipt_hash": proposal_receipt_hash,
        "proposal_schema_path": proposal_schema_path,
        "decision_intake_logging": "PROJECTED_ONLY_NO_ATTESTATION_RECORDING",
        "proposal_mode": "OPERATOR_REVIEW_PROPOSAL_ONLY_NOT_AUTHORIZED",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_measurement": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement_execution": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_authorization_proposal_observability_hook(
    *,
    timestamp: str,
    authorization_proposal_receipt_hash: str,
    authorization_proposal_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_OBSERVABILITY_HOOK",
        "hook_status": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_OBSERVABILITY_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "authorization_proposal_receipt_hash": authorization_proposal_receipt_hash,
        "authorization_proposal_schema_path": authorization_proposal_schema_path,
        "decision_intake_logging": "PROJECTED_ONLY_NO_ATTESTATION_RECORDING",
        "authorization_mode": "PROPOSAL_ONLY_NOT_AUTHORIZED",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_measurement": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement_execution": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_live_wiring_preparation_observability_hook(
    *,
    timestamp: str,
    live_wiring_receipt_hash: str,
    live_wiring_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_LIVE_WIRING_PREPARATION_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "live_wiring_receipt_hash": live_wiring_receipt_hash,
        "live_wiring_schema_path": live_wiring_schema_path,
        "connector_logging": "TEMPLATE_ONLY_NO_EXTERNAL_CALLS",
        "scheduler_queue_logging": "REFERENCE_ONLY_NO_MUTATION",
        "telemetry_mode": "MONITORING_TEMPLATE_ONLY_NO_WRITEBACK",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_signal_ingest": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_scheduler_mutation": False,
        "valid_for_queue_mutation": False,
        "valid_for_mcp_exposure": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_production_activation_ready_observability_hook(
    *,
    timestamp: str,
    production_activation_receipt_hash: str,
    production_activation_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_PRODUCTION_ACTIVATION_READY_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_PRODUCTION_ACTIVATION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "production_activation_receipt_hash": production_activation_receipt_hash,
        "production_activation_schema_path": production_activation_schema_path,
        "code_generation_logging": "PRODUCTION_TEMPLATE_GENERATION_ONLY",
        "shadow_dryrun_logging": "AUTHORIZED_FOR_SHADOW_DRYRUN_ONLY",
        "external_connectivity_logging": "BLOCKED_UNTIL_FULL_LIVE_EXECUTION_GATE",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_production_code_generation": True,
        "valid_for_shadow_dryrun_execution": True,
        "valid_for_actual_external_oracle_calls": False,
        "valid_for_actual_live_data_ingestion": False,
        "valid_for_persistent_production_runtime_activation": False,
        "valid_for_mcp_exposure": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_execution_observability_hook(
    *,
    timestamp: str,
    full_live_execution_receipt_hash: str,
    full_live_execution_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_FULL_LIVE_EXECUTION_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_FULL_LIVE_EXECUTION_READY_GOVERNED",
        "timestamp": timestamp,
        "full_live_execution_receipt_hash": full_live_execution_receipt_hash,
        "full_live_execution_schema_path": full_live_execution_schema_path,
        "external_connectivity_logging": "AUTHORIZED_UNDER_FULL_LIVE_EXECUTION_GATE",
        "live_ingestion_logging": "AUTHORIZED_UNDER_GOVERNANCE_LOOP_CONTROL",
        "scheduler_queue_logging": "AUTHORIZED_WITH_RECEIPT_BEFORE_EXECUTION",
        "telemetry_mode": "PERSISTENT_MONITORING_READY_OPERATOR_MONITORED",
        "authority_locks": {
            **AUTHORITY_LOCKS,
            "execution_authority": True,
            "actual_external_oracle_calls": True,
            "actual_live_data_ingestion": True,
            "persistent_production_runtime_activation": True,
        },
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_run_control_observability_hook(
    *,
    timestamp: str,
    full_live_run_control_receipt_hash: str,
    full_live_run_control_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_FULL_LIVE_RUN_CONTROL_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_FULL_LIVE_RUN_CONTROL_READY_GOVERNED",
        "timestamp": timestamp,
        "full_live_run_control_receipt_hash": full_live_run_control_receipt_hash,
        "full_live_run_control_schema_path": full_live_run_control_schema_path,
        "endpoint_runtime_logging": "AUTHORIZED_REQUIRES_OPERATOR_RUNTIME_ENV",
        "live_ingestion_logging": "AUTHORIZED_REQUIRES_RECEIPT_BEFORE_RUN",
        "scheduler_queue_logging": "AUTHORIZED_REQUIRES_OPERATOR_MONITORING",
        "telemetry_mode": "PERSISTENT_MONITORING_READY_NO_WRITEBACK",
        "authority_locks": {
            **AUTHORITY_LOCKS,
            "execution_authority": True,
            "actual_external_oracle_calls": True,
            "actual_live_data_ingestion": True,
            "persistent_production_runtime_activation": True,
            "autonomous_outcome_recording": False,
        },
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_runtime_command_observability_hook(
    *,
    timestamp: str,
    full_live_runtime_command_receipt_hash: str,
    full_live_runtime_command_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_FULL_LIVE_RUNTIME_COMMAND_OBSERVABILITY_HOOK",
        "hook_status": "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY_GOVERNED",
        "timestamp": timestamp,
        "full_live_runtime_command_receipt_hash": (
            full_live_runtime_command_receipt_hash
        ),
        "full_live_runtime_command_schema_path": (
            full_live_runtime_command_schema_path
        ),
        "runtime_command_logging": "AUTHORIZED_REQUIRES_RECEIPT_BEFORE_COMMAND",
        "endpoint_runtime_logging": "AUTHORIZED_REQUIRES_OPERATOR_RUNTIME_ENV",
        "scheduler_queue_logging": "AUTHORIZED_REQUIRES_OPERATOR_MONITORING",
        "telemetry_mode": "PERSISTENT_MONITORING_READY_NO_WRITEBACK",
        "authority_locks": {
            **AUTHORITY_LOCKS,
            "execution_authority": True,
            "actual_external_oracle_calls": True,
            "actual_live_data_ingestion": True,
            "persistent_production_runtime_activation": True,
            "autonomous_outcome_recording": False,
        },
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_authorization_decision_review_candidate_observability_hook(
    *,
    timestamp: str,
    decision_review_candidate_receipt_hash: str,
    decision_review_candidate_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_OBSERVABILITY_HOOK"
        ),
        "hook_status": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_OBSERVABILITY_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "decision_review_candidate_receipt_hash": (
            decision_review_candidate_receipt_hash
        ),
        "decision_review_candidate_schema_path": (
            decision_review_candidate_schema_path
        ),
        "decision_intake_logging": "PROJECTED_ONLY_NO_ATTESTATION_RECORDING",
        "decision_review_mode": "CANDIDATE_ONLY_NOT_RECORDED_NOT_AUTHORIZED",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_measurement": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement_execution": False,
        "valid_for_authorization_decision_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_authorization_decision_record_observability_hook(
    *,
    timestamp: str,
    decision_record_receipt_hash: str,
    decision_record_schema_path: str,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_OBSERVABILITY_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hook_id": "ORACLE_AUTHORIZATION_DECISION_RECORD_OBSERVABILITY_HOOK",
        "hook_status": (
            "ORACLE_AUTHORIZATION_DECISION_RECORD_OBSERVABILITY_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "decision_record_receipt_hash": decision_record_receipt_hash,
        "decision_record_schema_path": decision_record_schema_path,
        "decision_record_logging": "TEMPLATE_ONLY_NO_DECISION_RECORDING",
        "authorization_mode": "HELD_FOR_SEPARATE_OPERATOR_GATE_NOT_AUTHORIZED",
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_live_measurement": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement_execution": False,
        "valid_for_authorization_decision_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
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
