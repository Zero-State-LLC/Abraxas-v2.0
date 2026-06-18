from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.oracle_signal_intake_boundary import build_oracle_signal_intake_receipt

SCHEMA_VERSION = "OracleSignalModule.v1"
LANE = "SHADOW"
AUTHORIZATION_RECORD_PATH = Path(
    "out/operator_review/oracle_signal_physical_implementation_authorization_record_001.latest.json"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _load_physical_implementation_authorization_record(
    source_root: str | Path,
) -> dict[str, Any] | None:
    return _read_json(Path(source_root) / AUTHORIZATION_RECORD_PATH)


def physical_implementation_authorized(source_root: str | Path = ".") -> bool:
    record = _load_physical_implementation_authorization_record(source_root)
    if record is None:
        return False
    return (
        record.get("status") == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_EMITTED"
        and record.get("implementation_authorized") is True
    )


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
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    receipt = build_oracle_signal_intake_receipt(source_root=root)
    auth_record = _load_physical_implementation_authorization_record(root)
    physical_impl_authorized = physical_implementation_authorized(root)
    candidates = [
        normalize_candidate_signal(item) for item in receipt.get("candidate_signals", [])
    ]
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "lane": LANE,
        "status": (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_SHADOW_PROCESSING_PACKET_EMITTED"
            if physical_impl_authorized
            else "ORACLE_SIGNAL_PROCESSING_PACKET_EMITTED"
        ),
        "candidate_signal_count": len(candidates),
        "candidate_signals": candidates,
        "source_receipt_hash": receipt.get("receipt_hash", NOT_COMPUTABLE),
        "physical_implementation_authorized": physical_impl_authorized,
        "source_authorization_record_path": AUTHORIZATION_RECORD_PATH.as_posix(),
        "source_authorization_record_hash": (
            auth_record.get("record_hash", NOT_COMPUTABLE)
            if auth_record is not None
            else NOT_COMPUTABLE
        ),
        "implementation_scope": (
            auth_record.get("implementation_scope", NOT_COMPUTABLE)
            if physical_impl_authorized and auth_record is not None
            else NOT_COMPUTABLE
        ),
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
