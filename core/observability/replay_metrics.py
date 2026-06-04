from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class ReplayTelemetryPacket(BaseModel):
    schema_version: Literal["ReplayTelemetryPacket.v1"] = "ReplayTelemetryPacket.v1"
    replay_telemetry_id: str
    replay_hash: str
    compared_receipts: list[str]
    mismatched_receipts: list[str]
    deterministic_match: bool
    authority: Authority
    status: Literal["valid", "failed", "not_computable"]


def build_replay_telemetry_packet(runtime_run: dict, replay_packet: dict) -> ReplayTelemetryPacket:
    src = runtime_run.get("receipt", {}).get("receipt_id", "")
    deterministic = replay_packet.get("status") == "passed"
    mismatched = [] if deterministic else [src]
    body = {"replay_hash": replay_packet.get("replay_id", ""), "compared_receipts": [src], "mismatched_receipts": mismatched, "deterministic_match": deterministic, "status": "valid" if deterministic else "failed"}
    rid = canonical_hash(body)
    return ReplayTelemetryPacket(replay_telemetry_id=rid, authority=Authority(), **body)
