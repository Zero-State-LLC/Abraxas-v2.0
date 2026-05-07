from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator

class ManualExecutionContinuityPacket(BaseModel):
    schema_version: Literal["ManualExecutionContinuityPacket.v1"] = "ManualExecutionContinuityPacket.v1"
    continuity_id: str
    authorization_hash: str
    inherited_resolution_hash: str
    append_only: bool
    deterministic_continuity_hash: str
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:bool)->str:
        return hashlib.sha256(f"{a}|{b}|{int(c)}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        if self.deterministic_continuity_hash != self.compute_hash(self.authorization_hash,self.inherited_resolution_hash,self.append_only):
            raise ValueError('continuity hash')
        return self
