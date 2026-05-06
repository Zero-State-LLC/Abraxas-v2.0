from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator


class OperatorQueueReplayPacket(BaseModel):
    schema_version: Literal["OperatorQueueReplayPacket.v1"] = "OperatorQueueReplayPacket.v1"
    replay_id: str
    source_queue_hash: str
    replay_queue_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str]
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(source_queue_hash: str, replay_queue_hash: str, deterministic_match: bool, mismatch_reasons: list[str]) -> str:
        return hashlib.sha256(f"{source_queue_hash}|{replay_queue_hash}|{deterministic_match}|{'|'.join(mismatch_reasons)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        expected = self.source_queue_hash == self.replay_queue_hash and not self.mismatch_reasons
        if self.deterministic_match != expected:
            raise ValueError("replay match mismatch")
        if self.deterministic_replay_hash != self.compute_hash(self.source_queue_hash, self.replay_queue_hash, self.deterministic_match, self.mismatch_reasons):
            raise ValueError("replay hash mismatch")
        return self
