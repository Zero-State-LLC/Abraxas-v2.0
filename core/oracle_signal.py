from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.oracle_signal_intake_boundary import build_oracle_signal_intake_receipt

SCHEMA_VERSION = "OracleSignalModule.v1"
LANE = "SHADOW"


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_weight": False,
        "ingest_runner_mutation": False,
        "pipeline_or_route_mutation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
    }


def normalize_candidate_signal(candidate: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "schema_version",
        "signal_id",
        "signal_status",
        "payload_ref",
        "source_ref",
        "signal_hash",
    )
    for key in required:
        if key not in candidate:
            raise ValueError(f"missing candidate field: {key}")
    if candidate.get("signal_status") != "CANDIDATE_SHADOW_ONLY":
        raise ValueError("candidate signal must remain shadow-only")
    return {
        "schema_version": str(candidate["schema_version"]),
        "signal_id": str(candidate["signal_id"]),
        "signal_status": str(candidate["signal_status"]),
        "payload_ref": str(candidate["payload_ref"]),
        "source_ref": dict(candidate["source_ref"]),
        "signal_hash": str(candidate["signal_hash"]),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }


def build_oracle_signal_processing_packet(
    *,
    source_root: str = ".",
) -> dict[str, Any]:
    receipt = build_oracle_signal_intake_receipt(source_root=source_root)
    candidates = [
        normalize_candidate_signal(item) for item in receipt.get("candidate_signals", [])
    ]
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "lane": LANE,
        "status": "ORACLE_SIGNAL_PROCESSING_PACKET_EMITTED",
        "candidate_signal_count": len(candidates),
        "candidate_signals": candidates,
        "source_receipt_hash": receipt.get("receipt_hash", "NOT_COMPUTABLE"),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "authority_locks": _authority_locks(),
        "packet_hash": "",
    }
    packet["packet_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "packet_hash"}
    )
    return packet
