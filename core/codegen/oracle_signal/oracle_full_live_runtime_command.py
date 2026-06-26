"""Oracle full-live runtime command/runbook builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records receipt-first runtime command readiness after FULL_LIVE_EXECUTION_GATE.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


FULL_LIVE_RUN_CONTROL_RECEIPT_HASH = (
    "ef55fc9356dbc23fc15f1e029a84c028f53a965a381f3ab57064d2fe63545697"
)


def build_oracle_full_live_runtime_command(
    *,
    timestamp: str,
    oracle_full_live_run_control: Mapping[str, Any],
    oracle_full_live_run_control_receipt: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRuntimeCommand.v1",
        "runtime_command_id": canonical_hash(
            {
                "record": "oracle_full_live_runtime_command",
                "run_control": oracle_full_live_run_control["canonical_hash"],
                "run_control_receipt": (
                    oracle_full_live_run_control_receipt["canonical_hash"]
                ),
                "operator_gate": "FULL_LIVE_EXECUTION_GATE",
            }
        ),
        "runtime_command_status": "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_full_live_run_control": oracle_full_live_run_control[
                "canonical_hash"
            ],
            "oracle_full_live_run_control_receipt": (
                oracle_full_live_run_control_receipt["canonical_hash"]
            ),
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "operator_monitoring_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_FULL_LIVE_EXECUTION_GATE_001",
            "gate_status": "RECORDED_AND_BOUND_TO_RUNTIME_COMMAND",
            "operator_console_required": True,
            "receipt_required_before_each_runtime_command": True,
            "brier_score": 0.1,
        },
        "runtime_command_manifest": [
            _runtime_command(
                "ORACLE_SCHEMA_VALIDATION_PRECHECK",
                "python Scripts/abx_loop.py --validate-oracle-schemas",
            ),
            _runtime_command(
                "ORACLE_FULL_LIVE_RUN_CONTROL_RECEIPT_PRECHECK",
                (
                    "python Scripts/abx_loop.py "
                    "--emit-oracle-full-live-run-control --validate-oracle-schemas"
                ),
            ),
            _runtime_command(
                "ORACLE_FULL_LIVE_RUNTIME_COMMAND_RECEIPT",
                (
                    "python Scripts/abx_loop.py "
                    "--emit-oracle-full-live-runtime-command "
                    "--validate-oracle-schemas"
                ),
            ),
        ],
        "endpoint_environment_requirements": [
            _endpoint_requirement(
                "ORACLE_SIGNAL_PRIMARY_ENDPOINT",
                "ORACLE_SIGNAL_ENDPOINT_URL",
            ),
            _endpoint_requirement(
                "HOLLERSPORTS_PRIMARY_ENDPOINT",
                "HOLLERSPORTS_BATCH_ENDPOINT_URL",
            ),
        ],
        "scheduler_queue_runtime_manifest": [
            _runtime_binding("ORACLE_SIGNAL_PRODUCTION_SCHEDULER", "scheduler"),
            _runtime_binding("ORACLE_SIGNAL_PRODUCTION_QUEUE", "queue"),
        ],
        "telemetry_monitoring_manifest": [
            _telemetry_manifest("ORACLE_LIVE_CONNECTIVITY_HEALTH", "health"),
            _telemetry_manifest("ORACLE_LIVE_INGEST_LATENCY", "latency"),
            _telemetry_manifest("ORACLE_LIVE_BRIER_DRIFT", "brier_drift"),
        ],
        "holler_live_batch_manifest": [
            {
                "manifest_id": "HOLLERSPORTS_LIVE_BATCH_RUNTIME_COMMAND",
                "endpoint_env_var": "HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "batch_scope": "HOLLERSPORTS_OPERATOR_MONITORED_LIVE_BATCH",
                "valid_for_live_market_reads": True,
                "autonomous_outcome_recording": False,
                "requires_operator_monitoring": True,
                "requires_receipt_before_run": True,
                "brier_score": 0.1,
            }
        ],
        "pre_run_blockers": [
            _pre_run_blocker("SCHEMA_VALIDATION_NOT_CURRENT"),
            _pre_run_blocker("RUN_CONTROL_RECEIPT_MISSING"),
            _pre_run_blocker("ENDPOINT_ENV_MISSING"),
            _pre_run_blocker("OPERATOR_MONITORING_NOT_ACTIVE"),
            _pre_run_blocker("MCP_OR_WRITEBACK_PATH_PRESENT"),
        ],
        "provenance": _provenance("oracle_full_live_runtime_command"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_autonomous_outcome_recording": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_runtime_command_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_full_live_runtime_command: Mapping[str, Any],
    holler_oracle_full_live_runtime_command: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRuntimeCommandReceipt.v1",
        "receipt_id": "ORACLE_FULL_LIVE_RUNTIME_COMMAND_RECEIPT_001",
        "receipt_status": "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_full_live_runtime_command": (
                oracle_full_live_runtime_command["canonical_hash"]
            ),
            "holler_oracle_full_live_runtime_command": (
                holler_oracle_full_live_runtime_command["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "recommended_next_advisory_action": (
            "Run the operator-monitored runtime command only after endpoint "
            "environment, schema validation, and monitoring console checks pass."
        ),
        "provenance": _provenance("oracle_full_live_runtime_command_receipt"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _runtime_command(command_id: str, command: str) -> dict[str, Any]:
    return {
        "command_id": command_id,
        "command": command,
        "mode": "RECEIPT_EMITTING_OPERATOR_MONITORED",
        "secret_material_embedded": False,
        "requires_operator_monitoring": True,
        "brier_score": 0.1,
    }


def _endpoint_requirement(connection_id: str, endpoint_env_var: str) -> dict[str, Any]:
    return {
        "connection_id": connection_id,
        "endpoint_env_var": endpoint_env_var,
        "required_before_runtime_command": True,
        "secret_material_embedded": False,
        "brier_score": 0.1,
    }


def _runtime_binding(binding_id: str, binding_type: str) -> dict[str, Any]:
    return {
        "binding_id": binding_id,
        "binding_type": binding_type,
        "runtime_status": "READY_REQUIRES_OPERATOR_MONITORING",
        "requires_receipt_before_execution": True,
        "brier_score": 0.1,
    }


def _telemetry_manifest(monitor_id: str, metric_family: str) -> dict[str, Any]:
    return {
        "monitor_id": monitor_id,
        "metric_family": metric_family,
        "monitoring_status": "PERSISTENT_MONITORING_READY_NO_WRITEBACK",
        "operator_monitoring_required": True,
        "brier_score": 0.1,
    }


def _pre_run_blocker(blocker_id: str) -> dict[str, Any]:
    return {
        "blocker_id": blocker_id,
        "blocking": True,
        "resolution_mode": "OPERATOR_REVIEW_REQUIRED",
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
        "full_live_run_control_receipt_hash": FULL_LIVE_RUN_CONTROL_RECEIPT_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
