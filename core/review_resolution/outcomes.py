from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ReviewResolutionOutcomePacket(BaseModel):
    schema_version: Literal["ReviewResolutionOutcomePacket.v1"] = "ReviewResolutionOutcomePacket.v1"
    outcome_id: str
    posture_hash: str
    outcome_state: Literal["unresolved", "denied", "deferred", "review_only_complete", "blocked"]
    outcome_reason: str
    closure_ready: bool
    deterministic_outcome_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(posture_hash: str, outcome_state: str, outcome_reason: str, closure_ready: bool) -> str:
        return hashlib.sha256(f"{posture_hash}|{outcome_state}|{outcome_reason}|{int(closure_ready)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ReviewResolutionOutcomePacket":
        self.authority.assert_locked()
        if self.deterministic_outcome_hash != self.compute_hash(self.posture_hash, self.outcome_state, self.outcome_reason, self.closure_ready):
            raise ValueError("outcome hash")
        return self
