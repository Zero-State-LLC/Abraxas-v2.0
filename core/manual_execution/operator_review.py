from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ManualExecutionOperatorReviewPacket(BaseModel):
    schema_version: Literal["ManualExecutionOperatorReviewPacket.v1"] = "ManualExecutionOperatorReviewPacket.v1"
    review_id: str
    envelope_hash: str
    authorization_status: str
    eligible_for_manual_review: bool
    unresolved_diagnostics: int
    forbidden_actions: list[str]
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "pending", "blocked"]
    @staticmethod
    def compute_hash(a:str,b:str,c:bool,d:int,e:list[str])->str:
        return hashlib.sha256(f"{a}|{b}|{int(c)}|{d}|{'|'.join(sorted(e))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_review_hash != self.compute_hash(self.envelope_hash,self.authorization_status,self.eligible_for_manual_review,self.unresolved_diagnostics,self.forbidden_actions):
            raise ValueError('review hash')
        return self
