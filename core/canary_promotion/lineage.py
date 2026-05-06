from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryPromotionLineageNode(BaseModel):
    candidate_hash: str
    parent_hash: str | None = None
    generation: int
    diagnostic_hash: str | None = None


class CanaryPromotionLineagePacket(BaseModel):
    schema_version: Literal["CanaryPromotionLineagePacket.v1"] = "CanaryPromotionLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[CanaryPromotionLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[CanaryPromotionLineageNode]) -> str:
        raw = "|".join(f"{n.candidate_hash}:{n.parent_hash}:{n.generation}:{n.diagnostic_hash}" for n in nodes)
        return hashlib.sha256(raw.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryPromotionLineagePacket":
        self.authority.assert_locked()
        seen: set[str] = set()
        for node in self.lineage_nodes:
            if node.candidate_hash in seen or node.parent_hash == node.candidate_hash:
                raise ValueError("cyclic lineage fail closed")
            seen.add(node.candidate_hash)
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("ordering")
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("hash")
        return self
