from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ReviewResolutionClosurePacket(BaseModel):
    schema_version: Literal["ReviewResolutionClosurePacket.v1"] = "ReviewResolutionClosurePacket.v1"
    closure_id: str
    posture_hash: str
    outcome_hash: str
    unresolved_blocker_count: int
    critical_blocker_count: int
    closure_ready: bool
    deterministic_closure_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(posture_hash: str, outcome_hash: str, unresolved_blocker_count: int, critical_blocker_count: int, closure_ready: bool) -> str:
        return hashlib.sha256(f"{posture_hash}|{outcome_hash}|{unresolved_blocker_count}|{critical_blocker_count}|{int(closure_ready)}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> 'ReviewResolutionClosurePacket':
        self.authority.assert_locked()
        if self.critical_blocker_count > 0 and self.closure_ready:
            raise ValueError('critical blockers prevent closure')
        if self.deterministic_closure_hash != self.compute_hash(self.posture_hash, self.outcome_hash, self.unresolved_blocker_count, self.critical_blocker_count, self.closure_ready):
            raise ValueError('closure hash')
        return self
