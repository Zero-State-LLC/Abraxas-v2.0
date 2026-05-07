from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionInheritancePacket(BaseModel):
    schema_version: Literal["HumanDecisionInheritancePacket.v1"] = "HumanDecisionInheritancePacket.v1"
    chain_hash: str
    inherited_rationale: str
    deterministic_inheritance_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,inherited_rationale:str)->str:
        return hashlib.sha256(f"{chain_hash}|{inherited_rationale}".encode()).hexdigest()
