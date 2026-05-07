from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityBlockerPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityBlockerPacket.v1"] = "HumanDecisionContinuityBlockerPacket.v1"
    chain_hash: str
    blocked_chains: int
    deterministic_blocker_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,blocked_chains:int)->str:
        return hashlib.sha256(f"{chain_hash}|{blocked_chains}".encode()).hexdigest()
