from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class HumanAcknowledgementPacket(BaseModel):
    schema_version: Literal["HumanAcknowledgementPacket.v1"] = "HumanAcknowledgementPacket.v1"
    acknowledgement_id: str
    operator_id_hash: str
    acknowledgement_scope: str
    acknowledgement_text_hash: str
    acknowledged_constraints: list[str]
    deterministic_acknowledgement_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str,d:list[str])->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{'|'.join(sorted(d))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_acknowledgement_hash != self.compute_hash(self.operator_id_hash,self.acknowledgement_scope,self.acknowledgement_text_hash,self.acknowledged_constraints):
            raise ValueError('ack hash')
        return self
