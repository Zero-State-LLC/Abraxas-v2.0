"""Oracle full live run-control builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records receipt-first live execution controls after FULL_LIVE_EXECUTION_GATE.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


FULL_LIVE_EXECUTION_RECEIPT_HASH = (
    "8849ac411e0f36f7a086e2fb8476078e8f54e08c6311c79a852e5b2c8601c08c"
)


def build_oracle_full_live_run_control(
    *,
    timestamp: str,
    full_live_execution_receipt: Mapping[str, Any],
    oracle_full_live_execution: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRunControl.v1",
        "run_control_id": canonical_hash(
            {
                "record": "oracle_full_live_run_control",
                "full_live_execution_receipt": (
                    full_live_execution_receipt["canonical_hash"]
                ),
                "oracle_full_live_execution": (
                    oracle_full_live_execution["canonical_hash"]
                ),
                "operator_gate": "FULL_LIVE_EXECUTION_GATE",
            }
        ),
        "run_control_status": "ORACLE_FULL_LIVE_RUN_CONTROL_READY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "full_live_execution_receipt": (
                full_live_execution_receipt["canonical_hash"]
            ),
            "oracle_full_live_execution": oracle_full_live_execution[
                "canonical_hash"
            ],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_FULL_LIVE_EXECUTION_GATE_001",
            "gate_status": "RECORDED_AND_BOUND_TO_RUN_CONTROL",
            "operator_monitoring_required": True,
            "receipt_required_before_each_run": True,
            "brier_score": 0.1,
        },
        "endpoint_runtime_plan": [
            _endpoint_plan("ORACLE_SIGNAL_PRIMARY_ENDPOINT", "ORACLE_SIGNAL_ENDPOINT_URL"),
            _endpoint_plan("HOLLERSPORTS_PRIMARY_ENDPOINT", "HOLLERSPORTS_BATCH_ENDPOINT_URL"),
        ],
        "scheduler_queue_plan": [
            _scheduler_queue_plan("ORACLE_SIGNAL_PRODUCTION_SCHEDULER", "scheduler"),
            _scheduler_queue_plan("ORACLE_SIGNAL_PRODUCTION_QUEUE", "queue"),
        ],
        "telemetry_monitoring_plan": [
            _telemetry_plan("ORACLE_LIVE_CONNECTIVITY_HEALTH", "health"),
            _telemetry_plan("ORACLE_LIVE_INGEST_LATENCY", "latency"),
            _telemetry_plan("ORACLE_LIVE_BRIER_DRIFT", "brier_drift"),
        ],
        "holler_live_batch_plan": [
            {
                "plan_id": "HOLLERSPORTS_OPERATOR_MONITORED_BATCH_RUN",
                "endpoint_env_var": "HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "live_market_reads_authorized": True,
                "autonomous_outcome_recording": False,
                "requires_operator_monitoring": True,
                "requires_receipt_before_run": True,
                "brier_score": 0.1,
            }
        ],
        "pre_execution_checks": [
            _pre_execution_check("SCHEMA_VALIDATION_CURRENT", "PASS_REQUIRED"),
            _pre_execution_check("ENDPOINT_ENV_PRESENT", "OPERATOR_RUNTIME_REQUIRED"),
            _pre_execution_check("OPERATOR_MONITORING_ACTIVE", "PASS_REQUIRED"),
            _pre_execution_check("NO_MCP_OR_WRITEBACK_PATH", "PASS_REQUIRED"),
        ],
        "governance_controls": {
            "required_cli": (
                "python scripts/abx_loop.py --emit-oracle-full-live-run-control "
                "--validate-oracle-schemas"
            ),
            "receipt_required": (
                "out/audit/"
                "oracle_full_live_run_control_receipt_001.latest.json"
            ),
            "secret_material_embedded": False,
            "operator_runtime_environment_required": True,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_full_live_run_control"),
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


def build_oracle_full_live_run_control_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_full_live_run_control: Mapping[str, Any],
    holler_oracle_full_live_run_control: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRunControlReceipt.v1",
        "receipt_id": "ORACLE_FULL_LIVE_RUN_CONTROL_RECEIPT_001",
        "receipt_status": "ORACLE_FULL_LIVE_RUN_CONTROL_READY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_full_live_run_control": oracle_full_live_run_control[
                "canonical_hash"
            ],
            "holler_oracle_full_live_run_control": (
                holler_oracle_full_live_run_control["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "recommended_next_advisory_action": (
            "Run operator-monitored live execution only through a receipt-emitting "
            "runtime command with endpoint environment configured."
        ),
        "provenance": _provenance("oracle_full_live_run_control_receipt"),
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


def _endpoint_plan(connection_id: str, endpoint_env_var: str) -> dict[str, Any]:
    return {
        "connection_id": connection_id,
        "endpoint_env_var": endpoint_env_var,
        "secret_material_embedded": False,
        "run_status": "READY_REQUIRES_OPERATOR_RUNTIME_ENV",
        "requires_receipt_before_call": True,
        "brier_score": 0.1,
    }


def _scheduler_queue_plan(binding_id: str, binding_type: str) -> dict[str, Any]:
    return {
        "binding_id": binding_id,
        "binding_type": binding_type,
        "run_status": "READY_REQUIRES_OPERATOR_MONITORING",
        "persistent_runtime_activation_authorized": True,
        "requires_receipt_before_execution": True,
        "brier_score": 0.1,
    }


def _telemetry_plan(monitor_id: str, metric_family: str) -> dict[str, Any]:
    return {
        "monitor_id": monitor_id,
        "metric_family": metric_family,
        "run_status": "PERSISTENT_TELEMETRY_READY",
        "telemetry_writeback_authorized": False,
        "operator_monitoring_required": True,
        "brier_score": 0.1,
    }


def _pre_execution_check(check_id: str, required_status: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "required_status": required_status,
        "blocking": True,
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
        "full_live_execution_receipt_hash": FULL_LIVE_EXECUTION_RECEIPT_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
