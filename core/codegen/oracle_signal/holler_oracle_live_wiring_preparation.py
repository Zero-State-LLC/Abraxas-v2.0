"""HollerSports Oracle live wiring preparation advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no live ingest, no telemetry writeback.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_live_wiring_preparation(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_live_wiring_preparation: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleLiveWiringPreparation.v1",
        "preparation_id": canonical_hash(
            {
                "record": "holler_oracle_live_wiring_preparation",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_live_wiring_preparation_hash": (
                    oracle_live_wiring_preparation["canonical_hash"]
                ),
            }
        ),
        "preparation_status": (
            "HOLLER_ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_live_wiring_preparation_hash": oracle_live_wiring_preparation[
            "canonical_hash"
        ],
        "holler_connector_templates": [
            {
                "connector_id": "HOLLERSPORTS_MARKET_BATCH_CONNECTOR_TEMPLATE",
                "sport": holler_batch["sport"],
                "market_count_projection": int(holler_batch["market_count"]),
                "valid_for_live_market_reads": False,
                "brier_score": 0.1,
            },
            {
                "connector_id": "HOLLERSPORTS_SETTLEMENT_CONNECTOR_TEMPLATE",
                "sport": holler_batch["sport"],
                "settlement_mode": "TEMPLATE_ONLY_NO_OUTCOME_RECORDING",
                "valid_for_outcome_recording": False,
                "brier_score": 0.1,
            },
        ],
        "telemetry_templates": [
            {
                "hook_id": "HOLLERSPORTS_CONNECTOR_HEALTH_TEMPLATE",
                "metric_family": "holler_connector_health",
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
            {
                "hook_id": "HOLLERSPORTS_MARKET_LATENCY_TEMPLATE",
                "metric_family": "holler_market_latency",
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
        ],
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "live_signal_ingest": False,
            "external_oracle_calls": False,
            "live_market_reads": False,
            "outcome_recording": False,
            "telemetry_writeback": False,
            "scheduler_mutation": False,
            "queue_mutation": False,
            "production_activation": False,
        },
        "advisory_only": True,
        "valid_for_live_signal_ingest": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_live_market_reads": False,
        "valid_for_outcome_recording": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
