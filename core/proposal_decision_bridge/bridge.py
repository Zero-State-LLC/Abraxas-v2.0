from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ProposalDecisionBridgePacket(BaseModel):
    schema_version: Literal["ProposalDecisionBridgePacket.v1"] = "ProposalDecisionBridgePacket.v1"
    bridge_id: str
    evaluation_hash: str
    decision_readiness: float
    deterministic_bridge_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(evaluation_hash: str, decision_readiness: float) -> str:
        return hashlib.sha256(f"{evaluation_hash}|{decision_readiness:.6f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "ProposalDecisionBridgePacket":
        self.authority.assert_locked()
        if not 0.0 <= self.decision_readiness <= 1.0:
            raise ValueError("readiness bounds")
        if self.deterministic_bridge_hash != self.compute_hash(self.evaluation_hash, self.decision_readiness):
            raise ValueError("bridge hash mismatch")
        return self
