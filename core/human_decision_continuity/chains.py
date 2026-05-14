from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
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

    @model_validator(mode="after")
    def _v(self) -> "HumanDecisionChainPacket":
        self.authority.assert_locked()
        if not self.chain_id.strip():
            raise ValueError("chain id required")
        if not self.root_decision_hash.strip():
            raise ValueError("root decision hash required")
        if self.continuity_chain_count <= 0:
            raise ValueError("continuity chain must advance")
        if self.deterministic_chain_hash != self.compute_hash(
            self.root_decision_hash, self.continuity_chain_count
        ):
            raise ValueError("chain hash")
        return self
