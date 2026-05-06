from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OverlayGovernanceEventPacket(BaseModel):
    schema_version: Literal["OverlayGovernanceEventPacket.v1"] = "OverlayGovernanceEventPacket.v1"
    event_id: str
    event_type: Literal[
        "overlay_created",
        "overlay_observed",
        "schedule_proposed",
        "schedule_blocked",
        "promotion_reviewed",
        "promotion_denied",
        "rollback_triggered",
        "authority_violation_detected",
        "operator_review_required",
    ]
    source_packet_hash: str
    overlay_hash: str | None = None
    governance_scope: Literal["audit_only", "replay_only", "projection_only"]
    event_generation: int = Field(ge=1)
    deterministic_event_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(event_type: str, source_packet_hash: str, overlay_hash: str | None, governance_scope: str, event_generation: int) -> str:
        return hashlib.sha256(f"{event_type}|{source_packet_hash}|{overlay_hash or '-'}|{governance_scope}|{event_generation}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayGovernanceEventPacket":
        self.authority.assert_locked()
        self.authority
        if self.deterministic_event_hash != self.compute_hash(
            self.event_type,
            self.source_packet_hash,
            self.overlay_hash,
            self.governance_scope,
            self.event_generation,
        ):
            raise ValueError("event hash")
        return self
