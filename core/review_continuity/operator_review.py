from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class ReviewContinuityReviewPacket(BaseModel):
    schema_version: Literal["ReviewContinuityReviewPacket.v1"] = "ReviewContinuityReviewPacket.v1"
    review_id: str
    continuity_hash: str
    continuity_chains: int
    deferred_sequences: int
    denied_sequences: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(continuity_hash: str, continuity_chains: int, deferred_sequences: int, denied_sequences: int, unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{continuity_hash}|{continuity_chains}|{deferred_sequences}|{denied_sequences}|{unresolved_diagnostics}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_review_hash != self.compute_hash(self.continuity_hash, self.continuity_chains, self.deferred_sequences, self.denied_sequences, self.unresolved_diagnostics):
            raise ValueError("review hash mismatch")
        return self
