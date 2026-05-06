from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OverlayResolutionEventPacket(BaseModel):
    schema_version: Literal["OverlayResolutionEventPacket.v1"] = "OverlayResolutionEventPacket.v1"
    resolution_event_id: str
    overlay_hash: str
    related_review_hash: str
    related_replay_hash: str
    related_diagnostic_hash: str
    resolution_type: Literal["review_completed", "review_denied", "rollback_ready", "rollback_blocked", "containment_acknowledged", "replay_verified", "replay_failed", "diagnostic_closed", "diagnostic_pending"]
    resolution_reason: str
    operator_required: bool
    deterministic_event_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, review_hash: str, replay_hash: str, diag_hash: str, resolution_type: str, reason: str, operator_required: bool) -> str:
        return hashlib.sha256(f"{overlay_hash}|{review_hash}|{replay_hash}|{diag_hash}|{resolution_type}|{reason}|{int(operator_required)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayResolutionEventPacket":
        self.authority.assert_locked()
        if any(s in self.resolution_reason.lower() for s in ["enforce", "auto-resolve", "execute"]):
            raise ValueError("non-advisory")
        if self.deterministic_event_hash != self.compute_hash(self.overlay_hash, self.related_review_hash, self.related_replay_hash, self.related_diagnostic_hash, self.resolution_type, self.resolution_reason, self.operator_required):
            raise ValueError("event hash")
        return self
