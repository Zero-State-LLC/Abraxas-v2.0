from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalDecisionContinuityPacket(BaseModel):
    schema_version: Literal["ProposalDecisionContinuityPacket.v1"] = "ProposalDecisionContinuityPacket.v1"
    bridge_hash: str
    prior_hashes: list[str] = Field(default_factory=list)
    append_only: bool
    deterministic_continuity_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, prior_hashes: list[str], append_only: bool) -> str:
        return hashlib.sha256(f"{bridge_hash}|{'/'.join(sorted(prior_hashes))}|{append_only}".encode()).hexdigest()
