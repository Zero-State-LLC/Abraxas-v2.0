from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority
class HumanDecisionContinuityOperatorReviewPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityOperatorReviewPacket.v1"] = "HumanDecisionContinuityOperatorReviewPacket.v1"
    review_id: str
    chain_hash: str
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,unresolved_diagnostics:int)->str:
        return hashlib.sha256(f"{chain_hash}|{unresolved_diagnostics}".encode()).hexdigest()
