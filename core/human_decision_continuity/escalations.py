from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityEscalationPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityEscalationPacket.v1"] = "HumanDecisionContinuityEscalationPacket.v1"
    chain_hash: str
    escalation_state: str
    deterministic_escalation_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,escalation_state:str)->str:
        return hashlib.sha256(f"{chain_hash}|{escalation_state}".encode()).hexdigest()
