from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator

class ManualExecutionReplayPacket(BaseModel):
    schema_version: Literal["ManualExecutionReplayPacket.v1"] = "ManualExecutionReplayPacket.v1"
    replay_id: str
    source_hash: str
    replay_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str]
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:bool,d:list[str])->str:
        return hashlib.sha256(f"{a}|{b}|{int(c)}|{'|'.join(sorted(d))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        if self.deterministic_replay_hash != self.compute_hash(self.source_hash,self.replay_hash,self.deterministic_match,self.mismatch_reasons):
            raise ValueError('replay hash')
        return self
