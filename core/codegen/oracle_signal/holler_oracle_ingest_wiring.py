"""HollerSports Oracle ingest wiring advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live ingest.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_ingest_wiring(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_ingest_wiring: Mapping[str, Any],
    schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleIngestWiring.v1",
        "wiring_id": canonical_hash(
            {
                "record": "holler_oracle_ingest_wiring",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_ingest_wiring_hash": oracle_ingest_wiring["canonical_hash"],
            }
        ),
        "wiring_status": "HOLLER_ORACLE_INGEST_WIRING_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_ingest_wiring_hash": oracle_ingest_wiring["canonical_hash"],
        "schema_validation_receipt_hash": schema_validation_receipt["canonical_hash"],
        "telemetry_hooks": [
            {
                "hook_id": "HOLLER_MARKET_COUNT_TELEMETRY",
                "observed_value": int(holler_batch["market_count"]),
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
            {
                "hook_id": "HOLLER_ADVERSARIAL_FIXTURE_TELEMETRY",
                "observed_value": int(holler_batch["adversarial_fixture_count"]),
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
        ],
        "routing_constraints": {
            "calibration_policy": holler_batch["calibration_policy"],
            "valid_for_marketplace_ingest": False,
            "valid_for_live_route": False,
            "brier_score": 0.1,
        },
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "live_signal_ingest": False,
            "marketplace_ingest": False,
            "telemetry_writeback": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
        },
        "advisory_only": True,
        "valid_for_live_ingest": False,
        "valid_for_runtime_execution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
