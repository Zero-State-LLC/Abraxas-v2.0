"""Oracle production activation readiness advisory builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Generates production-ready templates only; no external calls or activation.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


LIVE_WIRING_PREPARATION_RECEIPT_HASH = (
    "74b539eb289cd67750cf5f5e3c6451081a347b401984b184da71ab3f9fb6a0d6"
)


def build_oracle_production_activation_ready(
    *,
    timestamp: str,
    activation_ready_gate_receipt: Mapping[str, Any],
    live_wiring_preparation_receipt: Mapping[str, Any],
    oracle_live_wiring_preparation: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleProductionActivationReady.v1",
        "activation_id": canonical_hash(
            {
                "record": "oracle_production_activation_ready",
                "activation_ready_hash": activation_ready_gate_receipt[
                    "canonical_hash"
                ],
                "live_wiring_receipt_hash": live_wiring_preparation_receipt[
                    "canonical_hash"
                ],
                "live_wiring_preparation_hash": oracle_live_wiring_preparation[
                    "canonical_hash"
                ],
            }
        ),
        "activation_status": "ORACLE_SIGNAL_LAYER_PRODUCTION_ACTIVATION_READY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "activation_ready_gate": activation_ready_gate_receipt["canonical_hash"],
            "live_wiring_preparation_receipt": live_wiring_preparation_receipt[
                "canonical_hash"
            ],
            "oracle_live_wiring_preparation": oracle_live_wiring_preparation[
                "canonical_hash"
            ],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "production_connector_surfaces": [
            _connector_surface("ORACLE_SIGNAL_LIVE_CONNECTOR", "oracle_signal"),
            _connector_surface("HOLLERSPORTS_LIVE_BATCH_CONNECTOR", "hollersports"),
        ],
        "production_endpoint_configurations": [
            _endpoint_config("ORACLE_SIGNAL_ENDPOINT_CONFIG", "ORACLE_SIGNAL_ENDPOINT_URL"),
            _endpoint_config("HOLLERSPORTS_BATCH_ENDPOINT_CONFIG", "HOLLERSPORTS_BATCH_ENDPOINT_URL"),
        ],
        "scheduler_queue_bindings": [
            _scheduler_queue_binding("ORACLE_SIGNAL_INGEST_SCHEDULE", "scheduler"),
            _scheduler_queue_binding("ORACLE_SIGNAL_INGEST_QUEUE", "queue"),
        ],
        "production_telemetry_monitors": [
            _telemetry_monitor("ORACLE_PRODUCTION_CONNECTOR_HEALTH", "health"),
            _telemetry_monitor("ORACLE_PRODUCTION_BRIER_DRIFT", "brier_drift"),
            _telemetry_monitor("ORACLE_PRODUCTION_LATENCY", "latency"),
        ],
        "holler_live_batch_pipelines": [
            {
                "pipeline_id": "HOLLERSPORTS_LIVE_BATCH_PIPELINE",
                "pipeline_status": "PRODUCTION_TEMPLATE_READY_NOT_CONNECTED",
                "supports_shadow_dryrun": True,
                "valid_for_actual_live_ingestion": False,
                "valid_for_external_oracle_calls": False,
                "brier_score": 0.1,
            }
        ],
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_PRODUCTION_ACTIVATION_GATE_001",
            "gate_status": "EXPLICIT_OPERATOR_GATE_RECEIVED",
            "operator": "Daniel (AALM1tch) - Operator",
            "date": "2026-06-23",
            "production_ready_templates_authorized": True,
            "shadow_dryrun_execution_authorized": True,
            "actual_external_calls_authorized": False,
            "persistent_runtime_activation_authorized": False,
            "full_live_execution_gate_required": True,
            "brier_score": 0.1,
        },
        "required_next_gate": {
            "full_live_execution_gate_required": True,
            "next_gate_statement": (
                "Operator must issue a separate FULL_LIVE_EXECUTION_GATE with "
                "risk review before external connectivity or live ingestion."
            ),
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_production_activation_ready"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_production_code_generation": True,
        "valid_for_shadow_dryrun_execution": True,
        "valid_for_actual_external_oracle_calls": False,
        "valid_for_actual_live_data_ingestion": False,
        "valid_for_persistent_production_runtime_activation": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_production_activation_ready_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_production_activation_ready: Mapping[str, Any],
    holler_oracle_production_activation_ready: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleProductionActivationReadyReceipt.v1",
        "receipt_id": "ORACLE_PRODUCTION_ACTIVATION_READY_RECEIPT_001",
        "receipt_status": "ORACLE_SIGNAL_LAYER_PRODUCTION_ACTIVATION_READY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_production_activation_ready": oracle_production_activation_ready[
                "canonical_hash"
            ],
            "holler_oracle_production_activation_ready": (
                holler_oracle_production_activation_ready["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_PRODUCTION_ACTIVATION_GATE_001",
            "live_wiring_preparation_receipt_hash": (
                LIVE_WIRING_PREPARATION_RECEIPT_HASH
            ),
            "production_ready_templates_authorized": True,
            "shadow_dryrun_execution_authorized": True,
            "actual_external_calls_authorized": False,
            "persistent_runtime_activation_authorized": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Review production activation templates and require a separate "
            "FULL_LIVE_EXECUTION_GATE before external connectivity or live ingestion."
        ),
        "provenance": _provenance("oracle_production_activation_ready_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_production_code_generation": True,
        "valid_for_shadow_dryrun_execution": True,
        "valid_for_actual_external_oracle_calls": False,
        "valid_for_actual_live_data_ingestion": False,
        "valid_for_persistent_production_runtime_activation": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _connector_surface(surface_id: str, domain: str) -> dict[str, Any]:
    return {
        "surface_id": surface_id,
        "domain": domain,
        "surface_status": "PRODUCTION_READY_TEMPLATE_NOT_CONNECTED",
        "supports_shadow_dryrun": True,
        "valid_for_actual_external_calls": False,
        "brier_score": 0.1,
    }


def _endpoint_config(config_id: str, env_var: str) -> dict[str, Any]:
    return {
        "config_id": config_id,
        "endpoint_env_var": env_var,
        "secret_material_embedded": False,
        "network_calls_enabled": False,
        "requires_full_live_execution_gate": True,
        "brier_score": 0.1,
    }


def _scheduler_queue_binding(binding_id: str, binding_type: str) -> dict[str, Any]:
    return {
        "binding_id": binding_id,
        "binding_type": binding_type,
        "binding_status": "PRODUCTION_BINDING_TEMPLATE_NOT_MUTATED",
        "supports_shadow_dryrun": True,
        "valid_for_persistent_mutation": False,
        "brier_score": 0.1,
    }


def _telemetry_monitor(monitor_id: str, metric_family: str) -> dict[str, Any]:
    return {
        "monitor_id": monitor_id,
        "metric_family": metric_family,
        "monitor_status": "PRODUCTION_MONITOR_TEMPLATE_NOT_WRITING",
        "supports_shadow_dryrun": True,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "actual_external_oracle_calls": False,
        "actual_live_data_ingestion": False,
        "persistent_production_runtime_activation": False,
        "mcp_exposure": False,
        "unreviewed_production_deployment": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "operator_gate": "PRODUCTION_ACTIVATION_GATE",
        "live_wiring_preparation_receipt_hash": LIVE_WIRING_PREPARATION_RECEIPT_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
