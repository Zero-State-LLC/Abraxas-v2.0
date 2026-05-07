from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityReplayPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityReplayPacket.v1"] = "HumanDecisionContinuityReplayPacket.v1"
    chain_hash: str
    replay_chain_hash: str
    deterministic_match: bool
    deterministic_replay_hash: str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(chain_hash:str,replay_chain_hash:str,deterministic_match:bool)->str:
        return hashlib.sha256(f"{chain_hash}|{replay_chain_hash}|{deterministic_match}".encode()).hexdigest()
