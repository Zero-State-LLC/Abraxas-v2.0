from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class HumanDecisionReplayPacket(BaseModel):
    schema_version: Literal["HumanDecisionReplayPacket.v1"] = "HumanDecisionReplayPacket.v1"
    decision_hash: str
    replay_decision_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str] = Field(default_factory=list)
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, replay_decision_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{decision_hash}|{replay_decision_hash}|{deterministic_match}|{'/'.join(sorted(mismatch_reasons))}".encode()).hexdigest()
