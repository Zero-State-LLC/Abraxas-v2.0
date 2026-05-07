from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ManualActionCustodyOperatorReviewPacket(BaseModel):
    schema_version: Literal["ManualActionCustodyOperatorReviewPacket.v1"]="ManualActionCustodyOperatorReviewPacket.v1"
    review_id:str
    custody_hash:str
    handoff_count:int
    acknowledgement_count:int
    escalation_required:bool
    unresolved_diagnostics:int
    deterministic_review_hash:str
    authority: Authority=Authority()
    status: Literal["passed","failed","pending","blocked"]
    @staticmethod
    def compute_hash(a:str,b:int,c:int,d:bool,e:int)->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{int(d)}|{e}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_review_hash!=self.compute_hash(self.custody_hash,self.handoff_count,self.acknowledgement_count,self.escalation_required,self.unresolved_diagnostics):
            raise ValueError('review hash')
        return self
