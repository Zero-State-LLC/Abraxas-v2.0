from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ManualActionHandoffPacket(BaseModel):
    schema_version: Literal["ManualActionHandoffPacket.v1"]="ManualActionHandoffPacket.v1"
    handoff_id:str
    custody_hash:str
    from_operator_hash:str
    to_operator_hash:str
    handoff_reason:str
    handoff_constraints:list[str]
    deterministic_handoff_hash:str
    authority: Authority=Authority()
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str,d:str,e:list[str])->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{d}|{'|'.join(sorted(e))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        ex=self.compute_hash(self.custody_hash,self.from_operator_hash,self.to_operator_hash,self.handoff_reason,self.handoff_constraints)
        if self.deterministic_handoff_hash!=ex:
            raise ValueError('handoff hash')
        return self
