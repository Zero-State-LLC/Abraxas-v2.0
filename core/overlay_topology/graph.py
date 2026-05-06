from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

class OverlayTopologyGraphPacket(BaseModel):
    schema_version: Literal['OverlayTopologyGraphPacket.v1'] = 'OverlayTopologyGraphPacket.v1'
    topology_graph_id: str
    overlay_nodes: list[str]
    overlay_edges: list[tuple[str, str]]
    graph_depth: int = Field(ge=1)
    graph_density: float = Field(ge=0, le=1)
    deterministic_graph_hash: str
    authority: Authority = Authority()
    status: Literal['passed','failed','not_computable']

    @staticmethod
    def compute_hash(nodes:list[str], edges:list[tuple[str,str]], depth:int, density:float)->str:
        return hashlib.sha256(f"{sorted(nodes)}|{sorted(edges)}|{depth}|{density:.8f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self)->'OverlayTopologyGraphPacket':
        self.authority.assert_locked()
        if self.deterministic_graph_hash != self.compute_hash(self.overlay_nodes, self.overlay_edges, self.graph_depth, self.graph_density):
            raise ValueError('graph hash')
        return self
