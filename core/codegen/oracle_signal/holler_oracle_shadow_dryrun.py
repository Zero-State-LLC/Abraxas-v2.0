"""HollerSports Oracle shadow dry-run advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live ingest.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_shadow_dryrun(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_shadow_dryrun: Mapping[str, Any],
    oracle_ingest_wiring: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    fixture_count = len(oracle_shadow_dryrun["replay_fixtures"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleShadowDryRun.v1",
        "dryrun_id": canonical_hash(
            {
                "record": "holler_oracle_shadow_dryrun",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_shadow_dryrun_hash": oracle_shadow_dryrun["canonical_hash"],
            }
        ),
        "dryrun_status": "HOLLER_ORACLE_SHADOW_DRYRUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_shadow_dryrun_hash": oracle_shadow_dryrun["canonical_hash"],
        "oracle_ingest_wiring_hash": oracle_ingest_wiring["canonical_hash"],
        "batch_replay_summary": {
            "fixture_count": fixture_count,
            "expected_operator_holds": fixture_count,
            "live_market_reads": 0,
            "live_signal_writes": 0,
            "brier_score": 0.1,
        },
        "telemetry_hooks": [
            {
                "hook_id": "HOLLER_SHADOW_FIXTURE_COUNT_TELEMETRY",
                "observed_value": fixture_count,
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
            {
                "hook_id": "HOLLER_SHADOW_MARKET_COUNT_TELEMETRY",
                "observed_value": int(holler_batch["market_count"]),
                "valid_for_live_telemetry": False,
                "brier_score": 0.1,
            },
        ],
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "live_signal_ingest": False,
            "marketplace_ingest": False,
            "shadow_replay_execution": False,
            "telemetry_writeback": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
        },
        "advisory_only": True,
        "valid_for_live_ingest": False,
        "valid_for_runtime_execution": False,
        "valid_for_shadow_replay_execution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
