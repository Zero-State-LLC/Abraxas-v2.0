from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class BrierLineageNode(BaseModel):
    score_hash: str
    parent_hash: str | None = None
    generation: int
    calibration_hash: str | None = None


class BrierLineagePacket(BaseModel):
    schema_version: Literal["BrierLineagePacket.v1"] = "BrierLineagePacket.v1"
    lineage_id: str
    lineage_depth: int
    lineage_nodes: list[BrierLineageNode]
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(nodes: list[BrierLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.score_hash}:{n.parent_hash}:{n.generation}:{n.calibration_hash}" for n in nodes).encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "BrierLineagePacket":
        self.authority.assert_locked()
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("lineage deterministic")
        seen = set()
        for n in self.lineage_nodes:
            if n.score_hash in seen:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.score_hash)
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("lineage deterministic")
        return self
