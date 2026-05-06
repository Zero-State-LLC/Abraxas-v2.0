from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator


class ReviewContinuityReplayPacket(BaseModel):
    schema_version: Literal["ReviewContinuityReplayPacket.v1"] = "ReviewContinuityReplayPacket.v1"
    replay_id: str
    source_continuity_hash: str
    replay_continuity_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str]
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(source_continuity_hash: str, replay_continuity_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{source_continuity_hash}|{replay_continuity_hash}|{deterministic_match}|{'|'.join(mismatch_reasons)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        should = self.source_continuity_hash == self.replay_continuity_hash and len(self.mismatch_reasons) == 0
        if self.deterministic_match != should:
            raise ValueError("replay mismatch")
        if self.deterministic_replay_hash != self.compute_hash(self.source_continuity_hash, self.replay_continuity_hash, self.deterministic_match, self.mismatch_reasons):
            raise ValueError("replay hash mismatch")
        return self
