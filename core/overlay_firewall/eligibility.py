from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority


class OverlayFirewallEligibilityPacket(BaseModel):
    schema_version: Literal["OverlayFirewallEligibilityPacket.v1"] = (
        "OverlayFirewallEligibilityPacket.v1"
    )
    eligibility_id: str
    overlay_hash: str
    readiness_score: float = Field(ge=0, le=1)
    rollback_ready: bool
    governance_safe: bool
    containment_safe: bool
    continuity_safe: bool
    replay_valid: bool
    eligible_for_operator_review: bool
    denial_reasons: list[str]
    deterministic_eligibility_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        overlay_hash: str,
        readiness_score: float,
        rollback_ready: bool,
        governance_safe: bool,
        containment_safe: bool,
        continuity_safe: bool,
        replay_valid: bool,
        eligible: bool,
        reasons: list[str],
    ) -> str:
        return hashlib.sha256(
            f"{overlay_hash}|{readiness_score:.8f}|{rollback_ready}|{governance_safe}|{containment_safe}|{continuity_safe}|{replay_valid}|{eligible}|{'|'.join(reasons)}".encode()
        ).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        should = (
            self.rollback_ready
            and self.governance_safe
            and self.containment_safe
            and self.continuity_safe
            and self.replay_valid
            and self.readiness_score >= 0.65
        )
        if self.eligible_for_operator_review != should:
            raise ValueError("eligibility mismatch")
        if (not self.eligible_for_operator_review) and not self.denial_reasons:
            raise ValueError("denial reasons required")
        if self.deterministic_eligibility_hash != self.compute_hash(
            self.overlay_hash,
            self.readiness_score,
            self.rollback_ready,
            self.governance_safe,
            self.containment_safe,
            self.continuity_safe,
            self.replay_valid,
            self.eligible_for_operator_review,
            self.denial_reasons,
        ):
            raise ValueError("eligibility hash mismatch")
        return self
