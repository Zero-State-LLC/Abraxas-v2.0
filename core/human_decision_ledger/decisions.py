from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

FORBIDDEN_DECISIONS = {"approved_live", "execute", "deploy", "route_production"}

class HumanDecisionLedgerPacket(BaseModel):
    schema_version: Literal["HumanDecisionLedgerPacket.v1"] = "HumanDecisionLedgerPacket.v1"
    decision_id: str
    bridge_hash: str
    decision_state: str
    deterministic_decision_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, decision_state: str) -> str:
        return hashlib.sha256(f"{bridge_hash}|{decision_state}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "HumanDecisionLedgerPacket":
        self.authority.assert_locked()
        if self.decision_state in FORBIDDEN_DECISIONS:
            raise ValueError("forbidden decision state")
        if self.deterministic_decision_hash != self.compute_hash(self.bridge_hash, self.decision_state):
            raise ValueError("decision hash mismatch")
        return self
