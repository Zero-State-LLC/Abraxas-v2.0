from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ManualExecutionEnvelopePacket(BaseModel):
    schema_version: Literal["ManualExecutionEnvelopePacket.v1"] = "ManualExecutionEnvelopePacket.v1"
    envelope_id: str
    authorization_hash: str
    bounded_scope_hash: str
    acknowledgement_hash: str
    rollback_hash: str
    replay_hash: str
    envelope_status: Literal["blocked", "deferred", "review_ready", "not_computable"]
    unresolved_blockers: list[str]
    deterministic_envelope_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str,d:str,e:str,f:str,g:list[str])->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{d}|{e}|{f}|{'|'.join(sorted(g))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_envelope_hash != self.compute_hash(self.authorization_hash,self.bounded_scope_hash,self.acknowledgement_hash,self.rollback_hash,self.replay_hash,self.envelope_status,self.unresolved_blockers):
            raise ValueError('envelope hash')
        return self
