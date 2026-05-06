from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OverlayContainmentReplayPacket(BaseModel):
    schema_version: Literal["OverlayContainmentReplayPacket.v1"] = "OverlayContainmentReplayPacket.v1"
    replay_id: str
    source_policy_hash: str
    replay_policy_hash: str
    deterministic_match: bool
    mismatched_components: list[str]
    status: Literal["passed", "failed", "not_computable"]
