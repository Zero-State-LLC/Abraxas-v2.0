from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OverlayResolutionReplayPacket(BaseModel):
    schema_version: Literal["OverlayResolutionReplayPacket.v1"] = "OverlayResolutionReplayPacket.v1"
    replay_id: str
    source_ledger_hash: str
    replay_ledger_hash: str
    deterministic_match: bool
    mismatched_components: list[str]
    status: Literal["passed", "failed", "not_computable"]
