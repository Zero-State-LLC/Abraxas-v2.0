from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

class OverlayReadinessThresholdPacket(BaseModel):
    schema_version: Literal["OverlayReadinessThresholdPacket.v1"] = "OverlayReadinessThresholdPacket.v1"
    threshold_id: str
    blocked_max: float = Field(ge=0, le=1)
    watch_max: float = Field(ge=0, le=1)
    review_ready_min: float = Field(ge=0, le=1)
    stable_candidate_min: float = Field(ge=0, le=1)
    deterministic_threshold_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(blocked_max: float, watch_max: float, review_ready_min: float, stable_candidate_min: float) -> str:
        return hashlib.sha256(f"{blocked_max:.8f}|{watch_max:.8f}|{review_ready_min:.8f}|{stable_candidate_min:.8f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayReadinessThresholdPacket":
        self.authority.assert_locked()
        if not (self.blocked_max <= self.watch_max <= self.review_ready_min <= self.stable_candidate_min):
            raise ValueError("threshold order")
        if self.deterministic_threshold_hash != self.compute_hash(self.blocked_max, self.watch_max, self.review_ready_min, self.stable_candidate_min):
            raise ValueError("threshold hash")
        return self
