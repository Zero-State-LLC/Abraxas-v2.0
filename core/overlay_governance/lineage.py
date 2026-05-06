from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OverlayGovernanceLineageNode(BaseModel):
    ledger_hash: str
    parent_hash: str | None = None
    generation: int = Field(ge=1)
    continuity_hash: str | None = None


class OverlayGovernanceLineagePacket(BaseModel):
    schema_version: Literal["OverlayGovernanceLineagePacket.v1"] = "OverlayGovernanceLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[OverlayGovernanceLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[OverlayGovernanceLineageNode]) -> str:
        ordered = sorted(nodes, key=lambda n: (n.generation, n.ledger_hash))
        return hashlib.sha256("|".join(f"{n.ledger_hash}:{n.parent_hash or '-'}:{n.generation}:{n.continuity_hash or '-'}" for n in ordered).encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayGovernanceLineagePacket":
        self.authority.assert_locked()
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("depth")
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("hash")
        for node in self.lineage_nodes:
            if node.parent_hash == node.ledger_hash:
                raise ValueError("cyclic lineage")
        return self
