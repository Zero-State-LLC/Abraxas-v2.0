from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OverlayFirewallReplayPacket(BaseModel):
    schema_version: Literal["OverlayFirewallReplayPacket.v1"] = (
        "OverlayFirewallReplayPacket.v1"
    )
    replay_id: str
    source_firewall_hash: str
    replay_firewall_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str]
    status: Literal["passed", "failed", "not_computable"]
