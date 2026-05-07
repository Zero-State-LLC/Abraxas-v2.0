from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ManualExecutionEligibilityPacket(BaseModel):
    schema_version: Literal["ManualExecutionEligibilityPacket.v1"] = "ManualExecutionEligibilityPacket.v1"
    eligibility_id: str
    authorization_hash: str
    closure_ready: bool
    rollback_ready: bool
    replay_verified: bool
    acknowledgement_required: bool
    critical_blockers: int
    eligible_for_manual_review: bool
    denial_reasons: list[str]
    deterministic_eligibility_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:bool,c:bool,d:bool,e:bool,f:int,g:bool,h:list[str])->str:
        return hashlib.sha256(f"{a}|{int(b)}|{int(c)}|{int(d)}|{int(e)}|{f}|{int(g)}|{'|'.join(sorted(h))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        should = self.closure_ready and self.rollback_ready and self.replay_verified and self.critical_blockers==0 and not self.acknowledgement_required
        if self.eligible_for_manual_review != should:
            raise ValueError('eligibility mismatch')
        if self.deterministic_eligibility_hash != self.compute_hash(self.authorization_hash,self.closure_ready,self.rollback_ready,self.replay_verified,self.acknowledgement_required,self.critical_blockers,self.eligible_for_manual_review,self.denial_reasons):
            raise ValueError('eligibility hash')
        return self
