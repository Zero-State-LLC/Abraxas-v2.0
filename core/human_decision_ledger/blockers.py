from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class HumanDecisionBlockerPacket(BaseModel):
    schema_version: Literal["HumanDecisionBlockerPacket.v1"] = "HumanDecisionBlockerPacket.v1"
    decision_hash: str
    blockers: list[str] = Field(default_factory=list)
    unresolved_blockers: int
    deterministic_blocker_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, blockers: list[str], unresolved_blockers: int) -> str:
        return hashlib.sha256(f"{decision_hash}|{'/'.join(sorted(blockers))}|{unresolved_blockers}".encode()).hexdigest()
