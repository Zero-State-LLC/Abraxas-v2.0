"""HollerSports full-live runtime preflight helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records HollerSports endpoint readiness without performing live market reads.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_full_live_runtime_preflight(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_full_live_runtime_preflight: Mapping[str, Any],
) -> dict[str, Any]:
    holler_endpoint = next(
        check
        for check in oracle_full_live_runtime_preflight["endpoint_environment_checks"]
        if check["endpoint_env_var"] == "HOLLERSPORTS_BATCH_ENDPOINT_URL"
    )
    ready = holler_endpoint["check_status"] == "ENV_PRESENT_VALUE_REDACTED"
    base: dict[str, Any] = {
        "schema_version": "HollerOracleFullLiveRuntimePreflight.v1",
        "preflight_id": canonical_hash(
            {
                "record": "holler_oracle_full_live_runtime_preflight",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_preflight_hash": (
                    oracle_full_live_runtime_preflight["canonical_hash"]
                ),
            }
        ),
        "preflight_status": (
            "HOLLER_ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
            if ready
            else "HOLLER_ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_BLOCKED_ENV_MISSING"
        ),
        "timestamp": timestamp,
        "holler_batch": dict(holler_intake["holler_batch"]),
        "oracle_full_live_runtime_preflight_hash": (
            oracle_full_live_runtime_preflight["canonical_hash"]
        ),
        "holler_endpoint_check": holler_endpoint,
        "projected_live_batch_controls": [
            {
                "control_id": "HOLLERSPORTS_NO_MARKET_READ_DURING_PREFLIGHT",
                "external_call_made": False,
                "live_market_read_count": 0,
                "blocking": False,
                "brier_score": 0.1,
            },
            {
                "control_id": "HOLLERSPORTS_OPERATOR_MONITORING_REQUIRED",
                "operator_required": True,
                "blocking": not ready,
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
        "valid_for_hollersports_live_batch_processing": ready,
        "valid_for_outcome_recording": False,
        "external_calls_made": 0,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
