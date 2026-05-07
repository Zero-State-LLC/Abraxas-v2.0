from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalDecisionLineagePacket(BaseModel):
    schema_version: Literal["ProposalDecisionLineagePacket.v1"] = "ProposalDecisionLineagePacket.v1"
    bridge_hash: str
    parent_hashes: list[str] = Field(default_factory=list)
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, parent_hashes: list[str], lineage_cycle_detected: bool) -> str:
        return hashlib.sha256(f"{bridge_hash}|{'/'.join(sorted(parent_hashes))}|{lineage_cycle_detected}".encode()).hexdigest()
