"""Oracle full live execution readiness builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records explicit FULL_LIVE_EXECUTION_GATE for governed live surfaces only.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


PRODUCTION_ACTIVATION_READY_RECEIPT_HASH = (
    "625369624ff8843c4f4ea7e0fe32c3563e4fb4bdc553c54baac7497416328a28"
)
LIVE_WIRING_PREPARATION_RECEIPT_HASH = (
    "756a84c23e5555ff058aae9ceca50c52c6d6f9527e036bc9a054497bf9549145"
)


def build_oracle_full_live_execution(
    *,
    timestamp: str,
    production_activation_ready_receipt: Mapping[str, Any],
    oracle_production_activation_ready: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveExecution.v1",
        "execution_id": canonical_hash(
            {
                "record": "oracle_full_live_execution",
                "production_activation_ready_receipt": (
                    production_activation_ready_receipt["canonical_hash"]
                ),
                "oracle_production_activation_ready": (
                    oracle_production_activation_ready["canonical_hash"]
                ),
                "operator_gate": "FULL_LIVE_EXECUTION_GATE",
            }
        ),
        "execution_status": "ORACLE_SIGNAL_LAYER_FULL_LIVE_EXECUTION_READY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "production_activation_ready_receipt": (
                production_activation_ready_receipt["canonical_hash"]
            ),
            "oracle_production_activation_ready": (
                oracle_production_activation_ready["canonical_hash"]
            ),
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "real_oracle_endpoint_connections": [
            _endpoint_connection(
                "ORACLE_SIGNAL_PRIMARY_ENDPOINT",
                "ORACLE_SIGNAL_ENDPOINT_URL",
                "oracle_signal",
            ),
            _endpoint_connection(
                "HOLLERSPORTS_PRIMARY_ENDPOINT",
                "HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "hollersports",
            ),
        ],
        "live_signal_ingestion_pipelines": [
            _ingestion_pipeline("ORACLE_SIGNAL_LIVE_INGEST", "oracle_signal"),
            _ingestion_pipeline("HOLLERSPORTS_LIVE_BATCH_INGEST", "hollersports"),
        ],
        "production_scheduler_queue_integration": [
            _scheduler_queue_runtime("ORACLE_SIGNAL_PRODUCTION_SCHEDULER", "scheduler"),
            _scheduler_queue_runtime("ORACLE_SIGNAL_PRODUCTION_QUEUE", "queue"),
        ],
        "persistent_telemetry_monitors": [
            _telemetry_monitor("ORACLE_LIVE_CONNECTIVITY_HEALTH", "health"),
            _telemetry_monitor("ORACLE_LIVE_INGEST_LATENCY", "latency"),
            _telemetry_monitor("ORACLE_LIVE_BRIER_DRIFT", "brier_drift"),
        ],
        "holler_live_batch_processing": [
            {
                "pipeline_id": "HOLLERSPORTS_FULL_LIVE_BATCH_PROCESSING",
                "pipeline_status": "FULL_LIVE_EXECUTION_READY_UNDER_OPERATOR_MONITORING",
                "valid_for_live_market_reads": True,
                "valid_for_live_batch_processing": True,
                "valid_for_outcome_recording": False,
                "requires_governance_receipt_before_run": True,
                "brier_score": 0.1,
            }
        ],
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_FULL_LIVE_EXECUTION_GATE_001",
            "gate_status": "EXPLICIT_OPERATOR_GATE_RECEIVED",
            "operator": "Daniel (AALM1tch) - Operator",
            "date": "2026-06-23",
            "real_external_connectivity_authorized": True,
            "live_data_flows_authorized": True,
            "governance_loop_control_required": True,
            "receipts_required_before_execution": True,
            "mcp_exposure_authorized": False,
            "unreviewed_deployment_authorized": False,
            "brier_score": 0.1,
        },
        "governance_controls": {
            "required_cli": (
                "python Scripts/abx_loop.py --emit-oracle-full-live "
                "--validate-oracle-schemas"
            ),
            "receipt_required": (
                "out/audit/oracle_full_live_execution_receipt_001.latest.json"
            ),
            "operator_monitoring_required": True,
            "notion_writeback": "PASTE_READY_ONLY_UNTIL_SEPARATE_WRITEBACK_GATE",
            "github_writeback": False,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_full_live_execution"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_execution_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_full_live_execution: Mapping[str, Any],
    holler_oracle_full_live_execution: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveExecutionReceipt.v1",
        "receipt_id": "ORACLE_FULL_LIVE_EXECUTION_RECEIPT_001",
        "receipt_status": "ORACLE_SIGNAL_LAYER_FULL_LIVE_EXECUTION_READY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_full_live_execution": oracle_full_live_execution[
                "canonical_hash"
            ],
            "holler_oracle_full_live_execution": (
                holler_oracle_full_live_execution["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_FULL_LIVE_EXECUTION_GATE_001",
            "production_activation_ready_receipt_hash": (
                PRODUCTION_ACTIVATION_READY_RECEIPT_HASH
            ),
            "live_wiring_preparation_receipt_hash": (
                LIVE_WIRING_PREPARATION_RECEIPT_HASH
            ),
            "real_external_connectivity_authorized": True,
            "live_data_flows_authorized": True,
            "receipts_required_before_execution": True,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Review full live execution surfaces, verify operator monitoring, "
            "and run governed live execution only through receipt-emitting CLI."
        ),
        "provenance": _provenance("oracle_full_live_execution_receipt"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_persistent_telemetry": True,
        "valid_for_scheduler_queue_runtime": True,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _endpoint_connection(
    connection_id: str,
    endpoint_env_var: str,
    domain: str,
) -> dict[str, Any]:
    return {
        "connection_id": connection_id,
        "domain": domain,
        "endpoint_env_var": endpoint_env_var,
        "secret_material_embedded": False,
        "connection_status": "FULL_LIVE_READY_REQUIRES_RUNTIME_ENV",
        "requires_governance_receipt_before_call": True,
        "brier_score": 0.1,
    }


def _ingestion_pipeline(pipeline_id: str, domain: str) -> dict[str, Any]:
    return {
        "pipeline_id": pipeline_id,
        "domain": domain,
        "pipeline_status": "FULL_LIVE_READY_UNDER_GOVERNANCE_LOOP",
        "live_ingestion_authorized": True,
        "requires_operator_monitoring": True,
        "brier_score": 0.1,
    }


def _scheduler_queue_runtime(binding_id: str, binding_type: str) -> dict[str, Any]:
    return {
        "binding_id": binding_id,
        "binding_type": binding_type,
        "binding_status": "FULL_LIVE_RUNTIME_READY",
        "persistent_runtime_activation_authorized": True,
        "requires_receipt_before_execution": True,
        "brier_score": 0.1,
    }


def _telemetry_monitor(monitor_id: str, metric_family: str) -> dict[str, Any]:
    return {
        "monitor_id": monitor_id,
        "metric_family": metric_family,
        "monitor_status": "PERSISTENT_TELEMETRY_READY",
        "telemetry_writeback_authorized": True,
        "requires_operator_monitoring": True,
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
        "github_writeback": False,
        "notion_writeback": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "operator_gate": "FULL_LIVE_EXECUTION_GATE",
        "production_activation_ready_receipt_hash": (
            PRODUCTION_ACTIVATION_READY_RECEIPT_HASH
        ),
        "live_wiring_preparation_receipt_hash": LIVE_WIRING_PREPARATION_RECEIPT_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
