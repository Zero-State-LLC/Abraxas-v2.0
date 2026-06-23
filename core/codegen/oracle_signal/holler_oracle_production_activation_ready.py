"""HollerSports Oracle production activation readiness advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Production-ready templates only; no live ingestion or external calls.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_production_activation_ready(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_production_activation_ready: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleProductionActivationReady.v1",
        "activation_id": canonical_hash(
            {
                "record": "holler_oracle_production_activation_ready",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_production_activation_ready_hash": (
                    oracle_production_activation_ready["canonical_hash"]
                ),
            }
        ),
        "activation_status": "HOLLER_ORACLE_PRODUCTION_ACTIVATION_READY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_production_activation_ready_hash": (
            oracle_production_activation_ready["canonical_hash"]
        ),
        "live_batch_pipeline_templates": [
            {
                "pipeline_id": "HOLLERSPORTS_PRODUCTION_MARKET_BATCH_PIPELINE",
                "sport": holler_batch["sport"],
                "pipeline_status": "PRODUCTION_TEMPLATE_READY_NOT_CONNECTED",
                "supports_shadow_dryrun": True,
                "valid_for_live_market_reads": False,
                "brier_score": 0.1,
            },
            {
                "pipeline_id": "HOLLERSPORTS_PRODUCTION_SETTLEMENT_PIPELINE",
                "sport": holler_batch["sport"],
                "pipeline_status": "PRODUCTION_TEMPLATE_READY_NO_OUTCOME_WRITES",
                "supports_shadow_dryrun": True,
                "valid_for_outcome_recording": False,
                "brier_score": 0.1,
            },
        ],
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "actual_external_oracle_calls": False,
            "actual_live_data_ingestion": False,
            "persistent_production_runtime_activation": False,
            "mcp_exposure": False,
            "unreviewed_production_deployment": False,
        },
        "advisory_only": True,
        "valid_for_production_code_generation": True,
        "valid_for_shadow_dryrun_execution": True,
        "valid_for_actual_external_oracle_calls": False,
        "valid_for_actual_live_data_ingestion": False,
        "valid_for_outcome_recording": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
