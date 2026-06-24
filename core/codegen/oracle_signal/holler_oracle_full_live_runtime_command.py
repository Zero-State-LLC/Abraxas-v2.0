"""HollerSports full-live runtime command helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records operator-monitored HollerSports live batch runtime commands only.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_full_live_runtime_command(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_full_live_runtime_command: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleFullLiveRuntimeCommand.v1",
        "runtime_command_id": canonical_hash(
            {
                "record": "holler_oracle_full_live_runtime_command",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_full_live_runtime_command_hash": (
                    oracle_full_live_runtime_command["canonical_hash"]
                ),
            }
        ),
        "runtime_command_status": "HOLLER_ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_full_live_runtime_command_hash": (
            oracle_full_live_runtime_command["canonical_hash"]
        ),
        "runtime_command_controls": [
            {
                "control_id": "HOLLERSPORTS_ENDPOINT_ENV_PRESENT",
                "endpoint_env_var": "HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "valid_for_live_market_reads": True,
                "secret_material_embedded": False,
                "requires_operator_monitoring": True,
                "brier_score": 0.1,
            },
            {
                "control_id": "HOLLERSPORTS_RECEIPT_BEFORE_BATCH",
                "valid_for_live_batch_processing": True,
                "valid_for_outcome_recording": False,
                "requires_receipt_before_run": True,
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
            "autonomous_outcome_recording": False,
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
