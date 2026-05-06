from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class OverlayReadinessLineageNode(BaseModel):
    readiness_hash: str
    generation: int

class OverlayReadinessLineagePacket(BaseModel):
    schema_version: Literal["OverlayReadinessLineagePacket.v1"] = "OverlayReadinessLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[OverlayReadinessLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(nodes: list[OverlayReadinessLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.readiness_hash}:{n.generation}" for n in nodes).encode()).hexdigest()
