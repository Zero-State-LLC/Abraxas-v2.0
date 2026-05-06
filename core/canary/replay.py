from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.governance.authority import Authority


class CanaryReplayPacket(BaseModel):
    schema_version: Literal["CanaryReplayPacket.v1"] = "CanaryReplayPacket.v1"
    replay_id: str
    overlay_hash: str
    deterministic_match: bool
    replayed_routes: list[str]
    mismatched_routes: list[str]
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
