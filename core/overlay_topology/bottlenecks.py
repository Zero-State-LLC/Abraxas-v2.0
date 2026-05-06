from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class OverlayBottleneckPacket(BaseModel):
    schema_version: Literal['OverlayBottleneckPacket.v1'] = 'OverlayBottleneckPacket.v1'
    bottleneck_id: str
    high_degree_overlays: list[str]
    rollback_chokepoints: list[str]
    review_chokepoints: list[str]
    propagation_chokepoints: list[str]
    governance_ledger_bottlenecks: list[str]
    bottleneck_count: int = Field(ge=0)
    status: Literal['passed','failed','not_computable']
