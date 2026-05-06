from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class OverlayResolutionLineageNode(BaseModel):
    ledger_hash: str
    generation: int

class OverlayResolutionLineagePacket(BaseModel):
    schema_version: Literal["OverlayResolutionLineagePacket.v1"] = "OverlayResolutionLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[OverlayResolutionLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[OverlayResolutionLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.ledger_hash}:{n.generation}" for n in nodes).encode()).hexdigest()
