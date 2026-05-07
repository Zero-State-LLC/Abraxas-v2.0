from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class HumanDecisionDeferralPacket(BaseModel):
    schema_version: Literal["HumanDecisionDeferralPacket.v1"] = "HumanDecisionDeferralPacket.v1"
    decision_hash: str
    deferred: bool
    deferral_reason: str
    deterministic_deferral_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, deferred: bool, deferral_reason: str) -> str:
        return hashlib.sha256(f"{decision_hash}|{deferred}|{deferral_reason}".encode()).hexdigest()
