from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class OverlayRiskReplayPacket(BaseModel):
    schema_version: Literal["OverlayRiskReplayPacket.v1"] = "OverlayRiskReplayPacket.v1"
    replay_id: str
    source_risk_hash: str
    replay_risk_hash: str
    deterministic_match: bool
    mismatched_packets: list[str]
    status: Literal["passed", "failed", "not_computable"]
