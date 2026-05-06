from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class IntakeLineageNode(BaseModel):
    intake_hash: str
    parent_hash: str | None = None
    generation: int
    normalization_hash: str | None = None


class IntakeLineagePacket(BaseModel):
    schema_version: Literal["IntakeLineagePacket.v1"] = "IntakeLineagePacket.v1"
    lineage_id: str
    lineage_depth: int
    lineage_nodes: list[IntakeLineageNode]
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(nodes: list[IntakeLineageNode]) -> str:
        material = "|".join(f"{n.intake_hash}:{n.parent_hash}:{n.generation}:{n.normalization_hash}" for n in nodes)
        return hashlib.sha256(material.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "IntakeLineagePacket":
        self.authority.assert_locked()
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("lineage deterministic")
        seen = set()
        valid_hashes = {n.intake_hash for n in self.lineage_nodes}
        for n in self.lineage_nodes:
            if n.intake_hash in seen:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.intake_hash)
            if n.parent_hash and n.parent_hash not in valid_hashes:
                raise ValueError("parent references valid")
        if self.compute_hash(self.lineage_nodes) != self.deterministic_lineage_hash:
            raise ValueError("lineage deterministic")
        return self
