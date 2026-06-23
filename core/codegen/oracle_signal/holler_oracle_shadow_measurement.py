"""HollerSports Oracle shadow measurement advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no measurement execution, no telemetry writeback.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_shadow_measurement(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_shadow_measurement: Mapping[str, Any],
    oracle_measurement_readiness: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    run_count = len(oracle_shadow_measurement["measurement_run_refs"])
    comparison_count = len(oracle_shadow_measurement["projected_outcome_comparisons"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleShadowMeasurement.v1",
        "measurement_id": canonical_hash(
            {
                "record": "holler_oracle_shadow_measurement",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_shadow_measurement_hash": oracle_shadow_measurement[
                    "canonical_hash"
                ],
            }
        ),
        "measurement_status": "HOLLER_ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_shadow_measurement_hash": oracle_shadow_measurement["canonical_hash"],
        "oracle_measurement_readiness_hash": oracle_measurement_readiness[
            "canonical_hash"
        ],
        "mock_measurement_summary": {
            "projected_run_count": run_count,
            "projected_comparison_count": comparison_count,
            "live_market_reads": 0,
            "live_measurement_writes": 0,
            "real_outcome_records": 0,
            "brier_score": 0.1,
        },
        "telemetry_hooks": [
            {
                "hook_id": "HOLLER_SHADOW_MEASUREMENT_RUN_COUNT_TELEMETRY",
                "observed_value": run_count,
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
            {
                "hook_id": "HOLLER_SHADOW_MEASUREMENT_MARKET_COUNT_TELEMETRY",
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
            "measurement_execution": False,
            "external_oracle_calls": False,
            "outcome_recording": False,
            "telemetry_writeback": False,
            "marketplace_ingest": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
        },
        "advisory_only": True,
        "valid_for_live_measurement": False,
        "valid_for_measurement_execution": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_outcome_recording": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
