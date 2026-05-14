from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_ESCALATION={"none","operator_review_required","governance_review_required","containment_review_required","rollback_review_required"}
FORBIDDEN_ESCALATION={"auto_execute","auto_deploy","auto_activate"}

class ManualActionEscalationPacket(BaseModel):
    schema_version: Literal["ManualActionEscalationPacket.v1"]="ManualActionEscalationPacket.v1"
    escalation_id:str
    custody_hash:str
    escalation_type:str
    escalation_reason:str
    escalation_required:bool
    deterministic_escalation_hash:str
    authority: Authority=Authority()
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str,d:bool)->str:
        return hashlib.sha256(f"{a}|{b}|{c}|{int(d)}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if not self.custody_hash.strip():
            raise ValueError('custody hash required')
        if not self.escalation_reason.strip():
            raise ValueError('escalation reason required')
        if self.escalation_type in FORBIDDEN_ESCALATION or self.escalation_type not in ALLOWED_ESCALATION:
            raise ValueError('forbidden escalation type')
        if self.escalation_type == "none" and self.escalation_required:
            raise ValueError('invalid escalation transition')
        if self.escalation_type != "none" and not self.escalation_required:
            raise ValueError('invalid escalation transition')
        expected_hash = self.compute_hash(
            self.custody_hash,
            self.escalation_type,
            self.escalation_reason,
            self.escalation_required,
        )
        if self.deterministic_escalation_hash != expected_hash:
            raise ValueError('escalation hash')
        return self
