from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class OperatorOverlayTopologyReviewPacket(BaseModel):
    schema_version: Literal['OperatorOverlayTopologyReviewPacket.v1'] = 'OperatorOverlayTopologyReviewPacket.v1'
    review_id: str
    graph_density: float = Field(ge=0, le=1)
    bottleneck_count: int = Field(ge=0)
    critical_diagnostics: int = Field(ge=0)
    pending_actions: list[str]
    status: Literal['approved','pending','blocked']
