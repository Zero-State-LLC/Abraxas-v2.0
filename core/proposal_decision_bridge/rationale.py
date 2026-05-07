from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalDecisionRationalePacket(BaseModel):
    schema_version: Literal["ProposalDecisionRationalePacket.v1"] = "ProposalDecisionRationalePacket.v1"
    bridge_hash: str
    rationale_summary: str
    cited_restrictions: list[str] = Field(default_factory=list)
    deterministic_rationale_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, rationale_summary: str, cited_restrictions: list[str]) -> str:
        return hashlib.sha256(f"{bridge_hash}|{rationale_summary}|{'/'.join(sorted(cited_restrictions))}".encode()).hexdigest()
