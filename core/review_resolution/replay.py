from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator

class ReviewResolutionReplayPacket(BaseModel):
    schema_version: Literal["ReviewResolutionReplayPacket.v1"] = "ReviewResolutionReplayPacket.v1"
    replay_id: str
    source_resolution_hash: str
    replay_resolution_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str]
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(source_resolution_hash: str, replay_resolution_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{source_resolution_hash}|{replay_resolution_hash}|{int(deterministic_match)}|{'|'.join(sorted(mismatch_reasons))}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> 'ReviewResolutionReplayPacket':
        if self.deterministic_replay_hash != self.compute_hash(self.source_resolution_hash, self.replay_resolution_hash, self.deterministic_match, self.mismatch_reasons):
            raise ValueError('replay hash')
        return self
