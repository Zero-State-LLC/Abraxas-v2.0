from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ManualActionCustodyAcknowledgementPacket(BaseModel):
    schema_version: Literal["ManualActionCustodyAcknowledgementPacket.v1"]="ManualActionCustodyAcknowledgementPacket.v1"
    custody_acknowledgement_id:str
    custody_hash:str
    operator_id_hash:str
    acknowledged_constraints:list[str]
    acknowledgement_scope:str
    deterministic_acknowledgement_hash:str
    authority: Authority=Authority()
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:list[str],d:str)->str:
        return hashlib.sha256(f"{a}|{b}|{'|'.join(sorted(c))}|{d}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_acknowledgement_hash!=self.compute_hash(self.custody_hash,self.operator_id_hash,self.acknowledged_constraints,self.acknowledgement_scope):
            raise ValueError('ack hash')
        return self
