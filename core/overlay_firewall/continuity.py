from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority


class OverlayFirewallContinuityPacket(BaseModel):
    schema_version: Literal["OverlayFirewallContinuityPacket.v1"] = (
        "OverlayFirewallContinuityPacket.v1"
    )
    continuity_firewall_id: str
    overlay_hash: str
    continuity_score: float = Field(ge=0, le=1)
    unresolved_events: list[str]
    critical_unresolved_events: list[str]
    continuity_safe: bool
    deterministic_continuity_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        overlay_hash: str,
        score: float,
        unresolved: list[str],
        critical: list[str],
        safe: bool,
    ) -> str:
        return hashlib.sha256(
            f"{overlay_hash}|{score:.8f}|{'|'.join(unresolved)}|{'|'.join(critical)}|{safe}".encode()
        ).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.continuity_safe != (len(self.critical_unresolved_events) == 0):
            raise ValueError("continuity safety invalid")
        if self.deterministic_continuity_hash != self.compute_hash(
            self.overlay_hash,
            self.continuity_score,
            self.unresolved_events,
            self.critical_unresolved_events,
            self.continuity_safe,
        ):
            raise ValueError("continuity hash mismatch")
        return self
