from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority

class HumanDecisionOperatorReviewPacket(BaseModel):
    schema_version: Literal["HumanDecisionOperatorReviewPacket.v1"] = "HumanDecisionOperatorReviewPacket.v1"
    review_id: str
    decision_hash: str
    decision_count: int
    deferred_decisions: int
    blocked_decisions: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, decision_count: int, deferred_decisions: int, blocked_decisions: int, unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{decision_hash}|{decision_count}|{deferred_decisions}|{blocked_decisions}|{unresolved_diagnostics}".encode()).hexdigest()
