from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OverlayFirewallLineagePacket(BaseModel):
    schema_version: Literal["OverlayFirewallLineagePacket.v1"] = (
        "OverlayFirewallLineagePacket.v1"
    )
    lineage_id: str
    overlay_hash: str
    parent_hashes: list[str]
    lineage_cycle_detected: bool
    status: Literal["passed", "failed", "not_computable"]
