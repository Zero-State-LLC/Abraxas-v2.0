from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalSandboxReplayPacket(BaseModel):
    schema_version: Literal["ProposalSandboxReplayPacket.v1"] = "ProposalSandboxReplayPacket.v1"
    route_hash: str
    replay_route_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str] = Field(default_factory=list)
    deterministic_replay_hash: str
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, replay_route_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{route_hash}|{replay_route_hash}|{deterministic_match}|{'/'.join(sorted(mismatch_reasons))}".encode()).hexdigest()
