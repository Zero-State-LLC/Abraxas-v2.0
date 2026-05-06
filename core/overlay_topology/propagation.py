from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class OverlayPropagationPathPacket(BaseModel):
    schema_version: Literal['OverlayPropagationPathPacket.v1'] = 'OverlayPropagationPathPacket.v1'
    propagation_path_id: str
    propagation_path_nodes: list[str]
    propagation_depth: int = Field(ge=1)
    propagation_score: float = Field(ge=0, le=1)
    blocked_propagation_routes: list[str]
    production_route_included: bool = False
    status: Literal['passed','failed','not_computable']
