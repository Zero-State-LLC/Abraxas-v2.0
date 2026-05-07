from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalSandboxEvaluationReplayPacket(BaseModel):
    schema_version: Literal["ProposalSandboxEvaluationReplayPacket.v1"] = "ProposalSandboxEvaluationReplayPacket.v1"
    evaluation_hash: str
    replay_evaluation_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str] = Field(default_factory=list)
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(evaluation_hash: str, replay_evaluation_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{evaluation_hash}|{replay_evaluation_hash}|{deterministic_match}|{'/'.join(sorted(mismatch_reasons))}".encode()).hexdigest()
