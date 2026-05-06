from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority


class OperatorQueueContinuityPacket(BaseModel):
    schema_version: Literal["OperatorQueueContinuityPacket.v1"] = "OperatorQueueContinuityPacket.v1"
    continuity_id: str
    queue_hash: str
    continuity_score: float = Field(ge=0, le=1)
    unresolved_events: list[str]
    continuity_safe: bool
    deterministic_continuity_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(queue_hash: str, continuity_score: float, unresolved_events: list[str], continuity_safe: bool) -> str:
        return hashlib.sha256(f"{queue_hash}|{continuity_score:.8f}|{'|'.join(unresolved_events)}|{continuity_safe}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.continuity_safe != (len(self.unresolved_events) == 0):
            raise ValueError("continuity mismatch")
        if self.deterministic_continuity_hash != self.compute_hash(self.queue_hash, self.continuity_score, self.unresolved_events, self.continuity_safe):
            raise ValueError("continuity hash mismatch")
        return self
