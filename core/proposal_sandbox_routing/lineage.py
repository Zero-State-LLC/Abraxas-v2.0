from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalSandboxLineagePacket(BaseModel):
    schema_version: Literal["ProposalSandboxLineagePacket.v1"] = "ProposalSandboxLineagePacket.v1"
    route_hash: str
    parent_hashes: list[str] = Field(default_factory=list)
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, parent_hashes: list[str], lineage_cycle_detected: bool) -> str:
        return hashlib.sha256(f"{route_hash}|{'/'.join(sorted(parent_hashes))}|{lineage_cycle_detected}".encode()).hexdigest()
