from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

class OverlayCouplingPacket(BaseModel):
    schema_version: Literal['OverlayCouplingPacket.v1'] = 'OverlayCouplingPacket.v1'
    coupling_id: str
    dependency_coupling: float = Field(ge=0, le=1)
    replay_coupling: float = Field(ge=0, le=1)
    risk_coupling: float = Field(ge=0, le=1)
    governance_coupling: float = Field(ge=0, le=1)
    aggregate_coupling_score: float = Field(ge=0, le=1)
    production_route_detected: bool = False
    hidden_dependency_cycle: bool = False
    deterministic_coupling_hash: str
    authority: Authority = Authority()
    status: Literal['passed','failed','not_computable']
    @staticmethod
    def compute_hash(d:float,r:float,k:float,g:float,a:float,pr:bool,h:bool)->str:
        return hashlib.sha256(f"{d:.8f}|{r:.8f}|{k:.8f}|{g:.8f}|{a:.8f}|{pr}|{h}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self)->'OverlayCouplingPacket':
        self.authority.assert_locked()
        if self.deterministic_coupling_hash != self.compute_hash(self.dependency_coupling,self.replay_coupling,self.risk_coupling,self.governance_coupling,self.aggregate_coupling_score,self.production_route_detected,self.hidden_dependency_cycle):
            raise ValueError('coupling hash')
        return self
