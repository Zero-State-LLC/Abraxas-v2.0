from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalDecisionReplayPacket(BaseModel):
    schema_version: Literal["ProposalDecisionReplayPacket.v1"] = "ProposalDecisionReplayPacket.v1"
    bridge_hash: str
    replay_bridge_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str] = Field(default_factory=list)
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, replay_bridge_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{bridge_hash}|{replay_bridge_hash}|{deterministic_match}|{'/'.join(sorted(mismatch_reasons))}".encode()).hexdigest()
