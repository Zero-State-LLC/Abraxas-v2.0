from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class HumanDecisionEscalationPacket(BaseModel):
    schema_version: Literal["HumanDecisionEscalationPacket.v1"] = "HumanDecisionEscalationPacket.v1"
    decision_hash: str
    escalated: bool
    escalation_reason: str
    deterministic_escalation_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, escalated: bool, escalation_reason: str) -> str:
        return hashlib.sha256(f"{decision_hash}|{escalated}|{escalation_reason}".encode()).hexdigest()
