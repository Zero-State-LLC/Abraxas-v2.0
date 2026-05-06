from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class DriftLineageNode(BaseModel):
    overlay_hash: str
    parent_hash: str | None = None
    generation: int
    calibration_hash: str | None = None


class DriftLineagePacket(BaseModel):
    schema_version: Literal["DriftLineagePacket.v1"] = "DriftLineagePacket.v1"
    lineage_id: str
    lineage_depth: int
    lineage_nodes: list[DriftLineageNode]
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(nodes: list[DriftLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.overlay_hash}:{n.parent_hash}:{n.generation}:{n.calibration_hash}" for n in nodes).encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "DriftLineagePacket":
        self.authority.assert_locked()
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("lineage deterministic")
        seen=set()
        for n in self.lineage_nodes:
            if n.overlay_hash in seen:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.overlay_hash)
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("lineage deterministic")
        return self
