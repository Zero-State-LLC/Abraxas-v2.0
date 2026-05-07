from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class HumanDecisionContinuityPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityPacket.v1"] = "HumanDecisionContinuityPacket.v1"
    decision_hash: str
    prior_hashes: list[str] = Field(default_factory=list)
    append_only: bool
    deterministic_continuity_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, prior_hashes: list[str], append_only: bool) -> str:
        return hashlib.sha256(f"{decision_hash}|{'/'.join(sorted(prior_hashes))}|{append_only}".encode()).hexdigest()
