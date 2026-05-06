from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class OverlayReadinessReplayPacket(BaseModel):
    schema_version: Literal["OverlayReadinessReplayPacket.v1"] = "OverlayReadinessReplayPacket.v1"
    replay_id: str
    source_readiness_hash: str
    replay_readiness_hash: str
    deterministic_match: bool
    mismatched_components: list[str]
    status: Literal["passed","failed","not_computable"]
