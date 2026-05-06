from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OverlayResolutionOutcomePacket(BaseModel):
    schema_version: Literal["OverlayResolutionOutcomePacket.v1"] = "OverlayResolutionOutcomePacket.v1"
    outcome_id: str
    overlay_hash: str
    resolution_status: Literal["pending", "acknowledged", "verified", "blocked", "unresolved"]
    replay_verified: bool
    rollback_ready: bool
    diagnostic_state: str
    operator_review_state: str
    deterministic_outcome_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, resolution_status: str, replay_verified: bool, rollback_ready: bool, diagnostic_state: str, operator_review_state: str) -> str:
        return hashlib.sha256(f"{overlay_hash}|{resolution_status}|{int(replay_verified)}|{int(rollback_ready)}|{diagnostic_state}|{operator_review_state}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayResolutionOutcomePacket":
        self.authority.assert_locked()
        if self.deterministic_outcome_hash != self.compute_hash(self.overlay_hash, self.resolution_status, self.replay_verified, self.rollback_ready, self.diagnostic_state, self.operator_review_state):
            raise ValueError("outcome hash")
        return self
