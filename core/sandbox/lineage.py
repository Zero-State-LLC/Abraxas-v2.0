from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxLineageNode(BaseModel):
    branch_hash: str
    parent_hash: str | None = None
    generation: int
    proposal_hash: str | None = None


class SandboxLineagePacket(BaseModel):
    schema_version: Literal["SandboxLineagePacket.v1"] = "SandboxLineagePacket.v1"
    lineage_id: str
    lineage_depth: int
    lineage_nodes: list[SandboxLineageNode]
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(nodes: list[SandboxLineageNode]) -> str:
        material = "|".join(f"{n.branch_hash}:{n.parent_hash}:{n.generation}:{n.proposal_hash}" for n in nodes)
        return hashlib.sha256(material.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "SandboxLineagePacket":
        self.authority.assert_locked()
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("lineage_depth mismatch")
        if self.compute_hash(self.lineage_nodes) != self.deterministic_lineage_hash:
            raise ValueError("deterministic lineage hash mismatch")
        seen: set[str] = set()
        for node in self.lineage_nodes:
            if node.branch_hash in seen:
                raise ValueError("cyclic lineage fail-closed")
            seen.add(node.branch_hash)
        return self
