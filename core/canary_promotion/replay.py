from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.governance.authority import Authority


class CanaryPromotionReplayPacket(BaseModel):
    schema_version: Literal["CanaryPromotionReplayPacket.v1"] = "CanaryPromotionReplayPacket.v1"
    replay_id: str
    candidate_hash: str
    deterministic_match: bool
    mismatched_packets: list[str]
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
