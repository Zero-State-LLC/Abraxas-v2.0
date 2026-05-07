from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority
class HumanDecisionChainPacket(BaseModel):
    schema_version: Literal["HumanDecisionChainPacket.v1"] = "HumanDecisionChainPacket.v1"
    chain_id: str
    root_decision_hash: str
    continuity_chain_count: int
    deterministic_chain_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(root_decision_hash:str, continuity_chain_count:int)->str:
        return hashlib.sha256(f"{root_decision_hash}|{continuity_chain_count}".encode()).hexdigest()
