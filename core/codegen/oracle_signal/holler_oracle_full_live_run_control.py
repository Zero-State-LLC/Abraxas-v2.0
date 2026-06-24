"""HollerSports full-live run-control helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records operator-monitored HollerSports live batch run controls only.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_full_live_run_control(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_full_live_run_control: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleFullLiveRunControl.v1",
        "run_control_id": canonical_hash(
            {
                "record": "holler_oracle_full_live_run_control",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_full_live_run_control_hash": (
                    oracle_full_live_run_control["canonical_hash"]
                ),
            }
        ),
        "run_control_status": "HOLLER_ORACLE_FULL_LIVE_RUN_CONTROL_READY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_full_live_run_control_hash": oracle_full_live_run_control[
            "canonical_hash"
        ],
        "run_controls": [
            {
                "control_id": "HOLLERSPORTS_ENDPOINT_RUNTIME_ENV",
                "endpoint_env_var": "HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "valid_for_live_market_reads": True,
                "secret_material_embedded": False,
                "requires_operator_monitoring": True,
                "brier_score": 0.1,
            },
            {
                "control_id": "HOLLERSPORTS_NO_AUTONOMOUS_OUTCOME_RECORDING",
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
