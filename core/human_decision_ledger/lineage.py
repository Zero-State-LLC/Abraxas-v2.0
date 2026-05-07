from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class HumanDecisionLineagePacket(BaseModel):
    schema_version: Literal["HumanDecisionLineagePacket.v1"] = "HumanDecisionLineagePacket.v1"
    decision_hash: str
    parent_hashes: list[str] = Field(default_factory=list)
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, parent_hashes: list[str], lineage_cycle_detected: bool) -> str:
        return hashlib.sha256(f"{decision_hash}|{'/'.join(sorted(parent_hashes))}|{lineage_cycle_detected}".encode()).hexdigest()
