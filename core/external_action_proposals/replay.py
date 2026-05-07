from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field


class ExternalActionProposalReplayPacket(BaseModel):
    schema_version: Literal["ExternalActionProposalReplayPacket.v1"] = "ExternalActionProposalReplayPacket.v1"
    proposal_hash: str
    replay_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str] = Field(default_factory=list)
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, replay_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        value = f"{proposal_hash}|{replay_hash}|{deterministic_match}|{'/'.join(sorted(mismatch_reasons))}"
        return hashlib.sha256(value.encode()).hexdigest()
