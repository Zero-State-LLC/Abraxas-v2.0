from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority

class ProposalSandboxEvaluationOperatorReviewPacket(BaseModel):
    schema_version: Literal["ProposalSandboxEvaluationOperatorReviewPacket.v1"] = "ProposalSandboxEvaluationOperatorReviewPacket.v1"
    review_id: str
    evaluation_hash: str
    evaluation_count: int
    blocked_evaluations: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(evaluation_hash: str, evaluation_count: int, blocked_evaluations: int, unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{evaluation_hash}|{evaluation_count}|{blocked_evaluations}|{unresolved_diagnostics}".encode()).hexdigest()
