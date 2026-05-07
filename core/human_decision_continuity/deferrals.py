from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityDeferralPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityDeferralPacket.v1"] = "HumanDecisionContinuityDeferralPacket.v1"
    chain_hash: str
    deferred_chains: int
    deterministic_deferral_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,deferred_chains:int)->str:
        return hashlib.sha256(f"{chain_hash}|{deferred_chains}".encode()).hexdigest()
