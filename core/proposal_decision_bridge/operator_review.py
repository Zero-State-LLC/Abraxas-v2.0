from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority

class ProposalDecisionOperatorReviewPacket(BaseModel):
    schema_version: Literal["ProposalDecisionOperatorReviewPacket.v1"] = "ProposalDecisionOperatorReviewPacket.v1"
    review_id: str
    bridge_hash: str
    bridge_count: int
    blocked_bridges: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, bridge_count: int, blocked_bridges: int, unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{bridge_hash}|{bridge_count}|{blocked_bridges}|{unresolved_diagnostics}".encode()).hexdigest()
