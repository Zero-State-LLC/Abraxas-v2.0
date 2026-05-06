from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OverlayRiskLineageNode(BaseModel):
    risk_hash: str
    parent_hash: str | None = None
    generation: int = Field(ge=1)


class OverlayRiskLineagePacket(BaseModel):
    schema_version: Literal["OverlayRiskLineagePacket.v1"] = "OverlayRiskLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[OverlayRiskLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[OverlayRiskLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.risk_hash}:{n.parent_hash or '-'}:{n.generation}" for n in sorted(nodes, key=lambda n: (n.generation, n.risk_hash))).encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "OverlayRiskLineagePacket":
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError('depth')
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError('lineage hash')
        for n in self.lineage_nodes:
            if n.parent_hash == n.risk_hash:
                raise ValueError('cycle')
        return self
