from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalDecisionInputPacket(BaseModel):
    schema_version: Literal["ProposalDecisionInputPacket.v1"] = "ProposalDecisionInputPacket.v1"
    bridge_hash: str
    input_sources: list[str] = Field(default_factory=list)
    unresolved_diagnostics: int
    deterministic_input_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, input_sources: list[str], unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{bridge_hash}|{'/'.join(sorted(input_sources))}|{unresolved_diagnostics}".encode()).hexdigest()
