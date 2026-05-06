from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class OverlayRollbackPathPacket(BaseModel):
    schema_version: Literal['OverlayRollbackPathPacket.v1'] = 'OverlayRollbackPathPacket.v1'
    rollback_path_id: str
    rollback_path_nodes: list[str]
    rollback_path_depth: int = Field(ge=1)
    rollback_dependency_count: int = Field(ge=0)
    rollback_path_risk: float = Field(ge=0, le=1)
    execution_claimed: bool = False
    status: Literal['passed','failed','not_computable']
