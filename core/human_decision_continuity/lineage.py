from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityLineagePacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityLineagePacket.v1"] = "HumanDecisionContinuityLineagePacket.v1"
    chain_hash: str
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,lineage_cycle_detected:bool)->str:
        return hashlib.sha256(f"{chain_hash}|{lineage_cycle_detected}".encode()).hexdigest()
