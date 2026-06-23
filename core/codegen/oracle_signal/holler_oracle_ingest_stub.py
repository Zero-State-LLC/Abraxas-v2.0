"""HollerSports Oracle ingest advisory stubs.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live ingest.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_signal_ingest": False,
        "scheduler_mutation": False,
        "queue_mutation": False,
        "pipeline_or_route_mutation": False,
        "github_writeback": False,
        "notion_writeback": False,
        "mcp_tool_exposure_live": False,
    }


def build_shadow_replay_harness_stub(
    *,
    timestamp: str,
    source_packet: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleShadowReplayHarnessStub.v1",
        "stub_id": canonical_hash(
            {
                "record": "oracle_shadow_replay_harness_stub",
                "source_hash": source_packet["canonical_hash"],
            }
        ),
        "stub_status": "SHADOW_REPLAY_HARNESS_STUB_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hash": source_packet["canonical_hash"],
        "replay_mode": "SHADOW_REPLAY_PLAN_ONLY_NOT_EXECUTED",
        "provenance_seal": {
            "source": "core.codegen.oracle_signal",
            "source_packet_hash": source_packet["canonical_hash"],
            "sealed_for_live_ingest": False,
            "brier_score": 0.1,
        },
        "authority_locks": _authority_locks(),
        "valid_for_execution": False,
        "valid_for_live_ingest": False,
        "valid_for_brier_resolution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_holler_oracle_ingest_stub(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    shadow_replay_harness: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "HollerOracleIngestStub.v1",
        "stub_id": canonical_hash(
            {
                "record": "holler_oracle_ingest_stub",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "shadow_replay_hash": shadow_replay_harness["canonical_hash"],
            }
        ),
        "stub_status": "HOLLER_ORACLE_INGEST_STUB_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "holler_intake_hash": holler_intake["canonical_hash"],
        "shadow_replay_harness_hash": shadow_replay_harness["canonical_hash"],
        "ingest_mode": "STUB_ONLY_NO_FETCH_NO_QUEUE_NO_SCHEDULER",
        "provenance_seal": {
            "source": "HollerSports advisory batch pattern",
            "canonical_extension_only": True,
            "live_signal_ingest": False,
            "brier_score": 0.1,
        },
        "authority_locks": _authority_locks(),
        "valid_for_execution": False,
        "valid_for_live_ingest": False,
        "valid_for_queue_mutation": False,
        "valid_for_scheduler_mutation": False,
        "valid_for_brier_resolution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
