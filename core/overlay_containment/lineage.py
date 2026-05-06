from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class OverlayContainmentLineageNode(BaseModel):
    policy_hash: str
    generation: int

class OverlayContainmentLineagePacket(BaseModel):
    schema_version: Literal["OverlayContainmentLineagePacket.v1"] = "OverlayContainmentLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[OverlayContainmentLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[OverlayContainmentLineageNode]) -> str:
        payload = "|".join(f"{n.policy_hash}:{n.generation}" for n in nodes)
        return hashlib.sha256(payload.encode()).hexdigest()
