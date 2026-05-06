from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OverlayTopologyLineageNode(BaseModel):
    graph_hash: str
    parent_hash: str | None = None
    generation: int = Field(ge=1)


class OverlayTopologyLineagePacket(BaseModel):
    schema_version: Literal['OverlayTopologyLineagePacket.v1'] = 'OverlayTopologyLineagePacket.v1'
    lineage_id: str
    lineage_nodes: list[OverlayTopologyLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    status: Literal['passed', 'failed', 'not_computable']

    @staticmethod
    def compute_hash(nodes: list[OverlayTopologyLineageNode]) -> str:
        return hashlib.sha256('|'.join(f"{n.graph_hash}:{n.parent_hash or '-'}:{n.generation}" for n in nodes).encode()).hexdigest()

    @model_validator(mode='after')
    def _v(self) -> 'OverlayTopologyLineagePacket':
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError('depth')
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError('hash')
        return self
