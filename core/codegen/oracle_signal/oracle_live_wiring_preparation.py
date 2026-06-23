"""Oracle live wiring preparation advisory builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no live ingest, no external calls.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


LIVE_WIRING_GATE_RECEIPT_HASH = (
    "80c07e85819a9322856fd9416d4981810e3d097029f86f19bf3827899fe41a18"
)


def build_oracle_live_wiring_preparation(
    *,
    timestamp: str,
    activation_ready_gate_receipt: Mapping[str, Any],
    oracle_signal_layer_completion_receipt: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
    oracle_ingest_wiring: Mapping[str, Any],
    oracle_shadow_dryrun: Mapping[str, Any],
    oracle_shadow_measurement: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleLiveWiringPreparation.v1",
        "preparation_id": canonical_hash(
            {
                "record": "oracle_live_wiring_preparation",
                "activation_ready_gate_hash": activation_ready_gate_receipt[
                    "canonical_hash"
                ],
                "completion_receipt_hash": oracle_signal_layer_completion_receipt[
                    "canonical_hash"
                ],
                "shadow_measurement_hash": oracle_shadow_measurement[
                    "canonical_hash"
                ],
            }
        ),
        "preparation_status": "ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "activation_ready_gate": activation_ready_gate_receipt["canonical_hash"],
            "oracle_signal_layer_completion": oracle_signal_layer_completion_receipt[
                "canonical_hash"
            ],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
            "oracle_ingest_wiring": oracle_ingest_wiring["canonical_hash"],
            "oracle_shadow_dryrun": oracle_shadow_dryrun["canonical_hash"],
            "oracle_shadow_measurement": oracle_shadow_measurement["canonical_hash"],
        },
        "live_ingest_connector_stubs": [
            _connector_stub(
                "ORACLE_LIVE_INGEST_CONNECTOR_TEMPLATE",
                "external_oracle_endpoint",
            ),
            _connector_stub(
                "HOLLERSPORTS_LIVE_INGEST_CONNECTOR_TEMPLATE",
                "hollersports_batch_endpoint",
            ),
        ],
        "oracle_endpoint_configuration_templates": [
            _endpoint_template(
                "ORACLE_ENDPOINT_CONFIG_TEMPLATE",
                "https://example.invalid/oracle/signal",
            ),
            _endpoint_template(
                "HOLLERSPORTS_ENDPOINT_CONFIG_TEMPLATE",
                "https://example.invalid/hollersports/batch",
            ),
        ],
        "scheduler_queue_integration_points": [
            _integration_point(
                "ORACLE_SIGNAL_SCHEDULER_BINDING_POINT",
                "scheduler",
            ),
            _integration_point(
                "ORACLE_SIGNAL_QUEUE_BINDING_POINT",
                "queue",
            ),
        ],
        "telemetry_monitoring_hooks": [
            _telemetry_hook(
                "ORACLE_LIVE_WIRING_HEALTH_MONITOR_TEMPLATE",
                "connector_health",
            ),
            _telemetry_hook(
                "ORACLE_LIVE_WIRING_LATENCY_MONITOR_TEMPLATE",
                "route_latency",
            ),
            _telemetry_hook(
                "ORACLE_LIVE_WIRING_BRIER_MONITOR_TEMPLATE",
                "shadow_brier_drift",
            ),
        ],
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_LIVE_WIRING_GATE_001",
            "gate_status": "EXPLICIT_OPERATOR_GATE_RECEIVED",
            "operator": "Daniel (AALM1tch) - Operator",
            "date": "2026-06-23",
            "scope": "LIVE_WIRING_PREPARATION_ONLY",
            "production_activation_gate_required": True,
            "records_operator_attestation": False,
            "brier_score": 0.1,
        },
        "required_next_gate": {
            "production_activation_gate_required": True,
            "next_gate_statement": (
                "Operator must issue a separate PRODUCTION_ACTIVATION_GATE before "
                "any non-shadow, real-world execution is allowed."
            ),
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_live_wiring_preparation"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_signal_ingest": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_scheduler_mutation": False,
        "valid_for_queue_mutation": False,
        "valid_for_mcp_exposure": False,
        "valid_for_production_activation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_live_wiring_preparation_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_live_wiring_preparation: Mapping[str, Any],
    holler_oracle_live_wiring_preparation: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleLiveWiringPreparationReceipt.v1",
        "receipt_id": "ORACLE_LIVE_WIRING_PREPARATION_RECEIPT_001",
        "receipt_status": "ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_live_wiring_preparation": oracle_live_wiring_preparation[
                "canonical_hash"
            ],
            "holler_oracle_live_wiring_preparation": (
                holler_oracle_live_wiring_preparation["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_LIVE_WIRING_GATE_001",
            "source_activation_receipt_hash": LIVE_WIRING_GATE_RECEIPT_HASH,
            "live_wiring_preparation_approved": True,
            "live_signal_ingest_authorized": False,
            "production_activation_authorized": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Review live wiring preparation templates and require a separate "
            "PRODUCTION_ACTIVATION_GATE before any non-shadow execution."
        ),
        "provenance": _provenance("oracle_live_wiring_preparation_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_signal_ingest": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_scheduler_mutation": False,
        "valid_for_queue_mutation": False,
        "valid_for_mcp_exposure": False,
        "valid_for_production_activation": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _connector_stub(connector_id: str, endpoint_ref: str) -> dict[str, Any]:
    return {
        "connector_id": connector_id,
        "endpoint_ref": endpoint_ref,
        "connector_status": "TEMPLATE_ONLY_NOT_CONNECTED",
        "valid_for_live_ingest": False,
        "valid_for_external_oracle_calls": False,
        "brier_score": 0.1,
    }


def _endpoint_template(template_id: str, placeholder_uri: str) -> dict[str, Any]:
    return {
        "template_id": template_id,
        "placeholder_uri": placeholder_uri,
        "requires_secret_binding": True,
        "secret_material_present": False,
        "valid_for_network_calls": False,
        "brier_score": 0.1,
    }


def _integration_point(integration_id: str, integration_type: str) -> dict[str, Any]:
    return {
        "integration_id": integration_id,
        "integration_type": integration_type,
        "integration_status": "REFERENCE_ONLY_NO_MUTATION",
        "valid_for_scheduler_mutation": False,
        "valid_for_queue_mutation": False,
        "brier_score": 0.1,
    }


def _telemetry_hook(hook_id: str, metric_family: str) -> dict[str, Any]:
    return {
        "hook_id": hook_id,
        "metric_family": metric_family,
        "hook_status": "MONITORING_TEMPLATE_ONLY",
        "valid_for_live_telemetry": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_signal_ingest": False,
        "external_oracle_calls": False,
        "scheduler_mutation": False,
        "queue_mutation": False,
        "mcp_exposure": False,
        "github_writeback": False,
        "notion_writeback": False,
        "production_activation": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "operator_gate": "LIVE_WIRING_GATE",
        "activation_ready_receipt_hash": LIVE_WIRING_GATE_RECEIPT_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
