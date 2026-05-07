from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED = {"not_authorized", "blocked", "deferred", "authorized_for_manual_execution_review"}
FORBIDDEN = {"executed", "activated", "deployed", "live", "auto_executed", "production_ready"}

class ManualExecutionAuthorizationPacket(BaseModel):
    schema_version: Literal["ManualExecutionAuthorizationPacket.v1"] = "ManualExecutionAuthorizationPacket.v1"
    authorization_id: str
    review_resolution_hash: str
    operator_queue_hash: str
    firewall_hash: str
    readiness_hash: str
    authorization_status: str
    authorization_reason: str
    deterministic_authorization_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str,d:str,e:str,f:str)->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{d}|{e}|{f}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.authorization_status in FORBIDDEN or self.authorization_status not in ALLOWED:
            raise ValueError('forbidden authorization status')
        if self.deterministic_authorization_hash != self.compute_hash(self.review_resolution_hash,self.operator_queue_hash,self.firewall_hash,self.readiness_hash,self.authorization_status,self.authorization_reason):
            raise ValueError('authorization hash')
        return self
