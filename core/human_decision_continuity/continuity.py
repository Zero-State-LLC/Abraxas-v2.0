from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityPacket.v1"] = "HumanDecisionContinuityPacket.v1"
    chain_hash: str
    append_only: bool
    deterministic_continuity_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,append_only:bool)->str:
        return hashlib.sha256(f"{chain_hash}|{append_only}".encode()).hexdigest()
