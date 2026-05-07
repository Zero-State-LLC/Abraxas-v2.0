from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_CUSTODY_STATUS={"custody_recorded","custody_pending","custody_deferred","custody_blocked","custody_invalid"}
FORBIDDEN_CUSTODY_STATUS={"executed","activated","deployed","live","auto_executed","production_ready"}

class ManualActionCustodyPacket(BaseModel):
    schema_version: Literal["ManualActionCustodyPacket.v1"]="ManualActionCustodyPacket.v1"
    custody_id:str
    receipt_hash:str
    authorization_hash:str
    envelope_hash:str
    scope_hash:str
    current_custody_status:str
    custody_reason:str
    deterministic_custody_hash:str
    authority: Authority=Authority()
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(*parts:str)->str:
        return hashlib.sha256("|".join(parts).encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if self.current_custody_status in FORBIDDEN_CUSTODY_STATUS or self.current_custody_status not in ALLOWED_CUSTODY_STATUS:
            raise ValueError('forbidden custody status')
        ex=self.compute_hash(self.receipt_hash,self.authorization_hash,self.envelope_hash,self.scope_hash,self.current_custody_status,self.custody_reason)
        if self.deterministic_custody_hash!=ex:
            raise ValueError('custody hash')
        return self
