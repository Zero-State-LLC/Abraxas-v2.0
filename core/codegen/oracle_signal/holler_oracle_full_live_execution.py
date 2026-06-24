"""HollerSports Oracle full live execution readiness helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records full-live HollerSports batch readiness under operator gate.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_full_live_execution(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_full_live_execution: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleFullLiveExecution.v1",
        "execution_id": canonical_hash(
            {
                "record": "holler_oracle_full_live_execution",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_full_live_execution_hash": (
                    oracle_full_live_execution["canonical_hash"]
                ),
            }
        ),
        "execution_status": "HOLLER_ORACLE_FULL_LIVE_EXECUTION_READY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_full_live_execution_hash": (
            oracle_full_live_execution["canonical_hash"]
        ),
        "live_batch_processing": [
            {
                "pipeline_id": "HOLLERSPORTS_LIVE_MARKET_READS",
                "sport": holler_batch["sport"],
                "pipeline_status": "FULL_LIVE_READY_UNDER_OPERATOR_MONITORING",
                "valid_for_live_market_reads": True,
                "valid_for_external_oracle_calls": True,
                "requires_governance_receipt_before_run": True,
                "brier_score": 0.1,
            },
            {
                "pipeline_id": "HOLLERSPORTS_LIVE_BATCH_SETTLEMENT_REVIEW",
                "sport": holler_batch["sport"],
                "pipeline_status": "FULL_LIVE_READY_NO_AUTONOMOUS_OUTCOME_RECORDING",
                "valid_for_live_batch_processing": True,
                "valid_for_outcome_recording": False,
                "requires_operator_review": True,
                "brier_score": 0.1,
            },
        ],
        "authority_locks": {
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
        },
        "valid_for_external_oracle_calls": True,
        "valid_for_live_signal_ingestion": True,
        "valid_for_hollersports_live_batch_processing": True,
        "valid_for_outcome_recording": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
