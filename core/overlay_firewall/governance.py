from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority


class OverlayFirewallGovernancePacket(BaseModel):
    schema_version: Literal["OverlayFirewallGovernancePacket.v1"] = (
        "OverlayFirewallGovernancePacket.v1"
    )
    governance_firewall_id: str
    overlay_hash: str
    governance_continuity_score: float = Field(ge=0, le=1)
    critical_governance_diagnostics: list[str]
    authority_violation_count: int = Field(ge=0)
    governance_safe: bool
    deterministic_governance_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        overlay_hash: str,
        score: float,
        critical: list[str],
        violations: int,
        safe: bool,
    ) -> str:
        return hashlib.sha256(
            f"{overlay_hash}|{score:.8f}|{'|'.join(critical)}|{violations}|{safe}".encode()
        ).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.governance_safe != (
            not self.critical_governance_diagnostics
            and self.authority_violation_count == 0
        ):
            raise ValueError("governance_safe invalid")
        if self.deterministic_governance_hash != self.compute_hash(
            self.overlay_hash,
            self.governance_continuity_score,
            self.critical_governance_diagnostics,
            self.authority_violation_count,
            self.governance_safe,
        ):
            raise ValueError("governance hash mismatch")
        return self
