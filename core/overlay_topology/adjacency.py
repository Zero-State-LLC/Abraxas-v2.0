from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator

class OverlayAdjacencyPacket(BaseModel):
    schema_version: Literal['OverlayAdjacencyPacket.v1'] = 'OverlayAdjacencyPacket.v1'
    adjacency_id: str
    adjacent_overlays: int = Field(ge=0)
    shared_dependencies: int = Field(ge=0)
    shared_rollback_paths: int = Field(ge=0)
    shared_governance_events: int = Field(ge=0)
    adjacency_score: float = Field(ge=0, le=1)
    deterministic_adjacency_hash: str
    status: Literal['passed','failed','not_computable']
    @staticmethod
    def compute_hash(a:int,b:int,c:int,d:int,s:float)->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{d}|{s:.8f}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self)->'OverlayAdjacencyPacket':
        if self.deterministic_adjacency_hash != self.compute_hash(self.adjacent_overlays,self.shared_dependencies,self.shared_rollback_paths,self.shared_governance_events,self.adjacency_score):
            raise ValueError('adj hash')
        return self
