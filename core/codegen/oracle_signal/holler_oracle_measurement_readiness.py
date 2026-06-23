"""HollerSports Oracle measurement readiness advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no live measurement, no execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_measurement_readiness(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_measurement_readiness: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    fixture_count = len(oracle_measurement_readiness["held_out_fixture_refs"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleMeasurementReadiness.v1",
        "readiness_id": canonical_hash(
            {
                "record": "holler_oracle_measurement_readiness",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_measurement_readiness_hash": oracle_measurement_readiness[
                    "canonical_hash"
                ],
            }
        ),
        "readiness_status": "HOLLER_ORACLE_MEASUREMENT_READINESS_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_measurement_readiness_hash": oracle_measurement_readiness[
            "canonical_hash"
        ],
        "telemetry_hooks": [
            {
                "hook_id": "HOLLER_HELD_OUT_FIXTURE_COUNT_TELEMETRY",
                "observed_value": fixture_count,
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
            {
                "hook_id": "HOLLER_MEASUREMENT_MARKET_COUNT_TELEMETRY",
                "observed_value": int(holler_batch["market_count"]),
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
        ],
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "live_measurement": False,
            "marketplace_ingest": False,
            "telemetry_writeback": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
        },
        "advisory_only": True,
        "valid_for_live_measurement": False,
        "valid_for_runtime_execution": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
