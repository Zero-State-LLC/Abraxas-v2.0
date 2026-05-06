from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OverlayObservabilityLineageNode(BaseModel):
    fusion_hash: str
    parent_hash: str | None = None
    generation: int
    diagnostic_hash: str | None = None


class OverlayObservabilityLineagePacket(BaseModel):
    schema_version: Literal["OverlayObservabilityLineagePacket.v1"] = "OverlayObservabilityLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[OverlayObservabilityLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[OverlayObservabilityLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.fusion_hash}:{n.parent_hash}:{n.generation}:{n.diagnostic_hash}" for n in nodes).encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "OverlayObservabilityLineagePacket":
        self.authority.assert_locked()
        seen: set[str] = set()
        for n in self.lineage_nodes:
            if n.fusion_hash in seen or n.parent_hash == n.fusion_hash:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.fusion_hash)
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("deterministic ordering")
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("deterministic ordering")
        return self
