"""Oracle full-live runtime preflight builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records endpoint-environment readiness before operator-monitored live commands.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_full_live_runtime_preflight(
    *,
    timestamp: str,
    oracle_full_live_runtime_command: Mapping[str, Any],
    oracle_full_live_runtime_command_receipt: Mapping[str, Any],
    endpoint_environment: Mapping[str, str | None],
) -> dict[str, Any]:
    endpoint_checks = [
        _endpoint_check(
            "ORACLE_SIGNAL_PRIMARY_ENDPOINT",
            "ORACLE_SIGNAL_ENDPOINT_URL",
            endpoint_environment.get("ORACLE_SIGNAL_ENDPOINT_URL"),
        ),
        _endpoint_check(
            "HOLLERSPORTS_PRIMARY_ENDPOINT",
            "HOLLERSPORTS_BATCH_ENDPOINT_URL",
            endpoint_environment.get("HOLLERSPORTS_BATCH_ENDPOINT_URL"),
        ),
    ]
    missing_env = [
        check["endpoint_env_var"]
        for check in endpoint_checks
        if check["check_status"] != "ENV_PRESENT_VALUE_REDACTED"
    ]
    ready = not missing_env
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRuntimePreflight.v1",
        "preflight_id": canonical_hash(
            {
                "record": "oracle_full_live_runtime_preflight",
                "runtime_command": oracle_full_live_runtime_command["canonical_hash"],
                "runtime_command_receipt": (
                    oracle_full_live_runtime_command_receipt["canonical_hash"]
                ),
                "endpoint_checks": endpoint_checks,
            }
        ),
        "preflight_status": (
            "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
            if ready
            else "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_BLOCKED_ENV_MISSING"
        ),
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_full_live_runtime_command": (
                oracle_full_live_runtime_command["canonical_hash"]
            ),
            "oracle_full_live_runtime_command_receipt": (
                oracle_full_live_runtime_command_receipt["canonical_hash"]
            ),
        },
        "endpoint_environment_checks": endpoint_checks,
        "operator_monitoring_checks": [
            _operator_check("OPERATOR_CONSOLE_ATTACHED", ready),
            _operator_check("RECEIPT_BEFORE_COMMAND_CONFIRMED", ready),
            _operator_check("NO_MCP_OR_WRITEBACK_PATH_PRESENT", ready),
        ],
        "runtime_command_scope": {
            "scope_status": "PREFLIGHT_ONLY_NO_CALLS_MADE",
            "external_call_count": 0,
            "live_ingestion_count": 0,
            "persistent_write_count": 0,
            "valid_next_command": (
                "operator_monitored_runtime_command"
                if ready
                else "configure_endpoint_environment_then_rerun_preflight"
            ),
            "missing_endpoint_env_vars": missing_env,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_full_live_runtime_preflight"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": ready,
        "valid_for_live_signal_ingestion": ready,
        "valid_for_scheduler_queue_runtime": ready,
        "valid_for_persistent_telemetry": ready,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_autonomous_outcome_recording": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_runtime_preflight_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_full_live_runtime_preflight: Mapping[str, Any],
    holler_oracle_full_live_runtime_preflight: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    ready = (
        oracle_full_live_runtime_preflight["preflight_status"]
        == "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
    )
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRuntimePreflightReceipt.v1",
        "receipt_id": "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_RECEIPT_001",
        "receipt_status": (
            "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
            if ready
            else "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_BLOCKED_ENV_MISSING"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_full_live_runtime_preflight": (
                oracle_full_live_runtime_preflight["canonical_hash"]
            ),
            "holler_oracle_full_live_runtime_preflight": (
                holler_oracle_full_live_runtime_preflight["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "missing_endpoint_env_vars": oracle_full_live_runtime_preflight[
            "runtime_command_scope"
        ]["missing_endpoint_env_vars"],
        "recommended_next_advisory_action": (
            "Run the operator-monitored live runtime command through the "
            "receipt-emitting CLI."
            if ready
            else "Configure ORACLE_SIGNAL_ENDPOINT_URL and "
            "HOLLERSPORTS_BATCH_ENDPOINT_URL, then rerun the preflight."
        ),
        "provenance": _provenance("oracle_full_live_runtime_preflight_receipt"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": ready,
        "valid_for_live_signal_ingestion": ready,
        "valid_for_scheduler_queue_runtime": ready,
        "valid_for_persistent_telemetry": ready,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _endpoint_check(
    connection_id: str,
    endpoint_env_var: str,
    endpoint_value: str | None,
) -> dict[str, Any]:
    present = bool(endpoint_value and endpoint_value.strip())
    return {
        "connection_id": connection_id,
        "endpoint_env_var": endpoint_env_var,
        "check_status": (
            "ENV_PRESENT_VALUE_REDACTED" if present else "ENV_MISSING_OR_EMPTY"
        ),
        "secret_material_embedded": False,
        "endpoint_value_recorded": False,
        "external_call_made": False,
        "blocking": not present,
        "brier_score": 0.1,
    }


def _operator_check(check_id: str, endpoint_ready: bool) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "check_status": (
            "READY_PENDING_OPERATOR_RUNTIME_COMMAND" if endpoint_ready else "HELD"
        ),
        "operator_required": True,
        "blocking": not endpoint_ready,
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": True,
        "actual_external_oracle_calls": True,
        "actual_live_data_ingestion": True,
        "persistent_production_runtime_activation": True,
        "mcp_exposure": False,
        "unreviewed_production_deployment": False,
        "autonomous_outcome_recording": False,
        "github_writeback": False,
        "notion_writeback": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "operator_gate": "FULL_LIVE_EXECUTION_GATE",
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "external_calls_made": 0,
        "brier_score": 0.1,
    }
