from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator

class ProposalSandboxScorePacket(BaseModel):
    schema_version: Literal["ProposalSandboxScorePacket.v1"] = "ProposalSandboxScorePacket.v1"
    evaluation_hash: str
    evaluation_score: float
    deterministic_score_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(evaluation_hash: str, evaluation_score: float) -> str:
        return hashlib.sha256(f"{evaluation_hash}|{evaluation_score:.6f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "ProposalSandboxScorePacket":
        if not 0.0 <= self.evaluation_score <= 1.0:
            raise ValueError("score out of bounds")
        if self.deterministic_score_hash != self.compute_hash(self.evaluation_hash, self.evaluation_score):
            raise ValueError("score hash mismatch")
        return self
