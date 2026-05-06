from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryLineageNode(BaseModel):
    overlay_hash: str
    parent_hash: str | None = None
    generation: int
    rollback_hash: str | None = None


class CanaryLineagePacket(BaseModel):
    schema_version: Literal["CanaryLineagePacket.v1"] = "CanaryLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[CanaryLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[CanaryLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.overlay_hash}:{n.parent_hash}:{n.generation}:{n.rollback_hash}" for n in nodes).encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryLineagePacket":
        self.authority.assert_locked()
        seen: set[str] = set()
        for node in self.lineage_nodes:
            if node.overlay_hash in seen or node.parent_hash == node.overlay_hash:
                raise ValueError("cyclic lineage fail closed")
            seen.add(node.overlay_hash)
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("deterministic ordering")
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("lineage hash mismatch")
        return self
